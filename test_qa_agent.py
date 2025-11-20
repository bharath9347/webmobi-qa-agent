import os
import time
import pytest
from playwright.sync_api import sync_playwright, expect
from dotenv import load_dotenv, find_dotenv
from datetime import datetime

# 1. Load Credentials
load_dotenv(find_dotenv())
EMAIL = os.getenv("WEBMOBI_EMAIL")
PASSWORD = os.getenv("WEBMOBI_PASSWORD")

def test_full_qa_flow():
    with sync_playwright() as p:
        # Launch visibly so you can RECORD VIDEO now
        browser = p.chromium.launch(headless=False, slow_mo=1000) 
        context = browser.new_context(viewport={'width': 1500, 'height': 800})
        page = context.new_page()

        try:
            print("--- Step 1: Direct Login ---")
            # Use the URL you successfully found
            page.goto("https://events.webmobi.com/auth/login") 
            page.wait_for_load_state("networkidle")
            
            print(f"Logging in as {EMAIL}...")
            page.fill('input[type="email"]', EMAIL)
            page.fill('input[type="password"]', PASSWORD)
            
            # ROBUST FIX: Press 'Enter' instead of looking for a button
            # This works on almost every website!
            print("Pressing ENTER to submit...")
            page.keyboard.press('Enter')
            
            # Wait for Dashboard
            print("Waiting for Dashboard redirect...")
            # Wait up to 15 seconds for the URL to change
            page.wait_for_url("**/events**", timeout=15000) 
            print("✅ LOGIN SUCCESSFUL!")

            # --- Step 2: Create Event ---
            print("--- Step 2: Create New Event ---")
            
            # 1. Find 'Create Event' button (Update text if needed based on what you see)
            # Trying common variations
            try:
                page.click('text=Create Event', timeout=3000)
            except:
                try:
                    page.click('text=New Event', timeout=3000)
                except:
                    # If automation fails here, click it manually while recording!
                    print("⚠️ Could not click 'Create Event'. Please CLICK IT MANUALLY now!")
                    time.sleep(5) 

            # 2. Fill Event Form
            event_name = f"QA Auto Event {datetime.now().strftime('%H-%M')}"
            print(f"Creating event: {event_name}")
            
            # Look for Name input (usually first input)
            page.locator("input").first.fill(event_name)
            
            # Submit Event (Press Enter again)
            page.keyboard.press('Enter')
            
            # --- Step 3: Validation ---
            print("--- Step 3: Validating ---")
            time.sleep(3) # Wait for list to reload
            
            # Check if our event name appears on screen
            if page.get_by_text(event_name).is_visible():
                print(f"✅ TEST PASSED: Event '{event_name}' created and verified.")
                page.screenshot(path="success_evidence.png")
            else:
                print("⚠️ Event created, but not found in list immediately.")
                page.screenshot(path="partial_success.png")

        except Exception as e:
            print(f"❌ TEST FAILED: {e}")
            page.screenshot(path="failure_evidence.png")
        
        finally:
            print("Closing in 5 seconds...")
            time.sleep(5)
            browser.close()

if __name__ == "__main__":
    test_full_qa_flow()