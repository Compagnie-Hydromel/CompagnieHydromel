import asyncio
import importlib
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

from MIWOS.config import DBConfig
from MIWOS.db import migrate
from MIWOS.libs.sql.select import executor_select

from cogs.barman.person_votes import (
    CandidateUserSelect, PersonVotes, PollView, VoteQuantityModal, parse_expiry, poll_embed,
)
from libs.databases.bootstrap import load_all_models
from libs.databases.models.person_ballot import PersonBallot
from libs.databases.models.person_vote import PersonVote


class VoteDatabase:
    def setup_database(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        config = patch.dict(DBConfig._config, db_connector="sqlite",
                            db_database=str(Path(directory.name) / "votes.sqlite3"),
                            db_migration_dir="libs/databases/migrations", sql_log_file="")
        config.start()
        self.addCleanup(config.stop)
        self.executor = executor_select()
        self.addCleanup(self.executor.close)
        load_all_models()
        migrate()

    def launch(self, **changes):
        values = dict(guild_id="10", channel_id="20", title="Élection",
                      candidates=["100", "200", "300"], votes_per_member=3,
                      expires_at=4102444800, anonymous=True, allow_multiple=False)
        return PersonVote.launch(**{**values, **changes})


class TestPersonVotes(VoteDatabase, unittest.TestCase):
    def setUp(self):
        self.setup_database()

    def test_independent_member_quotas_and_no_duplicate_candidate(self):
        poll = self.launch()
        self.assertEqual(poll.cast(50, 10, "100"), 2)
        with self.assertRaisesRegex(ValueError, "seul vote"):
            poll.cast(50, 10, "100")
        self.assertEqual(poll.cast(50, 10, "200"), 1)
        self.assertEqual(poll.cast(50, 10, "300"), 0)
        self.assertEqual(poll.cast(60, 10, "100"), 2)
        self.assertEqual(poll.results(), ({"100": 2, "200": 1, "300": 1}, []))

    def test_cumulative_votes_cannot_exceed_quota_even_after_reload(self):
        poll = self.launch(allow_multiple=True)
        self.assertEqual(poll.cast(50, 10, "100", 2), 1)
        poll = PersonVote.find(poll.id)
        with self.assertRaisesRegex(ValueError, "reste 1"):
            poll.cast(50, 10, "200", 2)
        self.assertEqual(poll.cast(50, 10, "100"), 0)
        with self.assertRaisesRegex(ValueError, "reste 0"):
            poll.cast(50, 10, "200")
        self.assertEqual(poll.results()[0], {"100": 3, "200": 0, "300": 0})
        self.assertEqual(len(PersonBallot.all()), 1)

    def test_anonymous_ballots_hide_identity_and_are_scoped_to_poll(self):
        poll = self.launch()
        other = self.launch()
        poll.cast(123456789, 10, "100")
        ballot = PersonBallot.whereFirst(personvote_id=poll.id)
        self.assertNotIn("123456789", ballot.voter_key)
        self.assertNotEqual(poll.voter_key(123456789), other.voter_key(123456789))
        self.assertEqual(poll.results()[1], [])
        self.assertEqual(other.cast(123456789, 10, "100"), 2)

    def test_non_anonymous_results_include_voters_and_allocations(self):
        poll = self.launch(anonymous=False, allow_multiple=True)
        poll.cast(50, 10, "100", 2)
        self.assertEqual(poll.results()[1], [("50", {"100": 2})])

    def test_rejects_wrong_guild_unknown_candidate_and_invalid_quantities(self):
        poll = self.launch()
        for guild, candidate, quantity in ((11, "100", 1), (10, "404", 1),
                                            (10, "100", 0), (10, "100", -1),
                                            (10, "100", 1.5), (10, "100", 2)):
            with self.subTest(values=(guild, candidate, quantity)), self.assertRaises(ValueError):
                poll.cast(50, guild, candidate, quantity)
        self.assertEqual(len(PersonBallot.all()), 0)

    def test_deadline_enforced_without_waiting_for_background_closure(self):
        poll = self.launch()
        with patch("libs.databases.models.person_vote.time.time", return_value=poll.expires_at):
            with self.assertRaisesRegex(ValueError, "terminé"):
                poll.cast(50, 10, "100")
            self.assertIn("Terminé", poll_embed(poll).description)
        poll.closed = True
        with self.assertRaisesRegex(ValueError, "terminé"):
            poll.cast(50, 10, "100")

    def test_invalid_configuration_is_not_persisted(self):
        for changes in ({"title": " "}, {"title": "x" * 201}, {"candidates": ["100"]},
                        {"candidates": ["100", "100"]}, {"votes_per_member": 0},
                        {"votes_per_member": 101}, {"votes_per_member": 4}, {"expires_at": 1}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.launch(**changes)
        self.assertEqual(len(PersonVote.all()), 0)

    def test_migration_rolls_back_and_reapplies(self):
        migration = importlib.import_module(
            "libs.databases.migrations.20261030000000_create_person_votes").CreatePersonVotes()
        migration.rollback()
        migration.migrate()
        self.launch().cast(50, 10, "100")
        self.assertEqual(len(PersonBallot.all()), 1)

    def test_dates_are_parsed_in_paris_or_explicit_timezone(self):
        self.assertEqual(parse_expiry("2030-01-01 12:00"),
                         parse_expiry("2030-01-01T11:00:00+00:00"))
        self.assertEqual(parse_expiry("2030-07-01 12:00"),
                         parse_expiry("2030-07-01T10:00:00Z"))
        with self.assertRaises(ValueError):
            parse_expiry("demain")


class TestPersonVoteInteractions(VoteDatabase, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.setup_database()

    def interaction(self):
        return SimpleNamespace(user=SimpleNamespace(id=50, bot=False), guild_id=10,
                               response=SimpleNamespace(send_message=AsyncMock()))

    async def test_modal_records_votes_and_rejects_double_submission(self):
        poll = self.launch(votes_per_member=1)
        modal = VoteQuantityModal(poll.id, "100")
        modal.quantity._value = "1"
        first, second = self.interaction(), self.interaction()
        await asyncio.gather(modal.callback(first), modal.callback(second))
        self.assertEqual(poll.results()[0]["100"], 1)
        self.assertIn("enregistré", first.response.send_message.call_args.args[0])
        self.assertIn("seul vote", second.response.send_message.call_args.args[0])
        self.assertTrue(first.response.send_message.call_args.kwargs["ephemeral"])

    async def test_open_modal_cannot_vote_after_deadline(self):
        poll = self.launch()
        modal = VoteQuantityModal(poll.id, "100")
        modal.quantity._value = "1"
        interaction = self.interaction()
        with patch("libs.databases.models.person_vote.time.time", return_value=poll.expires_at):
            await modal.callback(interaction)
        self.assertIn("terminé", interaction.response.send_message.call_args.args[0])
        self.assertEqual(len(PersonBallot.all()), 0)

    async def test_persistent_button_survives_restart_and_expiry_disables_it(self):
        poll = self.launch()
        poll.message_id = "30"
        poll.saveOrFail()
        bot = Mock(wait_until_ready=AsyncMock())
        message = SimpleNamespace(edit=AsyncMock())
        bot.get_channel.return_value = SimpleNamespace(fetch_message=AsyncMock(return_value=message))
        with patch.object(PersonVotes.close_expired, "start"):
            cog = PersonVotes(bot)
        await cog.on_ready()
        await cog.on_ready()
        bot.add_view.assert_called_once()
        self.assertTrue(bot.add_view.call_args.args[0].is_persistent())
        self.assertEqual(bot.add_view.call_args.kwargs["message_id"], 30)
        with patch("libs.databases.models.person_vote.time.time", return_value=poll.expires_at):
            await PersonVotes.close_expired.coro(cog)
        self.assertTrue(PersonVote.find(poll.id).closed)
        self.assertTrue(message.edit.call_args.kwargs["view"].children[0].disabled)

    async def test_only_admins_can_create_polls_and_dm_is_rejected(self):
        cog = object.__new__(PersonVotes)
        ctx = SimpleNamespace(guild=SimpleNamespace(id=10), author=SimpleNamespace(id=50), respond=AsyncMock())
        with patch("cogs.barman.person_votes.GuildUser.from_user_discord_id_and_guild_discord_id",
                   return_value=SimpleNamespace(is_admin=False)):
            await PersonVotes.vote_creer.callback(cog, ctx, "Titre", "100 200", "2030-01-01 12:00")
        self.assertIn("administrateur", ctx.respond.call_args.args[0])
        ctx.guild = None
        await PersonVotes.vote_creer.callback(cog, ctx, "Titre", "100 200", "2030-01-01 12:00")
        self.assertEqual(len(PersonVote.all()), 0)

    async def test_results_deny_other_guild_and_inaccessible_channel(self):
        poll = self.launch()
        cog = object.__new__(PersonVotes)
        channel = SimpleNamespace(permissions_for=Mock(return_value=SimpleNamespace(view_channel=False)))
        ctx = SimpleNamespace(guild=SimpleNamespace(id=11, get_channel_or_thread=Mock(return_value=channel)),
                              author=Mock(), respond=AsyncMock())
        await PersonVotes.vote_resultats.callback(cog, ctx, poll.id)
        self.assertIn("introuvable", ctx.respond.call_args.args[0])
        ctx.guild.id = 10
        await PersonVotes.vote_resultats.callback(cog, ctx, poll.id)
        self.assertIn("accès", ctx.respond.call_args.args[0])

    def creation_context(self):
        channel = SimpleNamespace(id=20, send=AsyncMock(return_value=SimpleNamespace(id=30, jump_url="https://discord.com/message")))
        guild = SimpleNamespace(id=10, get_member=Mock(return_value=SimpleNamespace(bot=False)))
        return SimpleNamespace(guild=guild, channel=channel, author=SimpleNamespace(id=50),
                               defer=AsyncMock(), respond=AsyncMock())

    async def test_admin_creates_public_poll_with_configured_options(self):
        ctx = self.creation_context()
        with patch("cogs.barman.person_votes.GuildUser.from_user_discord_id_and_guild_discord_id",
                   return_value=SimpleNamespace(is_admin=True)):
            await PersonVotes.vote_creer.callback(object.__new__(PersonVotes), ctx,
                                                 "Élection", "<@100> <@!200>", "2030-01-01 12:00",
                                                 votes=5, anonyme=False, cumul=True)
        poll = PersonVote.all()[0]
        self.assertEqual(poll.message_id, "30")
        self.assertEqual(poll.candidate_ids, ["100", "200"])
        self.assertEqual(poll.votes_per_member, 5)
        self.assertFalse(poll.anonymous)
        self.assertTrue(poll.allow_multiple)
        self.assertTrue(ctx.channel.send.call_args.kwargs["view"].is_persistent())

    async def test_duplicate_candidate_ids_and_bots_are_rejected(self):
        for candidates, bot in (("100 0100", False), ("100 200", True)):
            with self.subTest(candidates=candidates, bot=bot):
                ctx = self.creation_context()
                ctx.guild.get_member.return_value.bot = bot
                with patch("cogs.barman.person_votes.GuildUser.from_user_discord_id_and_guild_discord_id",
                           return_value=SimpleNamespace(is_admin=True)):
                    await PersonVotes.vote_creer.callback(object.__new__(PersonVotes), ctx,
                                                         "Élection", candidates, "2030-01-01 12:00")
                ctx.channel.send.assert_not_awaited()
        self.assertEqual(len(PersonVote.all()), 0)

    async def test_failed_publication_does_not_leave_an_orphan_poll(self):
        ctx = self.creation_context()
        ctx.channel.send.side_effect = RuntimeError("Discord unavailable")
        with patch("cogs.barman.person_votes.GuildUser.from_user_discord_id_and_guild_discord_id",
                   return_value=SimpleNamespace(is_admin=True)), self.assertRaises(RuntimeError):
            await PersonVotes.vote_creer.callback(object.__new__(PersonVotes), ctx,
                                                 "Élection", "100 200", "2030-01-01 12:00")
        self.assertEqual(len(PersonVote.all()), 0)

    async def test_server_candidates_include_all_fetched_humans_and_exclude_bots(self):
        ctx = self.creation_context()
        members = [SimpleNamespace(id=id, bot=False) for id in range(100, 160)]
        members.append(SimpleNamespace(id=999, bot=True))

        async def fetch_members():
            for member in members:
                yield member

        ctx.guild.fetch_members = Mock(side_effect=lambda **kwargs: fetch_members())
        with patch("cogs.barman.person_votes.GuildUser.from_user_discord_id_and_guild_discord_id",
                   return_value=SimpleNamespace(is_admin=True)):
            await PersonVotes.vote_creer.callback(object.__new__(PersonVotes), ctx,
                                                 "Élection", " Serveur ", "2030-01-01 12:00")
        poll = PersonVote.all()[0]
        self.assertEqual(poll.candidate_ids, [str(id) for id in range(100, 160)])
        ctx.guild.fetch_members.assert_called_once_with(limit=None)
        ctx.guild.get_member.assert_not_called()
        self.assertEqual(poll.cast(50, 10, "159"), 0)
        self.assertLess(len(poll_embed(poll).description), 4096)
        poll.closed = True
        self.assertTrue(all(len(field.value) <= 1024 for field in poll_embed(poll).fields))

    async def test_large_poll_uses_searchable_member_picker(self):
        poll = self.launch(candidates=[str(id) for id in range(100, 160)])
        interaction = self.interaction()
        interaction.guild = Mock()
        await PollView(poll.id).vote(interaction)
        view = interaction.response.send_message.call_args.kwargs["view"]
        self.assertIsInstance(view.children[0], CandidateUserSelect)
        picker = view.children[0]
        interaction.response.send_modal = AsyncMock()
        with patch.object(CandidateUserSelect, "values", new_callable=PropertyMock,
                          return_value=[SimpleNamespace(id=159)]):
            await picker.callback(interaction)
        self.assertEqual(interaction.response.send_modal.call_args.args[0].candidate_id, "159")
        with patch.object(CandidateUserSelect, "values", new_callable=PropertyMock,
                          return_value=[SimpleNamespace(id=999)]):
            await picker.callback(interaction)
        self.assertIn("n'est pas candidate", interaction.response.send_message.call_args.args[0])
        self.assertEqual(interaction.response.send_modal.await_count, 1)

    async def test_server_with_fewer_than_two_humans_is_rejected(self):
        ctx = self.creation_context()

        async def fetch_members(**kwargs):
            yield SimpleNamespace(id=100, bot=False)
            yield SimpleNamespace(id=999, bot=True)

        ctx.guild.fetch_members = fetch_members
        with patch("cogs.barman.person_votes.GuildUser.from_user_discord_id_and_guild_discord_id",
                   return_value=SimpleNamespace(is_admin=True)):
            await PersonVotes.vote_creer.callback(object.__new__(PersonVotes), ctx,
                                                 "Élection", "serveur", "2030-01-01 12:00")
        ctx.channel.send.assert_not_awaited()
        self.assertEqual(len(PersonVote.all()), 0)
