import requests
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def get_country_choices():
    cached = cache.get("country_choices")
    if cached:
        return cached

    url = "https://restcountries.com/v3.1/all"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            countries = response.json()
            choices = sorted([
                (country["cca3"], country["name"]["common"])
                for country in countries if "cca3" in country
            ])
            cache.set("country_choices", choices, timeout=86400)
            return choices
    except Exception as e:
        logger.warning(f"Failed to fetch countries: {e}")

    return [
        ('USA', 'United States'),
        ('GBR', 'United Kingdom'),
        ('KEN', 'Kenya'),
        ('NGA', 'Nigeria'),
        ('UGA', 'Uganda'),
        ('IND', 'India'),
        ('CAN', 'Canada'),
        ('CHN', 'China'),
        ('JPN', 'Japan'),
        ('ABW', 'Aruba'),
    ]

#  Define this constant so it can be imported elsewhere
COUNTRIES = get_country_choices()



CRYPTO_CHOICES = [
    ("BTC", "Bitcoin"),
    ("ETH", "Ethereum"),
    ("USDT", "Tether"),
    ("BNB", "Binance Coin"),
    ("XRP", "XRP"),
]

PAYMENT_METHODS = [
    ('GPay', 'Google Pay'),
    ('APay', 'Apple Pay'),
    ('Crypto', 'Cryptocurrency'),
    ('Bank Transfer', 'Bank Transfer'),
    ('M-Pesa', 'M-Pesa'),
    ('Binance', 'Binance'),
    ('Mobile Wallet', 'Mobile Wallet'),
    ('Card', 'Card'),
]  # Dynamically append cryptocurrency choices





# Currency Choices
CURRENCY_CHOICES = [
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
    ('GBP', 'British Pound'),
    ('KES', 'Kenyan Shilling'),
    ('NGN', 'Nigerian Naira'),
    ('BTC', 'Bitcoin'),
    ('ETH', 'Ethereum'),
    ('JCB', 'Japan Credit Bureau'),
    ('USDT', 'United States Tether'),
    ("BNB", "Binance Coin"),
]







STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]


FEE_STATUS_CHOICES = [
    ("Pending", "Pending"),
    ("Transferred", "Transferred"),
    ("Failed", "Failed"),
]