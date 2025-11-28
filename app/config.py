import os

class Settings:
    BUCKET_NAME = os.getenv("BUCKET_NAME")

settings = Settings()
