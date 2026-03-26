import os
from dotenv import load_dotenv
from canvas_api import CanvasBot
from chatgpt_automation import ChatGPTBot
from gemini_automation import GeminiBot
from app_ui import AppUI

def main():
    load_dotenv()
    
    canvas_bot = CanvasBot()
    chatgpt_bot = ChatGPTBot()
    gemini_bot = GeminiBot()
    
    def on_play_clicked(course_id, assign_id, title, ai_target):
        bot = chatgpt_bot if ai_target == "chatgpt" else gemini_bot
        ai_name = "ChatGPT" if ai_target == "chatgpt" else "Gemini"
        
        print(f"Preparing to ask {ai_name} about: {title}")
        
        # 1. Fetch full details
        details = canvas_bot.get_assignment_details(course_id, assign_id)
        if not details:
            print("Could not fetch details for this assignment.")
            return
            
        # 2. Extract description text
        raw_desc = details.get('description', '')
        clean_text = canvas_bot.clean_html(raw_desc)
        
        # 3. Download attachments
        print("Downloading attachments if any...")
        attachment_paths = canvas_bot.download_attachments(details)
        print(f"Downloaded {len(attachment_paths)} attachments.")
        
        # 4. Construct prompt
        prompt = (
            "Please help me recap topics to solve this!\n\n"
            f"Assignment Title: {title}\n\n"
            "Assignment Description:\n"
            f"{clean_text}\n"
        )
        
        # 5. Run automation
        bot.run_automation(prompt, attachment_paths)
        print("Done handling", title)

    def on_setup_clicked(ai_target):
        if ai_target == "chatgpt":
            print("Opening ChatGPT setup...")
            chatgpt_bot.setup_login()
        else:
            print("Opening Gemini setup...")
            gemini_bot.setup_login()

    app = AppUI(canvas_bot, on_play_clicked, setup_callback=on_setup_clicked)
    app.mainloop()

if __name__ == "__main__":
    main()
