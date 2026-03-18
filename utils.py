from playwright.sync_api import sync_playwright


def find_url(query: str):
    # "hello+world%21+--+-"
    sub_url = query.replace(" ", "+")
    search_url = f"https://www.lyricsify.com/search?q={sub_url}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(search_url)

        page.wait_for_timeout(5000)  # or better: wait_for_selector

        print(page.content())
        browser.close()

def extract(url: str):
    ...


url = find_url("i think therefore i am")
print(url)