from MIWOS.migration import Migration

from libs.databases.models.radio import Radio
from libs.music.radios import DEFAULT_RADIOS


class CreateRadios(Migration):
    def migrate(self):
        with self.create_tables("radios") as x:
            x.primary_key("id", auto_increment=True)
            x.string("slug", null=False, unique=True)
            x.string("name", null=False, unique=True)
            x.string("url", null=False)
        for radio in DEFAULT_RADIOS:
            Radio.createOrFail(slug=radio.id, name=radio.name, url=radio.url)

    def rollback(self):
        self.drop_tables("radios")
