# settings.py
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    ENVIRONMENT: str
    APP_NAME: str

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value):
        if value not in ("dev", "test", "prod"):
            raise ValueError("not in enviroment")
        return value


# Settings(ENVIRONMENT="dev", APP_NAME="app")


# Pydantic wykona mniej więcej:
# value = "dev"
# value = Settings.validate_environment(value)


# Jeszcze czytelniej można opisać dozwolone wartości bez własnego walidatora:

# from typing import Literal
# from pydantic_settings import BaseSettings
# class Settings(BaseSettings):
#     ENVIRONMENT: Literal["dev", "test", "prod"]
#     APP_NAME: str
