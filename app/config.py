import os


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key-in-production",
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./sea_battle.db",
)

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1,
    )