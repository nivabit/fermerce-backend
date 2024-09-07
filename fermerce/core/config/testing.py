from databasez import Database
from edgy import Registry
from esmerald.conf.enums import EnvironmentType


from fermerce.core.config.production import ProductionSettings


class TestingSettings(ProductionSettings):
    environment: str = EnvironmentType.TESTING
    debug: bool = True

    @property
    def registry(self) -> tuple[Database, Registry]:
        database = Database(f"{self.get_database_url()}_test")
        return database, Registry(database=database)
