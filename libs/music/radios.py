from dataclasses import dataclass
from libs.databases.models.radio import Radio as RadioStation


@dataclass(frozen=True)
class Radio:
    id: str
    name: str
    url: str


# Initial catalogue, seeded once by migration. Runtime choices always use the DB.
DEFAULT_RADIOS = (
    Radio("fip", "FIP", "https://icecast.radiofrance.fr/fip-midfi.mp3"),
    Radio("france-inter", "France Inter",
          "https://icecast.radiofrance.fr/franceinter-midfi.mp3"),
    Radio("france-info", "franceinfo",
          "https://icecast.radiofrance.fr/franceinfo-midfi.mp3"),
    Radio("france-culture", "France Culture",
          "https://icecast.radiofrance.fr/franceculture-midfi.mp3"),
    Radio("france-musique", "France Musique",
          "https://icecast.radiofrance.fr/francemusique-midfi.mp3"),
    Radio("mouv", "Mouv’", "https://icecast.radiofrance.fr/mouv-midfi.mp3"),
)


def radio_choices():
    return [{"id": radio.slug, "name": radio.name}
            for radio in sorted(RadioStation.all(), key=lambda radio: radio.name.casefold())]


def get_radio(radio_id):
    radio = RadioStation.whereFirst(slug=radio_id)
    if radio is None:
        raise ValueError("Choisissez une radio dans la liste proposée.")
    return radio
