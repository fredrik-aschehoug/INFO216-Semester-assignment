from pydantic import BaseSettings


class Settings(BaseSettings):
    yago_endpoint: str
    yago_endpoint_max_connections: int = 0
    wd_endpoint: str
    wd_endpoint_max_connections: int = 0


settings = Settings()
