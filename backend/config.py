# backend/config.py

import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir)
load_dotenv()

class Settings:
    PROJECT_NAME = "Agente Autônomo YouTube"
    VERSION = "1.0"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")

    # Credenciais e chaves
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    AFFILIATE_ID = os.getenv("AFFILIATE_ID", "")

    # Reinvestimento de lucros
    REINVEST_PERCENTAGE = float(os.getenv("REINVEST_PERCENTAGE", 0.2))

settings = Settings()
