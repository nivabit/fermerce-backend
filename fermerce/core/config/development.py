from esmerald.conf.enums import EnvironmentType
from fermerce.core.config.production import ProductionSettings


class DevelopmentSettings(ProductionSettings):
    environment: str = EnvironmentType.DEVELOPMENT
    debug: bool = True
