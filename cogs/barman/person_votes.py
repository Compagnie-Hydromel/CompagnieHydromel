import datetime
import re
import textwrap
import traceback
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from libs.databases.models.guild_user import GuildUser
from libs.databases.models.person_vote import PersonVote
from libs.exception.handler import Handler


def parse_expiry(value):
    try:
        date = datetime.datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            "Date attendue : AAAA-MM-JJ HH:MM (heure de Paris), ou date ISO avec fuseau.") from error
    if date.tzinfo is None:
        date = date.replace(tzinfo=ZoneInfo("Europe/Paris"))
    return int(date.timestamp())


def poll_embed(poll):
    status = "Terminé" if poll.is_expired else "Ouvert"
    candidates = poll.candidate_ids
    embed = discord.Embed(title=poll.title, color=0xADFF2F)
    embed.description = (
        f"**{status}** · Clôture : <t:{poll.expires_at}:F>\n"
        f"Votes par membre : **{poll.votes_per_member}**\n"
        f"Vote anonyme : **{'oui' if poll.anonymous else 'non'}**\n"
        f"Plusieurs votes sur le même candidat : **{'oui' if poll.allow_multiple else 'non'}**\n\n"
        + "\n".join(f"• <@{candidate}>" for candidate in candidates[:25]))
    if len(candidates) > 25:
        embed.description += f"\n… et {len(candidates) - 25} autres personnes. **{len(candidates)} candidats** au total."
    if poll.is_expired:
        totals, _ = poll.results()
        ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
        embed.add_field(name="Résultats", value="\n".join(
            f"<@{candidate}> : **{total}**" for candidate, total in ranked[:20]), inline=False)
        if len(ranked) > 20:
            embed.add_field(name="Résultats complets",
                            value="Utilisez /vote_resultats pour consulter tous les candidats.", inline=False)
    embed.set_footer(
        text=f"Scrutin n°{poll.id} · /vote_resultats pour consulter les résultats")
    return embed


class VoteQuantityModal(discord.ui.Modal):
    def __init__(self, poll_id, candidate_id):
        super().__init__(title="Attribuer des votes")
        self.poll_id = poll_id
        self.candidate_id = candidate_id
        self.quantity = discord.ui.InputText(
            label="Nombre de votes", value="1", max_length=3)
        self.add_item(self.quantity)

    async def callback(self, interaction):
        try:
            quantity = int(self.quantity.value)
        except ValueError:
            await interaction.response.send_message("Indiquez un nombre entier de votes.", ephemeral=True)
            return
        poll = PersonVote.find(self.poll_id)
        if poll is None or interaction.user.bot:
            await interaction.response.send_message("Scrutin introuvable ou vote non autorisé.", ephemeral=True)
            return
        try:
            # No await between reading the ballot and saving it: concurrent
            # interactions on this bot cannot consume the same remaining votes.
            remaining = poll.cast(interaction.user.id, interaction.guild_id,
                                  self.candidate_id, quantity)
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return
        await interaction.response.send_message(
            f"Vote enregistré. Il vous reste {remaining} vote(s). Cliquez à nouveau sur « Voter » pour continuer.",
            ephemeral=True)


class CandidateSelect(discord.ui.Select):
    def __init__(self, poll, guild):
        self.poll_id = poll.id
        options = []
        for candidate in poll.candidate_ids:
            member = guild.get_member(int(candidate))
            label = f"{member.display_name} ({candidate})" if member else candidate
            options.append(discord.SelectOption(
                label=label[:100], value=candidate))
        super().__init__(placeholder="Choisissez une personne", options=options)

    async def callback(self, interaction):
        await interaction.response.send_modal(VoteQuantityModal(self.poll_id, self.values[0]))


class CandidateUserSelect(discord.ui.Select):
    def __init__(self, poll):
        self.poll_id = poll.id
        super().__init__(select_type=discord.ComponentType.user_select,
                         placeholder="Recherchez une personne candidate du serveur")

    async def callback(self, interaction):
        poll = PersonVote.find(self.poll_id)
        candidate_id = str(self.values[0].id)
        if poll is None or candidate_id not in poll.candidate_ids:
            await interaction.response.send_message(
                "Cette personne n'est pas candidate. Les bots et les membres arrivés après le lancement sont exclus.",
                ephemeral=True)
            return
        await interaction.response.send_modal(VoteQuantityModal(self.poll_id, candidate_id))


class PollView(discord.ui.View):
    def __init__(self, poll_id, disabled=False):
        super().__init__(timeout=None)
        self.poll_id = poll_id
        button = discord.ui.Button(label="Voter", style=discord.ButtonStyle.primary,
                                   custom_id=f"person_vote:{poll_id}", disabled=disabled)
        button.callback = self.vote
        self.add_item(button)

    async def vote(self, interaction):
        poll = PersonVote.find(self.poll_id)
        if (poll is None or poll.is_expired or interaction.user.bot or
                str(interaction.guild_id) != poll.guild_discord_id):
            await interaction.response.send_message("Ce scrutin est terminé ou indisponible.", ephemeral=True)
            return
        view = discord.ui.View(timeout=300)
        if len(poll.candidate_ids) > 25:
            view.add_item(CandidateUserSelect(poll))
        else:
            view.add_item(CandidateSelect(poll, interaction.guild))
        await interaction.response.send_message(
            "Choisissez un candidat, puis le nombre de votes à lui attribuer. Les votes enregistrés sont définitifs.",
            view=view, ephemeral=True)


