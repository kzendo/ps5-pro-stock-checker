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

    response = page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    print("HTTP status:", response.status if response else "No response")

    page.wait_for_timeout(5000)

    print("Final URL:", page.url)
    print("Page title:", page.title())

    text = page.locator("body").inner_text().lower()

    print("Page text length:", len(text))

    if "add to cart" in text:
        print("🚨 POSSIBLE PS5 PRO RESTOCK! 🚨")
    else:
        print("PS5 Pro does not appear to be available.")

    browser.close()
