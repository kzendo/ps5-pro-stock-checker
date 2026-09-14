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

    # Give Sony's JavaScript time to finish rendering
    page.wait_for_timeout(5000)

    # --------------------------------------------------
    # GET PAGE TEXT
    # --------------------------------------------------

    text = page.locator("body").inner_text().lower()

    # --------------------------------------------------
    # KNOWN UNAVAILABLE STATES
    # --------------------------------------------------

    unavailable_states = [
        "currently unavailable",
        "out of stock",
        "sold out",
        "not available"
    ]

    # --------------------------------------------------
    # KNOWN AVAILABLE / PURCHASABLE STATES
    # --------------------------------------------------

    available_states = [
        "low stock",
        "available now",
        "sign in to buy",
        "add to cart",
        "buy now",
        "purchase",
        "order now"
    ]

    unavailable_found = [
        state for state in unavailable_states
        if state in text
    ]

    available_found = [
        state for state in available_states
        if state in text
    ]

    # --------------------------------------------------
    # DETERMINE STATUS
    # --------------------------------------------------

    if unavailable_found:
        print("❌ PS5 Pro is currently unavailable.")
        print("Detected:", ", ".join(unavailable_found))

    elif available_found:
        print("🚨🚨 PS5 PRO MAY BE IN STOCK! 🚨🚨")
        print("Detected:", ", ".join(available_found))

        send_discord(
            "🚨🚨 **PS5 PRO MAY BE IN STOCK!** 🚨🚨\n\n"
            "Sony PlayStation Direct appears to have the PS5 Pro "
            "available or purchasable.\n\n"
            f"BUY NOW: {URL}"
        )

        print("✅ Discord notification sent!")

    else:
        # Something changed, but we don't know what it means.
        # Alerting here gives us a safety net rather than silently
        # missing a Sony page redesign.
        print("⚠️ UNKNOWN STOCK STATUS")
        print("No known availability state was detected.")

        send_discord(
            "⚠️ **PS5 PRO PAGE CHANGED — CHECK NOW!** ⚠️\n\n"
            "The Sony PS5 Pro page no longer matches the known "
            "availability states.\n\n"
            "This could be a restock or a Sony page change.\n\n"
            f"CHECK NOW: {URL}"
        )

    browser.close()