class PersonVotes(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.registered = False
        self.close_expired.start()

    def cog_unload(self):
        self.close_expired.cancel()

    @discord.Cog.listener()
    async def on_ready(self):
        if not self.registered:
            for poll in PersonVote.where(closed=False):
                if poll.message_id:
                    self.bot.add_view(PollView(poll.id),
                                      message_id=int(poll.message_id))
            self.registered = True

    @tasks.loop(seconds=30)
    async def close_expired(self):
        for poll in PersonVote.where(closed=False):
            if not poll.is_expired or not poll.message_id:
                continue
            try:
                channel = self.bot.get_channel(int(poll.channel_id)) or await self.bot.fetch_channel(int(poll.channel_id))
                message = await channel.fetch_message(int(poll.message_id))
                await message.edit(embed=poll_embed(poll), view=PollView(poll.id, disabled=True))
            except discord.NotFound:
                pass
            except Exception as error:
                Handler().response_handler(error, traceback.format_exc())
                continue
            poll.closed = True
            poll.saveOrFail()

    @close_expired.before_loop
    async def before_close_expired(self):
        await self.bot.wait_until_ready()

    @discord.slash_command(description="Créer un vote de personnes (administration)")
    @discord.option("titre", description="Titre du scrutin")
    @discord.option("candidats", description="« serveur » pour tous les membres hors bots, ou mentions/identifiants séparés par des espaces")
    @discord.option("fin", description="Clôture : AAAA-MM-JJ HH:MM (Paris), ou date ISO avec fuseau")
    @discord.option("votes", description="Nombre de votes par membre (1 à 100)", min_value=1, max_value=100)
    @discord.option("anonyme", description="Masquer l'identité des votants")
    @discord.option("cumul", description="Autoriser plusieurs votes sur un même candidat")
    async def vote_creer(self, ctx, titre: str, candidats: str, fin: str,
                         votes: int = 1, anonyme: bool = True, cumul: bool = False):
        if ctx.guild is None:
            await ctx.respond("Cette commande s'utilise dans un serveur.", ephemeral=True)
            return
        admin = GuildUser.from_user_discord_id_and_guild_discord_id(
            str(ctx.author.id), str(ctx.guild.id))
        if not admin.is_admin:
            await ctx.respond("Seul un administrateur peut lancer un vote.", ephemeral=True)
            return
        await ctx.defer(ephemeral=True)
        try:
            if candidats.strip().casefold() == "serveur":
                # Fetch the full membership, not just the locally cached users.
                ids = [str(member.id) async for member in ctx.guild.fetch_members(limit=None)
                       if not member.bot]
            else:
                tokens = candidats.replace(",", " ").split()
                ids = []
                for token in tokens:
                    match = re.fullmatch(r"(?:<@!?(\d+)>|(\d+))", token)
                    if not match:
                        raise ValueError(
                            "Utilisez « serveur », ou des mentions/identifiants de membres.")
                    ids.append(str(int(match.group(1) or match.group(2))))
                if len(ids) < 2 or len(set(ids)) != len(ids):
                    raise ValueError(
                        "Choisissez au moins 2 personnes différentes.")
                for candidate in ids:
                    member = ctx.guild.get_member(int(candidate))
                    if member is None:
                        try:
                            member = await ctx.guild.fetch_member(int(candidate))
                        except discord.NotFound as error:
                            raise ValueError(
                                "Chaque candidat doit être membre de ce serveur.") from error
                    if member.bot:
                        raise ValueError(
                            "Les bots ne peuvent pas être candidats.")
            poll = PersonVote.launch(
                guild_id=ctx.guild.id, channel_id=ctx.channel.id, title=titre,
                candidates=ids, votes_per_member=votes, expires_at=parse_expiry(
                    fin),
                anonymous=anonyme, allow_multiple=cumul)
            try:
                message = await ctx.channel.send(embed=poll_embed(poll), view=PollView(poll.id),
                                                 allowed_mentions=discord.AllowedMentions.none())
            except Exception:
                poll.delete()
                raise
            poll.message_id = str(message.id)
            poll.saveOrFail()
        except ValueError as error:
            await ctx.respond(str(error), ephemeral=True)
            return
        await ctx.respond(f"Scrutin créé : {message.jump_url}", ephemeral=True)

    @discord.slash_command(description="Consulter les résultats d'un vote de personnes")
    @discord.option("scrutin", description="Numéro du scrutin indiqué sous son message", min_value=1)
    async def vote_resultats(self, ctx, scrutin: int):
        poll = PersonVote.find(scrutin)
        if ctx.guild is None or poll is None or str(ctx.guild.id) != poll.guild_discord_id:
            await ctx.respond("Scrutin introuvable sur ce serveur.", ephemeral=True)
            return
        channel = ctx.guild.get_channel_or_thread(int(poll.channel_id))
        if channel is None or not channel.permissions_for(ctx.author).view_channel:
            await ctx.respond("Vous n'avez pas accès au salon de ce scrutin.", ephemeral=True)
            return
        totals, details = poll.results()
        lines = [
            f"**{discord.utils.escape_markdown(poll.title)}** — {'terminé' if poll.is_expired else 'en cours'}"]
        lines.extend(
            f"<@{candidate}> : {total} vote(s)" for candidate, total in totals.items())
        if poll.anonymous:
            lines.append(
                "Scrutin anonyme : aucune identité de votant n'est affichée.")
        else:
            lines.append("**Votes nominatifs**")
            for voter, allocations in details:
                lines.append(f"<@{voter}> → " + ", ".join(
                    f"<@{candidate}> × {quantity}" for candidate, quantity in allocations.items()))
        await ctx.defer(ephemeral=True)
        page = ""
        for line in (part for line in lines for part in textwrap.wrap(line, width=1800)):
            if len(page) + len(line) + 1 > 1900:
                await ctx.respond(page, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())
                page = ""
            page += line + "\n"
        if page:
            await ctx.respond(page, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())


def setup(bot):
    bot.add_cog(PersonVotes(bot))
