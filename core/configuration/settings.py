from typing import Optional

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):

    APP_PATH: str = ""
    SOURCE_PATH: str = ""
    CONFIGURATION_PATH: str = ""
    SOURCE_CONFIG: Optional[dict] = dict()


settings = Settings()
