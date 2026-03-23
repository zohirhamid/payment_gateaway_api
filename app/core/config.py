from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Payment Gateaway API"
    app_version: str = "0.1.0"
    app_description: str = "A Stripe-like payment gateway built with FastAPI for learning purposes."
    # database_url
    # debug?

settings = Settings()