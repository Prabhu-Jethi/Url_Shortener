from pydantic_settings import BaseSettings

''' reads .env and validate it's content '''

class Settings(BaseSettings):
    ## from .env 
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_PUBLISHABLE_KEY: str
    SUPABASE_SECRET_KEY: str
    SUPABASE_JWKS_URL: str

    class Config:
        env_file = ".env"


settings = Settings()
