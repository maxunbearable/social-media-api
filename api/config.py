from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    ENV_STATE: Optional[str] = None
    
    class Config:
        env_file = ".env"

class GlobalConfig(BaseConfig):
    DATABASE_URL: Optional[str] = None
    DB_FORCE_ROLLBACK: bool = False

class DevConfig(GlobalConfig):
    env_prefix = "DEV_"

class ProdConfig(GlobalConfig):
    env_prefix = "PROD_"

class TestConfig(GlobalConfig):
    DATABASE_URL = "sqlite///test.db"
    DB_FORCE_ROLLBACK = True

@lru_cache(maxsize=1)
def get_config(env_state: Optional[str] = None) -> GlobalConfig:
    configs = {
        "dev": DevConfig(),
        "prod": ProdConfig(),
        "test": TestConfig(),
    }
    
    return configs.get(env_state, GlobalConfig())

config = get_config(BaseConfig().ENV_STATE)