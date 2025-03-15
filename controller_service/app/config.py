from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_enabled: bool = False
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    jwt_secret_key: str = "your-secret-key"  # Change this in production
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour

settings = Settings() 