import os
from pathlib import Path
from typing import Optional
import yaml
from dotenv import load_dotenv


env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    #Основные настройки
    APP_NAME: str = os.getenv("APP_NAME", "SmartHomeSystem")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", False).lower() == "true"

    #Сетевые настройки
    FLASK_HOST: str = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "127.0.0.1")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))

    #Пути
    BASE_DIR = Path(__file__).parent.parent
    DATA_PATH = BASE_DIR / os.getenv("DATA_PATH", "data")
    CACHE_PATH = BASE_DIR / os.getenv("CACHE_PATH", "cache")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")

    #Яндекс API
    YANDEX_API_KEY: Optional[str] = os.getenv("YANDEX_API_KEY")
    YANDEX_SKILL_ID: Optional[str] = os.getenv("YANDEX_SKILL_ID")
    YANDEX_OAUTH_TOKEN: Optional[str] = os.getenv("YANDEX_OAUTH_TOKEN")

    #Логирование 
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def create_directories(cls):
        directories = [
            cls.DATA_PATH,
            cls.DATA_PATH / "database",
            cls.CACHE_PATH,
            cls.BASE_DIR / "logs"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load_yaml_config(cls, config_path: str = "config/config.yaml") -> dict:
        config_file = cls.BASE_DIR / config_path
        try:
            with open(config_file, "r", encoding="UTF-8") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return {}
        
    @classmethod
    def is_development(cls) -> bool:
        return cls.ENVIRONMENT.lower() == "development"

config = Config()
config.create_directories()