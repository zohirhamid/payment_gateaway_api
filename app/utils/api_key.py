import secrets


# python's secrets module is made for generating secure random values
# example shape pg_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
def generate_api_key() -> str:
    return f"pg_live_{secrets.token_urlsafe(32)}"

