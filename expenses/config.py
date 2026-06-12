
import os
from django.conf import settings

class CurrencyConfig:
    """Currency configuration - reads from environment variables"""
    
    # Read directly from environment variables
    BASE_CURRENCY = os.getenv("BASE_CURRENCY", "USD")
    API_URL = os.getenv("EXCHANGE_RATE_API_URL", "https://api.exchangerate.host")
    API_KEY = os.getenv("CURRENCY_API_KEY", "")
    TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))


class DiscordConfig:
    """Discord bot configuration - reads from environment variables"""
    
    WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
    TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))


# Create single instance
currency_config = CurrencyConfig()
discord_config = DiscordConfig()