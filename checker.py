import os
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

    print("\n========== AVAILABILITY-RELATED ELEMENTS ==========\n")

    elements = page.locator(
        "text=/available|unavailable|stock|cart|purchase|buy/i"
    )

    for i in range(elements.count()):
        element = elements.nth(i)

        try:
            if not element.is_visible():
                continue

            text = element.inner_text().strip()

            if not text:
                continue

            tag = element.evaluate("(el) => el.tagName")
            classes = element.get_attribute("class")
            aria = element.get_attribute("aria-label")
            disabled = element.get_attribute("disabled")
            aria_disabled = element.get_attribute("aria-disabled")

            print("--------------------------------------------------")
            print(f"TAG:           {tag}")
            print(f"TEXT:          {text[:500]}")
            print(f"CLASS:         {classes}")
            print(f"ARIA-LABEL:    {aria}")
            print(f"DISABLED:      {disabled}")
            print(f"ARIA-DISABLED: {aria_disabled}")

        except Exception:
            pass

    print("\n========== PRODUCT AREA TEXT ==========\n")

    body_text = page.locator("body").inner_text()

    # Print the first part of the page text so we can see
    # how Sony is presenting the product.
    print(body_text[:10000])

    print("\n========== END DIAGNOSTIC ==========\n")

    browser.close()
