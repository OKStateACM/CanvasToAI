import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request
import certifi

class CanvasBot:
    def __init__(self):
        self.domain = os.getenv("CANVAS_DOMAIN", "").rstrip('/')
        self.token = os.getenv("CANVAS_API_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

    def is_configured(self):
        return bool(self.domain and self.token)

    def get_upcoming_assignments(self):
        """Fetch upcoming/due assignments by iterating over courses."""
        if not self.is_configured():
            print("Canvas domain or token not configured.")
            return []
            
        assignments = []
        try:
            # 1. Get all courses
            courses_url = f"{self.domain}/api/v1/courses"
            courses_resp = requests.get(courses_url, params={'enrollment_state': 'active'}, headers=self.headers)
            courses_resp.raise_for_status()
            courses = courses_resp.json()
            
            # 2. For each course, get upcoming assignments
            for course in courses:
                course_id = course.get('id')
                if not course_id:
                    continue
                
                assign_url = f"{self.domain}/api/v1/courses/{course_id}/assignments"
                assign_resp = requests.get(assign_url, params={'bucket': 'upcoming'}, headers=self.headers)
                
                if assign_resp.status_code == 200:
                    course_assignments = assign_resp.json()
                    for assignment in course_assignments:
                        assignments.append({
                            'id': assignment.get('id'),
                            'name': assignment.get('name'),
                            'course_id': course_id,
                            'due_at': assignment.get('due_at'),
                            'html_url': assignment.get('html_url')
                        })
            return assignments
        except Exception as e:
            print(f"Error fetching Canvas assignments: {e}")
            return []

    def get_assignment_details(self, course_id, assignment_id):
        """Fetch the full description of an assignment."""
        url = f"{self.domain}/api/v1/courses/{course_id}/assignments/{assignment_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching assignment {assignment_id}: {e}")
            return None

    def clean_html(self, html_content):
        """Strip HTML tags to get plain text."""
        if not html_content:
            return ""
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(separator="\n").strip()

    def download_attachments(self, assignment_details, download_dir="downloads"):
        """Downloads files attached to the assignment."""
        assign_id = assignment_details.get('name', 'unknown_assignment')
        target_dir = os.path.join(download_dir, str(assign_id))
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        downloaded_paths = []
        
        # 1. Check for explicit attachments in the API response
        attachments = assignment_details.get('attachments', [])
        for attachment in attachments:
            url = attachment.get('url')
            filename = attachment.get('filename', 'attachment_file')
            filename = "".join(c for c in filename if c.isalnum() or c in " ._-")
            filepath = self._download_file(url, filename, target_dir)
            if filepath:
                downloaded_paths.append(filepath)

        # 2. Extract potential download links from the description HTML
        description = assignment_details.get('description', '')
        if description:
            soup = BeautifulSoup(description, "html.parser")
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # If it's a Canvas file link, it contains /files/ followed by digits
                match = re.search(r'/files/(\d+)', href)
                if match:
                    file_id = match.group(1)
                    # Instead of downloading the HTML wrapper page, we query the Canvas API
                    # for the specific file object to get the real download URL (usually AWS S3)
                    file_api_url = f"{self.domain}/api/v1/files/{file_id}"
                    try:
                        f_resp = requests.get(file_api_url, headers=self.headers)
                        if f_resp.status_code == 200:
                            f_data = f_resp.json()
                            real_dl_url = f_data.get('url')
                            if not real_dl_url:
                                continue
                                
                            filename = f_data.get('display_name') or f_data.get('filename') or a_tag.text.strip()
                            filename = "".join(c for c in filename if c.isalnum() or c in " ._-")
                            if not filename.strip():
                                filename = f"file_{file_id}"
                                
                            filepath = self._download_file(real_dl_url, filename, target_dir)
                            if filepath:
                                downloaded_paths.append(filepath)
                    except Exception as e:
                        print(f"Error fetching metadata for file {file_id}: {e}")

        return downloaded_paths

    def _download_file(self, url, filename, download_dir):
        if not url:
            return None
        filepath = os.path.join(download_dir, filename)
        
        # Check if we already downloaded this file to save time!
        if os.path.exists(filepath):
            print(f"Already grabbed {filename}, skipping download.")
            return filepath
            
        print(f"Downloading {filename}...")
        try:
            # Note: requests automatically strips the Authorization header on cross-domain redirects (e.g., to S3)
            # which is exactly what we want so Amazon doesn't reject it.
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filepath
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None
