# expenses/services/currency.py
from decimal import Decimal
import requests
from expenses.config import currency_config

def get_rates(base_currency):
    """Fetch exchange rates from API"""
    
    # For exchangerate.host with API key
    if currency_config.API_KEY:
        # Use the live endpoint with API key
        url = currency_config.API_URL
        params = {
            "access_key": currency_config.API_KEY,
            "source": base_currency,  # Use 'source' instead of 'base' for this API
            "format": 1
        }
    else:
        # Free tier without API key
        url = f"{currency_config.API_URL}/{base_currency}"
        params = {}
    
    response = requests.get(
        url,
        params=params,
        timeout=currency_config.TIMEOUT,
    )
    
    response.raise_for_status()
    data = response.json()
    
    # Check if API call was successful
    if not data.get("success", True):
        error_msg = data.get("error", {}).get("info", "Unknown error")
        raise ValueError(f"API Error: {error_msg}")
    
    # Handle different API response formats
    if "quotes" in data:
        # exchangerate.host live endpoint format
        # Quotes come as SOURCEcurrency format (e.g., USDAED)
        rates = {}
        for key, value in data["quotes"].items():
            # Remove source currency from key (e.g., USDAED -> AED)
            currency_code = key[3:]  # Remove first 3 characters (USD)
            rates[currency_code] = value
        date = data.get("timestamp", "")
        # Convert timestamp to readable date if needed
        if date:
            from datetime import datetime
            date = datetime.fromtimestamp(date).strftime("%Y-%m-%d")
        
    elif "rates" in data:
        # Standard format
        rates = data["rates"]
        date = data.get("date", data.get("time_last_update_utc", ""))
        
    elif "conversion_rates" in data:
        # ExchangeRate-API format
        rates = data["conversion_rates"]
        date = data.get("time_last_update", "")
        
    else:
        raise ValueError(f"Unexpected API response format. Keys: {list(data.keys())}")
    
    return {
        "rates": rates,
        "date": date,
    }


def convert_amount(amount, from_currency, to_currency):
    """Convert amount from one currency to another"""
    
    # If same currency, return original amount
    if from_currency == to_currency:
        return {
            "amount": Decimal(str(amount)).quantize(Decimal("0.01")),
            "rate": Decimal("1"),
            "date": None,
        }
    
    data = get_rates(from_currency)
    
    # Check if target currency exists in rates
    if to_currency not in data["rates"]:
        available = list(data["rates"].keys())[:20]  # Show first 20 available
        raise ValueError(f"Currency {to_currency} not found. Available: {available}")
    
    rate = Decimal(str(data["rates"][to_currency]))
    converted = Decimal(str(amount)) * rate
    
    return {
        "amount": converted.quantize(Decimal("0.01")),
        "rate": rate.quantize(Decimal("0.0001")),
        "date": data["date"],
    }