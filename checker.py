import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://direct.playstation.com/en-us/buy-consoles/playstation5-pro-console-2-tb"

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

    print("\n========== VISIBLE BUTTONS ==========\n")

    buttons = page.locator("button")

    for i in range(buttons.count()):
        button = buttons.nth(i)

        try:
            if not button.is_visible():
                continue

            text = button.inner_text().strip()
            disabled = button.is_disabled()

            print(
                f"BUTTON {i}: "
                f"text='{text}' | "
                f"disabled={disabled}"
            )

        except Exception:
            pass

    print("\n========== VISIBLE LINKS ==========\n")

    links = page.locator("a")

    for i in range(links.count()):
        link = links.nth(i)

        try:
            if not link.is_visible():
                continue

            text = link.inner_text().strip()
            href = link.get_attribute("href")

            print(
                f"LINK {i}: "
                f"text='{text}' | "
                f"href='{href}'"
            )

        except Exception:
            pass

    print("\n========== END DIAGNOSTIC ==========\n")

    browser.close()
