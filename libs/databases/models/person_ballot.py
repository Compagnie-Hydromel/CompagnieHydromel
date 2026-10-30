from MIWOS.libs.sql.association import BelongsTo
from MIWOS.model import Model


class PersonBallot(Model):
    _belongs_to = [BelongsTo("personvote")]
