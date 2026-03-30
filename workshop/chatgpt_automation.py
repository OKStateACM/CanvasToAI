# =============================================================================
# 🛠️ WORKSHOP: ChatGPT Automation with Playwright
# =============================================================================
#
# INSTRUCTIONS:
#   Replace every _______ blank with the correct code.
#   Each blank has a HINT comment above it to guide you.
#   Run the completed script to automate ChatGPT through your browser!
#
# CONCEPTS COVERED:
#   • Launching a persistent browser context with Playwright
#   • Navigating to URLs
#   • Waiting for and finding elements (selectors, test-ids)
#   • Uploading files using hidden <input type="file"> elements
#   • Filling text fields and submitting forms
#   • Keeping the browser open for user handoff
#
# =============================================================================

from playwright.sync_api import sync_playwright
import os
import time

class ChatGPTBot:
    def __init__(self, user_data_dir="playwright_profile"):
        # HINT: Convert the user_data_dir to an absolute path using os.path
        self.user_data_dir = _______

    def setup_login(self):
        """Opens a browser so the user can log into ChatGPT and save their session."""

        print(f"Opening ChatGPT for initial setup/login. Data dir: {self.user_data_dir}")

        with sync_playwright() as p:
            # HINT: Launch a PERSISTENT Chromium context so cookies/session are saved.
            #       Use channel="chrome" to use Google Chrome, headless=False so you can see it.
            #       Method: p.chromium.launch_persistent_context(...)
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

            # HINT: Get an existing page or create a new one from the browser context
            page = browser.pages[0] if len(browser.pages) > 0 else browser._______()

            # HINT: Navigate to the ChatGPT login page using page.goto(...)
            page._______(________)

            print("Please log in. Close the browser when you are finished.")
            try:
                # This line waits forever until you close the browser tab
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            browser.close()
            print("Setup finished!")

    def run_automation(self, prompt, attachment_paths):
        """Automates sending a prompt (and optional files) to ChatGPT."""

        print(f"Starting Playwright automation. Data dir: {self.user_data_dir}")

        with sync_playwright() as p:
            # HINT: Same as setup — launch a persistent context with Chrome
            browser = p.chromium._______(
                user_data_dir=self.user_data_dir,
                headless=False,
                channel=_______,
                args=[
                    "--window-size=1280,900",
                    "--disable-blink-features=AutomationControlled"
                ],
                viewport={'width': 1280, 'height': 900},
                ignore_default_args=["--enable-automation"]
            )

            page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()

            # HINT: Navigate to ChatGPT's main page
            page._______(________)

            print("Checking if we need to log in manually...")
            try:
                # HINT: Look for a "Log in" button on the page using page.get_by_text(...)
                login_btn = page._______(_______, exact=True)
                if login_btn.is_visible(timeout=2000):
                    print("Found 'Log in' button, clicking it for you...")
                    # HINT: Click the login button
                    login_btn._______()
            except Exception:
                pass

            try:
                # HINT: Wait for the ChatGPT text input box to appear.
                #       The chat box has id="prompt-textarea" → use CSS selector "#prompt-textarea"
                page._______(_______, timeout=10000)
            except Exception:
                print("Could not find chat input. Did you use the 'Setup Login' button? Exiting.")
                browser.close()
                return

            print("Chat page is ready! Proceeding with auto-upload...")
            try:
                # ------ FILE ATTACHMENT SECTION ------
                if attachment_paths:
                    # HINT: Filter to only paths that actually exist on disk
                    valid_paths = [os.path.abspath(p) for p in attachment_paths if _______]
                    if valid_paths:
                        try:
                            # HINT: The most robust way to upload in ChatGPT is to find
                            #       the hidden <input type="file"> element and set files on it.
                            #       Use page.locator('input[type="file"]')
                            file_inputs = page._______(________)
                            if file_inputs.count() > 0:
                                uploaded = False
                                for i in range(file_inputs.count()):
                                    try:
                                        # HINT: Use .set_input_files(paths) on the file input
                                        file_inputs.nth(i)._______(valid_paths)
                                        uploaded = True
                                        break
                                    except Exception:
                                        continue

                                if not uploaded:
                                    raise Exception("None of the hidden file inputs accepted the files.")
                            else:
                                # Fallback: click the attach button to trigger a file chooser
                                page.locator(
                                    '[data-testid="composer-plus-btn"], '
                                    '[aria-label="Attach files"], '
                                    '[aria-label="Add files and more"]'
                                ).first.click()
                                page.wait_for_timeout(1000)

                                # HINT: Use page.expect_file_chooser() to intercept the file dialog
                                with page._______(timeout=5000) as fc_info:
                                    page.locator('text=/Upload/i').first.click()
                                # HINT: Set the files on the file chooser that was intercepted
                                fc_info.value._______(valid_paths)

                            print(f"Successfully uploaded {len(valid_paths)} files.")
                            time.sleep(6)  # Wait for uploads to finish
                        except Exception as e:
                            print(f"Could not automate file attachment: {e}")
                            print("Please attach files manually if needed.")

                # ------ PROMPT INJECTION SECTION ------
                print("Injecting prompt...")
                # HINT: Fill the chat text area with the prompt text.
                #       Use page.fill(selector, text) with the "#prompt-textarea" selector
                page._______(_______, prompt)
                time.sleep(1)

                # ------ SEND SECTION ------
                # HINT: Click the send button. ChatGPT uses data-testid="send-button"
                try:
                    page.locator(_______).click()
                except Exception:
                    # Fallback: just press Enter
                    page.keyboard.press("Enter")

            except Exception as e:
                print(f"Error during ChatGPT automation: {e}")

            print("Handoff to user! The browser will stay open so you can do your thing.")
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
#     bot = ChatGPTBot()
#     # Step 1: Run setup first to log in (only needed once)
#     # bot.setup_login()
#     # Step 2: Then run the automation
#     # bot.run_automation("Explain quantum computing in simple terms", [])
