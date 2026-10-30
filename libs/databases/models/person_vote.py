import hashlib
import json
import secrets
import time

from MIWOS.model import Model

from libs.databases.models.person_ballot import PersonBallot


class PersonVote(Model):
    @classmethod
    def launch(cls, *, guild_id, channel_id, title, candidates, votes_per_member,
               expires_at, anonymous, allow_multiple):
        if not title.strip() or len(title) > 200:
            raise ValueError(
                "Le titre doit contenir entre 1 et 200 caractères.")
        if len(candidates) < 2 or len(set(candidates)) != len(candidates):
            raise ValueError("Choisissez au moins 2 personnes différentes.")
        if not 1 <= votes_per_member <= 100:
            raise ValueError(
                "Le nombre de votes doit être compris entre 1 et 100.")
        if not allow_multiple and votes_per_member > len(candidates):
            raise ValueError(
                "Sans cumul, le quota ne peut pas dépasser le nombre de candidats.")
        if expires_at <= time.time():
            raise ValueError("La date de clôture doit être dans le futur.")
        return cls.createOrFail(
            guild_discord_id=str(guild_id), channel_id=str(channel_id),
            title=title.strip(), candidates=json.dumps(candidates),
            votes_per_member=votes_per_member, expires_at=expires_at,
            anonymous=anonymous, allow_multiple=allow_multiple, closed=False,
            salt=secrets.token_hex(32))

    @property
    def candidate_ids(self):
        return json.loads(self.candidates)

    @property
    def is_expired(self):
        return self.closed or time.time() >= self.expires_at

    def voter_key(self, user_id):
        if not self.anonymous:
            return str(user_id)
        # Keep Discord IDs out of anonymous ballots. This is pseudonymisation,
        # not cryptographic secrecy against an operator with database access.
        return hashlib.sha256(f"{self.salt}:{user_id}".encode()).hexdigest()

    def cast(self, user_id, guild_id, candidate_id, quantity=1):
        if str(guild_id) != self.guild_discord_id:
            raise ValueError("Ce scrutin appartient à un autre serveur.")
        if self.is_expired:
            raise ValueError("Ce scrutin est terminé.")
        if candidate_id not in self.candidate_ids:
            raise ValueError(
                "Cette personne ne fait pas partie des candidats.")
        if type(quantity) is not int or quantity < 1:
            raise ValueError(
                "Indiquez un nombre entier de votes supérieur à zéro.")
        key = self.voter_key(user_id)
        ballot = PersonBallot.whereFirst(personvote_id=self.id, voter_key=key)
        allocations = json.loads(ballot.allocations) if ballot else {}
        if not self.allow_multiple and (quantity > 1 or allocations.get(candidate_id, 0)):
            raise ValueError(
                "Un seul vote par candidat est autorisé pour ce scrutin.")
        used = sum(allocations.values())
        if used + quantity > self.votes_per_member:
            raise ValueError(
                f"Il vous reste {self.votes_per_member - used} vote(s).")
        allocations[candidate_id] = allocations.get(candidate_id, 0) + quantity
        if ballot:
            ballot.allocations = json.dumps(allocations)
            ballot.saveOrFail()
        else:
            PersonBallot.createOrFail(personvote_id=self.id, voter_key=key,
                                      allocations=json.dumps(allocations))
        return self.votes_per_member - used - quantity

    def results(self):
        totals = dict.fromkeys(self.candidate_ids, 0)
        details = []
        for ballot in PersonBallot.where(personvote_id=self.id):
            allocations = json.loads(ballot.allocations)
            for candidate, quantity in allocations.items():
                totals[candidate] += quantity
            if not self.anonymous:
                details.append((ballot.voter_key, allocations))
        return totals, details
