from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Payment Gateway API"
    app_version: str = "0.1.0"
    app_description: str = "A Stripe-like payment gateway built with FastAPI for learning purposes."
    database_url: str = "sqlite:///./payment_gateway.db"
    
    rate_limit_create_payment_intent_max_requests: int = 10
    rate_limit_create_payment_intent_window_seconds: int = 10
    
    rate_limit_confirm_intent_max_requests: int = 5
    rate_limit_confirm_payment_intent_window_seconds: int = 60

settings = Settings()

