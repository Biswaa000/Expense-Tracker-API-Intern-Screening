# expenses/services/currency.py
from decimal import Decimal
import requests
from expenses.config import currency_config

def get_rates(base_currency):
    """Fetch exchange rates from API"""
    
    url = f"{currency_config.API_URL}/{base_currency}"
    
    # Prepare request parameters
    params = {}
    if currency_config.API_KEY:
        params = {"apikey": currency_config.API_KEY}
    
    response = requests.get(
        url,
        params=params,
        timeout=currency_config.TIMEOUT,
    )
    
    response.raise_for_status()
    data = response.json()
    
    # Handle different API response formats
    if "rates" in data:
        rates = data["rates"]
        date = data.get("time_last_update_utc", data.get("date", ""))
    elif "conversion_rates" in data:
        rates = data["conversion_rates"]
        date = data.get("time_last_update_utc", "")
    else:
        # Try to extract rates from exchangerate.host format
        if "rates" in data and isinstance(data["rates"], dict):
            rates = data["rates"]
            date = data.get("date", "")
        else:
            raise ValueError(f"Unexpected API response format")
    
    return {
        "rates": rates,
        "date": date,
    }


def convert_amount(amount, from_currency, to_currency):
    """Convert amount from one currency to another"""
    
    if from_currency == to_currency:
        return {
            "amount": amount,
            "rate": Decimal("1"),
            "date": None,
        }
    
    data = get_rates(from_currency)
    
    if to_currency not in data["rates"]:
        raise ValueError(f"Currency {to_currency} not found in exchange rates")
    
    rate = Decimal(str(data["rates"][to_currency]))
    converted = Decimal(str(amount)) * rate
    
    return {
        "amount": converted.quantize(Decimal("0.01")),
        "rate": rate.quantize(Decimal("0.0001")),
        "date": data["date"],
    }