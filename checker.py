import os
import requests

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

message = (
    "🧪 **PS5 Stock Bot Test**\n\n"
    "If you're seeing this, GitHub successfully sent a message "
    "through the Discord webhook!"
)

response = requests.post(
    WEBHOOK_URL,
    json={"content": message},
    timeout=30
)

print("Discord HTTP status:", response.status_code)
print("Discord response:", response.text)

response.raise_for_status()

print("✅ Discord message sent successfully!")


