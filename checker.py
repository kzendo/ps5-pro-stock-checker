import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://direct.playstation.com/en-us/buy-consoles/playstation5-pro-console-2-tb"
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

PRODUCT_NAME = "PlayStation®5 Pro Console - 2 TB"


def send_discord(message):
    response = requests.post(
        WEBHOOK_URL,
        json={"content": message},
        timeout=30
    )
    response.raise_for_status()


def find_product_section(page):
    """
    Find the specific PS5 Pro product section instead of scanning
    the entire Sony webpage.
    """

    result = page.locator("text=" + PRODUCT_NAME)

    if result.count() == 0:
        return None

    # Find a visible occurrence of the product name.
    for i in range(result.count()):
        element = result.nth(i)

        if not element.is_visible():
            continue

        # Walk upward through ancestors looking for the product container.
        section = element.locator("xpath=..")

        for _ in range(8):
            if section.count() == 0:
                break

            try:
                text = section.inner_text().strip()

                # The product section should contain the product name
                # plus some kind of availability/purchase information.
                lowered = text.lower()

                availability_terms = [
                    "currently unavailable",
                    "out of stock",
                    "sold out",
                    "not available",
                    "low stock",
                    "available now",
                    "sign in to buy",
                    "add to cart",
                    "buy now",
                    "order now",
                ]

                if (
                    PRODUCT_NAME.lower() in lowered
                    and any(term in lowered for term in availability_terms)
                ):
                    return section

            except Exception:
                pass

            section = section.locator("xpath=..")

    return None


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

    # Give Sony's JavaScript time to finish rendering the product.
    page.wait_for_timeout(5000)

    product_section = find_product_section(page)

    if product_section is None:

        print("⚠️ Could not locate the PS5 Pro product section.")

        send_discord(
            "⚠️ **PS5 PRO CHECKER NEEDS ATTENTION** ⚠️\n\n"
            "The checker could not locate the PS5 Pro product section "
            "on Sony's page.\n\n"
            "Sony may have changed the page structure, or the page "
            "may have failed to load correctly.\n\n"
            f"CHECK NOW: {URL}"
        )

    else:

        product_text = product_section.inner_text().strip()
        text = product_text.lower()

        print("\n--- PS5 PRO PRODUCT SECTION ---")
        print(product_text)
        print("--------------------------------\n")

        # Known unavailable states.
        unavailable_states = [
            "currently unavailable",
            "out of stock",
            "sold out",
            "not available",
        ]

        # Known states that indicate the product may be purchasable.
        available_states = [
            "low stock",
            "available now",
            "sign in to buy",
            "add to cart",
            "buy now",
            "order now",
        ]

        unavailable_found = [
            state
            for state in unavailable_states
            if state in text
        ]

        available_found = [
            state
            for state in available_states
            if state in text
        ]

        if unavailable_found:

            print("❌ PS5 Pro is currently unavailable.")
            print("Detected:", ", ".join(unavailable_found))

        elif available_found:

            print("🚨🚨 PS5 PRO MAY BE IN STOCK! 🚨🚨")
            print("Detected:", ", ".join(available_found))

            send_discord(
                "🚨🚨 **PS5 PRO MAY BE IN STOCK!** 🚨🚨\n\n"
                "The PS5 Pro product section on Sony PlayStation Direct "
                "appears to show a purchasable/available state.\n\n"
                f"DETECTED: {', '.join(available_found)}\n\n"
                f"BUY NOW: {URL}"
            )

            print("✅ Discord notification sent!")

        else:

            print("⚠️ PS5 PRO PRODUCT STATE CHANGED")
            print("No known availability state was detected.")

            send_discord(
                "⚠️ **PS5 PRO PRODUCT STATE CHANGED — CHECK NOW!** ⚠️\n\n"
                "The PS5 Pro product section was found, but its "
                "availability state does not match any known state.\n\n"
                "Sony may have changed the wording or the product "
                "may have entered a new availability state.\n\n"
                f"CHECK NOW: {URL}"
            )

    browser.close()
