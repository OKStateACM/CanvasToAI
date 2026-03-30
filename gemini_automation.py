from playwright.sync_api import sync_playwright
import os
import time
import re
import tkinter as tk

class GeminiBot:
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
        print(f"Opening Gemini for initial setup/login. Data dir: {self.user_data_dir}")
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
            
            # Go directly to Gemini
            page.goto("https://gemini.google.com/app")
            
            print("Please log in to your Google Account if required. Close the browser when you are finished.")
            try:
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            browser.close()
            print("Gemini Setup finished!")

    def run_automation(self, prompt, attachment_paths):
        print(f"Starting Playwright automation for Gemini. Data dir: {self.user_data_dir}")
        width, height = self._get_dynamic_size()
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,
                channel="chrome",
                args=[
                    f"--window-size={width},{height}",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=Translate",
                    "--lang=es-ES"
                ],
                viewport={'width': width, 'height': height},
                ignore_default_args=["--enable-automation"]
            )
            
            page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()
            
            # Set extra headers for consistency if needed
            page.set_extra_http_headers({"Accept-Language": "es-ES,es;q=0.9"})
            
            page.goto("https://gemini.google.com/app")
            
            print("Waiting for chat page to be ready...")
            try:
                # Wait for the chat input box (Gemini usually uses a contenteditable div or rich-textarea)
                page.wait_for_selector('div[contenteditable="true"]', timeout=10000) 
            except Exception:
                print("Could not find chat input. Did you use the 'Setup Gemini Login' button? Exiting automation.")
                browser.close()
                return
                
            print("Gemini Chat page is ready! Proceeding with auto-upload...")
            try:
                
                # Attach files if any exist
                if attachment_paths:
                    valid_paths = [os.path.abspath(p) for p in attachment_paths if os.path.exists(p)]
                    if valid_paths:
                        try:
                            print(f"Attempting to upload {len(valid_paths)} files...")
                                
                            # Robust attempt to find the upload trigger (the plus button)
                            # We'll try multiple times and multiple selectors
                            upload_trigger = None
                            for attempt in range(4):
                                # Selector ordered from most specific to more general
                                selectors = [
                                    'button[aria-controls="upload-file-menu"]',
                                    'uploader button',
                                    '.upload-card-button',
                                    'button:has(mat-icon[data-mat-icon-name="add_2"])',
                                    'button:has(mat-icon:has-text("add_2"))',
                                    'button[aria-label*="subir" i]',
                                    'button[aria-label*="añadir" i]',
                                    'button[aria-label*="add" i]',
                                    'button[aria-label*="upload" i]'
                                ]
                                
                                for selector in selectors:
                                    trigger = page.locator(selector).first
                                    if trigger.count() > 0 and trigger.is_visible():
                                        upload_trigger = trigger
                                        break
                                
                                if upload_trigger:
                                    break
                                
                                print(f"Upload button not found (attempt {attempt+1}/4). Waiting...")
                                page.wait_for_timeout(1500)
                            
                            if upload_trigger:
                                print(f"Found upload trigger button using selector: {upload_trigger}. Clicking...")
                                upload_trigger.click()
                                page.wait_for_timeout(2000) # Wait for menu animation
                                
                                # Try to find the "Upload from computer" / "Subir desde este ordenador" menu item
                                # We check multiple common labels and roles
                                menu_selectors = [
                                    'button[data-test-id="local-images-files-uploader-button"]',
                                    'button:has(mat-icon[fonticon="attach_file"])',
                                    'button:has(mat-icon[data-mat-icon-name="attach_file"])',
                                    'button[role="menuitem"]:has-text("Subir archivos")',
                                    'button[role="menuitem"]:has-text("Subir desde este ordenador")',
                                    'button[role="menuitem"]:has-text("Upload from computer")',
                                    'button[role="menuitem"]:has-text("Subir desde tu computadora")',
                                    '[role="menuitem"] mat-label:has-text("Subir desde")',
                                    '[role="menuitem"]:has(mat-icon:has-text("upload"))',
                                    'text=/Upload from computer/i',
                                    'text=/Subir desde este ordenador/i',
                                    'text=/Subir desde tu computadora/i'
                                ]
                                
                                menu_item = None
                                for selector in menu_selectors:
                                    item = page.locator(selector).first
                                    if item.count() > 0 and item.is_visible():
                                        menu_item = item
                                        break
                                
                                if not menu_item:
                                    # Fallback searching by aria-label regex
                                    menu_item = page.get_by_label(re.compile(r"Upload from computer|Subir desde.*ordenador|Subir desde.*computadora|Your computer", re.I)).first

                                try:
                                    if menu_item and menu_item.count() > 0 and menu_item.is_visible():
                                        print("Found menu item for local upload. Clicking...")
                                        with page.expect_file_chooser(timeout=10000) as fc_info:
                                            menu_item.click()
                                        fc_info.value.set_files(valid_paths)
                                    else:
                                        # If the menu didn't appear as expected, try the hidden buttons observed in the HTML
                                        print("Menu item not found or not visible. Trying hidden upload buttons fallback...")
                                        page.keyboard.press("Escape") # Close any open menu
                                        page.wait_for_timeout(500)
                                        
                                        # Target the specific hidden buttons from geminiHome.html
                                        hidden_selector = 'button[data-test-id="hidden-local-file-upload-button"], .hidden-local-file-upload-button'
                                        hidden_btn = page.locator(hidden_selector).first
                                        
                                        if hidden_btn.count() > 0:
                                            print("Found hidden local file upload button. Triggering...")
                                            with page.expect_file_chooser(timeout=10000) as fc_info:
                                                hidden_btn.click(force=True)
                                            fc_info.value.set_files(valid_paths)
                                        else:
                                            # Last resort: try clicking the trigger itself again with file chooser expectation
                                            print("Hidden button not found. Trying direct click on trigger as last resort...")
                                            with page.expect_file_chooser(timeout=7000) as fc_info:
                                                upload_trigger.click()
                                            fc_info.value.set_files(valid_paths)
                                except Exception as e:
                                    print(f"File chooser failed to trigger: {e}")
                            else:
                                print("Could not find the attach button (plus button) on the Gemini interface after multiple attempts.")
                            
                            # Wait for uploads to complete
                            print(f"Successfully processed {len(valid_paths)} files.")
                            time.sleep(6)
                              
                        except Exception as e:
                            print(f"Could not automate file attachment: {e}")
                            print("Please attach files manually if needed.")
            
                # Fill the prompt
                print("Injecting prompt...")
                chat_box = page.locator('div[contenteditable="true"]').first
                chat_box.click()
                page.keyboard.insert_text(prompt)
                time.sleep(1)
                
                # Send
                page.keyboard.press("Enter")
                    
            except Exception as e:
                print(f"Error during Gemini automation: {e}")
                
            print("Handoff to user! The browser will stay open so you can read the response.")
            print("Close the browser window when you are done.")
            try:
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            
            browser.close()
