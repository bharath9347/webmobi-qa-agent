from playwright.sync_api import sync_playwright
import time

def inspect_login_page():
    with sync_playwright() as p:
        # Launch WITH a visible window so you can see what happens
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        print("--- Navigating to WebMobi Login ---")
        # Try the main URL first, it usually redirects to login
        page.goto("https://events.webmobi.com/login") 
        
        print("Waiting 5 seconds for page to load...")
        time.sleep(5) # Give it time to render visually
        
        print("\n--- LOOKING FOR INPUTS ---")
        inputs = page.locator("input").all()
        
        if len(inputs) == 0:
            print("❌ No inputs found! Is there a 'Login' button we need to click first?")
            # Print all buttons just in case
            buttons = page.locator("button").all()
            print(f"Found {len(buttons)} buttons. Texts: {[b.inner_text() for b in buttons]}")
        else:
            print(f"✅ Found {len(inputs)} input fields:")
            for i, inp in enumerate(inputs):
                # Print the HTML of each input so we can copy the real ID/Name
                print(f"Input {i+1}: {inp.evaluate('el => el.outerHTML')}")

        print("\n--- LEAVING BROWSER OPEN FOR 20 SECONDS (Please Inspect Manually) ---")
        time.sleep(20)
        browser.close()

if __name__ == "__main__":
    inspect_login_page()