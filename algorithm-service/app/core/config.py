from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the solver service."""

    service_name: str = "stowage-algorithm-service"
    log_level: str = "INFO"
    default_solver_time_limit_seconds: int = 10
    default_gm_min: float = 0.5
    default_adjacent_hold_diff_max: float = 0.4
    default_ix_max: float = 5000.0
    default_fsc: float = 0.0
    default_isolation_distance: float = 1.0
    max_iterations: int = 3
    epsilon: float = 1e-6
    model_config = SettingsConfigDict(env_prefix="STOWAGE_", case_sensitive=False)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings."""
    return Settings()

