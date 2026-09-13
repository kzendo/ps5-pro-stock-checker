import requests

URL = "https://direct.playstation.com/en-us/buy-consoles/playstation5-pro-console-2-tb"

response = requests.get(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    },
    timeout=30
)

print("HTTP status:", response.status_code)

page = response.text.lower()

print("Page length:", len(page))

if "add to cart" in page:
    print("🚨 POSSIBLE PS5 PRO RESTOCK! 🚨")
else:
    print("PS5 Pro does not appear to be available.")
