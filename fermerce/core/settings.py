from dataclasses import dataclass
import os
from functools import lru_cache

from esmerald import EsmeraldAPISettings
from fermerce.core.config.development import DevelopmentSettings
from fermerce.core.config.production import ProductionSettings
from fermerce.core.config.testing import TestingSettings
from fermerce.lib.exceptions.exceptions import ServerError
from esmerald.conf.enums import EnvironmentType


@dataclass
class BaseSetting:
    environment: EnvironmentType = os.getenv("ENVIRONMENT")

    def get_environment(self):
        if self.environment == EnvironmentType.DEVELOPMENT:
            return DevelopmentSettings()
        elif self.environment == EnvironmentType.TESTING:
            return TestingSettings()
        elif self.environment == EnvironmentType.PRODUCTION:
            return ProductionSettings()
        raise ServerError("Internal server error")


@lru_cache
def get_settings():
    try:
        return BaseSetting().get_environment()
    except Exception as e:
        print(f"Error getting settings: {e}")  # Log error for debugging
        raise ServerError("Internal server error") from e


config = get_settings()
