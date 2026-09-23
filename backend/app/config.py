from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Operator Ergonomics & Environment API"
    data_dir: Path = Path(__file__).resolve().parent.parent.parent / "data"
    models_dir: Path = Path(__file__).resolve().parent.parent.parent / "models"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    log_level: str = "INFO"
    chassis_shock_threshold: float = 0.7
    co2_warning_threshold: float = 1000.0
    facial_temp_warning_threshold: float = 37.2
    max_series_limit: int = 1000
    default_series_limit: int = 120
    stream_interval_seconds: float = 1.0
    stream_series_window: int = 120

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
