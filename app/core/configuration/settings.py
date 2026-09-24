from pathlib import Path


class Settings:
    APP_PATH: Path = Path()
    SOURCE_PATH: Path = Path()
    CONFIGURATION_PATH: Path = Path()
    SOURCE_CONFIG: dict = {}
    ALL_SOURCES: dict = {}


settings = Settings()
