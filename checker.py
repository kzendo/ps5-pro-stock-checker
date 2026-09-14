import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://direct.playstation.com/en-us/buy-consoles/playstation5-pro-console-2-tb"
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


def send_discord(message):
    response = requests.post(
        WEBHOOK_URL,
        json={"content": message},
        timeout=30
    )
    response.raise_for_status()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        )
    )

    print("Opening Sony page...")

    response = page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    print(
        "HTTP status:",
        response.status if response else "No response"
    )

    page.wait_for_timeout(5000)

    text = page.locator("body").inner_text().lower()

    if "currently unavailable" in text:
        print("❌ PS5 Pro is currently unavailable.")

    elif "add to cart" in text:
        print("🚨🚨 PS5 PRO MAY BE IN STOCK! 🚨🚨")

        send_discord(
            "🚨🚨 **PS5 PRO MAY BE IN STOCK!** 🚨🚨\n\n"
            "Sony PlayStation Direct appears to have the PS5 Pro available!\n\n"
            f"BUY NOW: {URL}"
        )

        print("✅ Discord notification sent!")

    else:
        print("⚠️ UNKNOWN STOCK STATUS")

    browser.close()

