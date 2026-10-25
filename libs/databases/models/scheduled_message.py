import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from MIWOS.model import Model
from MIWOS.libs.sql.association import BelongsTo

from libs.databases.models.guild import Guild


class ScheduledMessage(Model):
    _belongs_to = [BelongsTo("guild")]

    @classmethod
    def by_name_and_guild(cls, name: str, guild: Guild) -> "ScheduledMessage | None":
        return cls.whereFirst(name=name, guild=guild)

    @staticmethod
    def validate_schedule(time: str, timezone: str) -> None:
        try:
            datetime.datetime.strptime(time, "%H:%M")
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Time must use the HH:MM format (for example 18:30).") from error
        try:
            ZoneInfo(timezone)
        except (TypeError, ZoneInfoNotFoundError) as error:
            raise ValueError(
                "Timezone must be a valid IANA timezone "
                "(for example Europe/Zurich).") from error
