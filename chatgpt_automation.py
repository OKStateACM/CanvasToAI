from playwright.sync_api import sync_playwright
import os
import time
import tkinter as tk

class ChatGPTBot:
    def __init__(self, user_data_dir="playwright_profile"):
        self.user_data_dir = os.path.abspath(user_data_dir)

    def _get_dynamic_size(self):
        """Returns a reasonable window size (width, height) based on screen resolution."""
        # We use a small temporary tkinter root to get the screen size
        try:
            root = tk.Tk()
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            root.destroy()
            
            # Use 50% of width and 80% of height, but not too small
            target_w = max(1024, int(sw * 0.5))
            target_h = max(768, int(sh * 0.8))
            
            # Ensure we don't exceed screen size
            target_w = min(target_w, sw)
            target_h = min(target_h, sh)
            
            return target_w, target_h
        except Exception:
            return 1024, 768

    def setup_login(self):
        print(f"Opening ChatGPT for initial setup/login. Data dir: {self.user_data_dir}")
        width, height = self._get_dynamic_size()
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,
                channel="chrome",
                args=[
                    f"--window-size={width},{height}",
                    "--disable-blink-features=AutomationControlled"
                ],
                viewport={'width': width, 'height': height},
                ignore_default_args=["--enable-automation"]
            )
            page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()
            # Go directly to login page
            page.goto("https://chatgpt.com/auth/login")
            
            print("Please log in. Close the browser when you are finished.")
            try:
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            browser.close()
            print("Setup finished!")

    def run_automation(self, prompt, attachment_paths):
        print(f"Starting Playwright automation using Google Chrome. Data dir: {self.user_data_dir}")
        width, height = self._get_dynamic_size()
        with sync_playwright() as p:
            # Using channel="chrome" launches your actual Google Chrome browser which 
            # naturally bypasses Cloudflare much better than Chromium.
            browser = p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,
                channel="chrome",
                args=[
                    f"--window-size={width},{height}",
                    "--disable-blink-features=AutomationControlled"
                ],
                viewport={'width': width, 'height': height},
                ignore_default_args=["--enable-automation"]
            )
            
            page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()
            
            page.goto("https://chatgpt.com")
            
            print("Checking if we need to log in manually...")
            try:
                # If we aren't logged in, ChatGPT shows a "Log in" button. 
                # Let's automatically click it to send you straight to the login form!
                login_btn = page.get_by_text("Log in", exact=True)
                if login_btn.is_visible(timeout=2000):
                    print("Found 'Log in' button, clicking it for you...")
                    login_btn.click()
            except Exception:
                pass
                
            try:
                # Wait for the chat box to appear.
                # If you aren't logged in, it will fail after 10s. Use the 'Setup Login' button if so!
                page.wait_for_selector("#prompt-textarea", timeout=10000) 
            except Exception:
                print("Could not find chat input. Did you use the 'Setup Login' button? Exiting automation.")
                browser.close()
                return
                
            print("Chat page is ready! Proceeding with auto-upload...")
            try:
                # Attach files if any exists
                if attachment_paths:
                    # Filter paths that actually exist and make them absolute
                    valid_paths = [os.path.abspath(p) for p in attachment_paths if os.path.exists(p)]
                    if valid_paths:
                        try:
                            # The most robust way to upload files is to inject them directly into the hidden input
                            file_inputs = page.locator('input[type="file"]')
                            if file_inputs.count() > 0:
                                # Try injecting into each available file input until one succeeds
                                uploaded = False
                                for i in range(file_inputs.count()):
                                    try:
                                        file_inputs.nth(i).set_input_files(valid_paths)
                                        uploaded = True
                                        break  # Stop exactly when one accepts it
                                    except Exception:
                                        continue
                                        
                                if not uploaded:
                                    raise Exception("None of the hidden file inputs accepted the files. They might be restricted to specific formats.")
                            else:
                                # Fallback: try clicking paperclip/plus button if input is missing
                                page.locator('[data-testid="composer-plus-btn"], [aria-label="Attach files"], [aria-label="Add files and more"]').first.click()
                                page.wait_for_timeout(1000)
                                
                                # Check if they hit the free tier upload limit
                                upload_limit_msg = page.locator('text=/wait .* to upload again|Get Plus for more uploads/i')
                                if upload_limit_msg.count() > 0:
                                    print("\n🚨 CHATGPT FILE UPLOAD LIMIT REACHED 🚨")
                                    print("You have hit the maximum number of file attachments for your free ChatGPT tier.")
                                    print("The script cannot attach files right now. They will need to be pasted as text or you must wait.\n")
                                    # dismiss the menu
                                    page.keyboard.press("Escape")
                                    raise Exception("ChatGPT Upload Rate Limit Reached.")

                                with page.expect_file_chooser(timeout=5000) as fc_info:
                                    # Click the matching upload text in the popup menu
                                    page.locator('text=/Upload/i').first.click()
                                fc_info.value.set_files(valid_paths)
                                
                            print(f"Successfully uploaded {len(valid_paths)} files.")
                            # Wait slightly longer for uploads to complete before sending
                            time.sleep(6)
                        except Exception as e:
                            print(f"Could not automate file attachment: {e}")
                            print("Please attach files manually if needed.")
                
                # Fill the prompt
                print("Injecting prompt...")
                page.fill("#prompt-textarea", prompt)
                time.sleep(1)
                
                # Send
                # Send button is usually data-testid="send-button"
                try:
                    page.locator('[data-testid="send-button"]').click()
                except Exception:
                    page.keyboard.press("Enter")
                    
            except Exception as e:
                print(f"Error during ChatGPT automation: {e}")
                
            print("Handoff to user! The browser will stay open so you can do your thing.")
            print("Close the browser window when you are done.")
            try:
                # This keeps the python script alive until you manually close the browser tab.
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            
            browser.close()
