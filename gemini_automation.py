# =============================================================================
# 🛠️ WORKSHOP: Gemini Automation with Playwright
# =============================================================================
#
# INSTRUCTIONS:
#   Replace every _______ blank with the correct code.
#   Each blank has a HINT comment above it to guide you.
#   Run the completed script to automate Google Gemini through your browser!
#
# CONCEPTS COVERED:
#   • Launching a persistent browser context with Playwright
#   • Navigating to URLs and waiting for page load
#   • Using multiple CSS selectors for resilient element finding
#   • Handling dynamic menus and popups
#   • File upload via file chooser interception
#   • Typing text into contenteditable areas
#   • Keyboard actions (Enter to send)
#
# =============================================================================

from playwright.sync_api import sync_playwright
import os
import time
import re

class GeminiBot:
    def __init__(self, user_data_dir="playwright_profile"):
        # HINT: Convert the user_data_dir to an absolute path using os.path
        self.user_data_dir = _______

    def setup_login(self):
        """Opens a browser so the user can log into their Google account for Gemini."""

        print(f"Opening Gemini for initial setup/login. Data dir: {self.user_data_dir}")

        with sync_playwright() as p:
            # HINT: Launch a PERSISTENT Chromium context.
            #       Key args: user_data_dir, headless=False, channel="chrome"
            browser = p.chromium._______(
                user_data_dir=self.user_data_dir,
                headless=_______,
                channel="chrome",
                args=[
                    "--window-size=1280,900",
                    "--disable-blink-features=AutomationControlled"
                ],
                viewport={'width': 1280, 'height': 900},
                ignore_default_args=["--enable-automation"]
            )

            # HINT: Get the first existing page or create a new one
            page = browser.pages[0] if len(browser.pages) > 0 else browser._______()

            # HINT: Navigate to Gemini's web app
            page._______(________)

            print("Please log in to your Google Account if required. Close the browser when finished.")
            try:
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            browser.close()
            print("Gemini Setup finished!")

    def run_automation(self, prompt, attachment_paths):
        """Automates sending a prompt (and optional files) to Google Gemini."""

        print(f"Starting Playwright automation for Gemini. Data dir: {self.user_data_dir}")

        with sync_playwright() as p:
            # HINT: Launch persistent context, same as setup, but also disable
            #       the Translate feature to avoid popup interference
            browser = p.chromium._______(
                user_data_dir=self.user_data_dir,
                headless=False,
                channel=_______,
                args=[
                    "--window-size=1280,900",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=Translate"
                ],
                viewport={'width': 1280, 'height': 900},
                ignore_default_args=["--enable-automation"]
            )

            page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()

            # HINT: Navigate to Gemini
            page._______(________)

            print("Waiting for chat page to be ready...")
            try:
                # HINT: Gemini's chat input is a <div> with contenteditable="true".
                #       Wait for it using page.wait_for_selector(...)
                page._______(_______, timeout=10000)
            except Exception:
                print("Could not find chat input. Did you use the 'Setup Gemini Login' button? Exiting.")
                browser.close()
                return

            print("Gemini Chat page is ready! Proceeding with auto-upload...")
            try:

                # ------ FILE ATTACHMENT SECTION ------
                if attachment_paths:
                    # HINT: Filter to only paths that exist on disk
                    valid_paths = [os.path.abspath(p) for p in attachment_paths if _______]
                    if valid_paths:
                        try:
                            print(f"Attempting to upload {len(valid_paths)} files...")

                            # STRATEGY: Find the upload trigger button (the "+" button).
                            # Gemini's UI can show different aria-labels depending on language,
                            # so we try MULTIPLE selectors for resilience.
                            upload_trigger = None
                            for attempt in range(4):
                                selectors = [
                                    # HINT: Fill in CSS selectors that might match the attach/upload button.
                                    #       Think about: aria-controls, aria-label, mat-icon names, etc.
                                    'button[aria-controls="upload-file-menu"]',
                                    _______,  # HINT: a selector using aria-label that contains "add" (case-insensitive)
                                    _______,  # HINT: a selector using aria-label that contains "upload" (case-insensitive)
                                ]

                                for selector in selectors:
                                    trigger = page.locator(selector).first
                                    # HINT: Check that the element exists AND is visible
                                    if trigger.count() > 0 and trigger._______():
                                        upload_trigger = trigger
                                        break

                                if upload_trigger:
                                    break

                                print(f"Upload button not found (attempt {attempt+1}/4). Waiting...")
                                # HINT: Wait 1500ms before retrying. Use page.wait_for_timeout(...)
                                page._______(________)

                            if upload_trigger:
                                print("Found upload trigger button. Clicking...")
                                # HINT: Click the upload trigger button
                                upload_trigger._______()
                                page.wait_for_timeout(2000)  # Wait for menu animation

                                # Now find the "Upload from computer" menu item
                                menu_selectors = [
                                    'button[data-test-id="local-images-files-uploader-button"]',
                                    'button[role="menuitem"]:has-text("Upload from computer")',
                                    'button[role="menuitem"]:has-text("Subir desde este ordenador")',
                                ]

                                menu_item = None
                                for selector in menu_selectors:
                                    # HINT: Find the first matching element using page.locator(selector).first
                                    item = page._______(selector)._______
                                    if item.count() > 0 and item.is_visible():
                                        menu_item = item
                                        break

                                try:
                                    if menu_item and menu_item.count() > 0 and menu_item.is_visible():
                                        print("Found menu item for local upload. Clicking...")
                                        # HINT: Use page.expect_file_chooser() to intercept the
                                        #       file dialog, then click the menu item inside the with block
                                        with page._______(timeout=10000) as fc_info:
                                            menu_item.click()
                                        # HINT: Set files on the intercepted file chooser
                                        fc_info.value._______(valid_paths)
                                    else:
                                        print("Menu item not found. Pressing Escape and trying fallback...")
                                        # HINT: Press the Escape key to close any open menu
                                        page.keyboard.press(_______)
                                        page.wait_for_timeout(500)
                                except Exception as e:
                                    print(f"File chooser failed to trigger: {e}")
                            else:
                                print("Could not find the attach button after multiple attempts.")

                            print(f"Successfully processed {len(valid_paths)} files.")
                            time.sleep(6)

                        except Exception as e:
                            print(f"Could not automate file attachment: {e}")
                            print("Please attach files manually if needed.")

                # ------ PROMPT INJECTION SECTION ------
                print("Injecting prompt...")
                # HINT: Gemini uses a contenteditable div, NOT a regular <input>.
                #       We need to: 1) Click on it,  2) Use keyboard.insert_text() to type
                chat_box = page.locator(_______).first
                chat_box._______()
                # HINT: Use page.keyboard.insert_text(text) to type the prompt
                page.keyboard._______(prompt)
                time.sleep(1)

                # ------ SEND SECTION ------
                # HINT: Press Enter to send the message in Gemini
                page.keyboard.press(_______)

            except Exception as e:
                print(f"Error during Gemini automation: {e}")

            print("Handoff to user! The browser will stay open so you can read the response.")
            print("Close the browser window when you are done.")
            try:
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass

            browser.close()


# =============================================================================
# 🧪 QUICK TEST — Uncomment the lines below to try your implementation!
# =============================================================================
# if __name__ == "__main__":
#     bot = GeminiBot()
#     # Step 1: Run setup first to log in (only needed once)
#     # bot.setup_login()
#     # Step 2: Then run the automation
#     # bot.run_automation("Summarize the key concepts of machine learning", [])
