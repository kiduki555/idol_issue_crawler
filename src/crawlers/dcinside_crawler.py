import os
import time
import hashlib
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from src.crawlers.base_crawler import BaseCrawler


class DCInsideCrawler(BaseCrawler):
    def __init__(self, db_client):
        super().__init__()
        self.db_client = db_client
        self.collection = self.db_client.db["dcinside"]

        # Configure Selenium for headless mode
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Referer": "https://gall.dcinside.com/",
        }

    def get_selenium_html(self, url):
        """
        Fetch HTML content using Selenium.
        """
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(url)
            time.sleep(3)  # Wait for page to load
            html = driver.page_source
            driver.quit()
            return html
        except Exception as e:
            print(f"[DCInside] Error fetching HTML with Selenium for URL: {url} -> {e}")
            return None

    def fetch_posts(self, gallery_id, max_pages=1):
        """
        Fetch posts from the specified number of pages in a gallery.
        """
        for page in range(1, max_pages + 1):
            url = f"https://gall.dcinside.com/mgallery/board/lists/?id={gallery_id}&page={page}&exception_mode=recommend"
            html = self.get_html(url)
            if html:
                post_urls = self.parse_post_urls(html, gallery_id)
                for post_url in post_urls:
                    post_details = self.parse_post_details(post_url, gallery_id)
                    if post_details:
                        self.store_post(post_details)

    def parse_post_urls(self, html, gallery_id):
        """
        Extract URLs of posts with required conditions and construct the post URLs.
        """
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select("tbody tr.ub-content")
        post_urls = []

        for row in rows:
            category_el = row.select_one(".gall_subject")
            if not category_el or category_el.text.strip() != "일반":
                continue

            # Extract views, recommendations, and comments
            views_text = row.select_one(".gall_count")
            recommend_text = row.select_one(".gall_recommend")
            comments_el = row.select_one(".reply_numbox")

            views = int(views_text.text.strip().replace(",", "")) if views_text and views_text.text.strip().replace(",", "").isdigit() else 0
            recommend = int(recommend_text.text.strip().replace(",", "")) if recommend_text and recommend_text.text.strip().replace(",", "").isdigit() else 0
            comments = int(comments_el.text.strip("[]")) if comments_el and comments_el.text.strip("[]").isdigit() else 0

            # Apply filters
            if views < 500 or recommend < 10 or comments < 5:
                continue

            # Construct post URL using id and no
            post_el = row.select_one(".gall_tit a")
            if post_el:
                post_no = post_el["href"].split("no=")[1].split("&")[0]
                post_url = f"https://gall.dcinside.com/mgallery/board/view/?id={gallery_id}&no={post_no}&exception_mode=recommend"
                post_urls.append(post_url)

        return post_urls

    @staticmethod
    def sanitize_filename(url):
        """
        Sanitize a filename extracted from a URL.
        Use a hash if the filename is invalid or contains query parameters.
        """
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if "?" in filename or "&" in filename or not filename:
            # Use hash for filenames with query parameters or invalid names
            filename = hashlib.md5(url.encode()).hexdigest()
        return filename

    def normalize_url(self, url):
        """
        Normalize a URL to ensure it has a valid scheme.
        """
        if url.startswith("//"):
            return f"https:{url}"  # Add HTTPS scheme
        elif not url.startswith("http"):
            return None  # Skip invalid URLs
        return url

    def download_file(self, url, save_path):
        """
        Download a file from the given URL and save it to the specified path with the correct extension.
        """
        try:
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()

            # Get Content-Type to determine the file extension
            content_type = response.headers.get("Content-Type", "")
            if "image/jpeg" in content_type:
                extension = ".jpg"
            elif "image/png" in content_type:
                extension = ".png"
            elif "image/gif" in content_type:
                extension = ".gif"
            else:
                extension = ".jpg"

            # Sanitize file name and apply extension
            sanitized_filename = self.sanitize_filename(url) + extension
            save_path = os.path.join(os.path.dirname(save_path), sanitized_filename)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save the file
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"[Image Test] Saved file: {save_path}")
            return save_path
        except Exception as e:
            print(f"[Image Test] Error downloading file: {url} -> {e}")
            return None

    def fetch_comments(self, post_id, post_no, page=1):
        """
        Fetch comments from DCInside using a POST request.
        """
        url = "https://gall.dcinside.com/board/comment/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://gall.dcinside.com",
            "Referer": f"https://gall.dcinside.com/mgallery/board/view/?id={post_id}&no={post_no}&exception_mode=recommend&page=1",
            "X-Requested-With": "XMLHttpRequest",
        }

        data = {
            "id": post_id,
            "no": post_no,
            "cmt_id": post_id,
            "cmt_no": post_no,
            "focus_cno": "",
            "focus_pno": "",
            "e_s_n_o": "3eabc219ebdd65fe3eef85e7",  # 업데이트 필요
            "comment_page": page,
            "sort": "",
            "prevCnt": "",
            "board_type": "",
            "_GALLTYPE_": "M",
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()

            json_data = response.json()
            if "comments" in json_data:
                return [
                    {
                        "author": comment.get("name", "Unknown"),
                        "content": comment.get("memo", "No Content"),
                        "date": comment.get("reg_date", "Unknown"),
                    }
                    for comment in json_data["comments"]
                ]
            else:
                print("[DCInside] No comments found in the response.")
                return []
        except requests.exceptions.RequestException as e:
            print(f"[DCInside] Error fetching comments: {e}")
            return []

    def parse_post_details(self, post_url, keyword):
        """
        Fetch detailed content, media (images/videos), and comments.
        """
        html = self.get_selenium_html(post_url)  # Fetch HTML using Selenium
        if not html:
            print(f"[DCInside] Failed to fetch HTML for URL: {post_url}")
            return None

        soup = BeautifulSoup(html, "html.parser")
        try:
            post_no = post_url.split("no=")[1].split("&")[0]
            title_el = soup.select_one(".title_subject")
            title = title_el.text.strip() if title_el else "No Title"

            # Extract views
            views_el = soup.select_one(".gall_count")
            views_text = views_el.text.strip().replace("조회 ", "").replace(",", "") if views_el else "0"
            views = int(views_text) if views_text.isdigit() else 0

            # Extract recommendations
            recommend_el = soup.select_one(".gall_recommend")
            recommend_text = recommend_el.text.strip().replace("추천 ", "").replace(",", "") if recommend_el else "0"
            recommendations = int(recommend_text) if recommend_text.isdigit() else 0

            # Extract content
            content_el = soup.select_one(".writing_view_box")
            content = content_el.text.strip() if content_el else "No Content"

            # Media initialization
            media = {"images": [], "videos": []}

            # Extract images
            image_elements = soup.select(".writing_view_box img")
            if image_elements:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                media_dir = os.path.join(current_dir, f"../../data/dcinside/{keyword}_{post_no}")
                images_dir = os.path.join(media_dir, "images")

                # Ensure directories exist
                os.makedirs(images_dir, exist_ok=True)

                for img_el in image_elements:
                    img_url = img_el["src"]
                    if img_url:
                        image_path = os.path.join(images_dir, self.sanitize_filename(img_url))
                        downloaded_path = self.download_file(img_url, image_path)
                        if downloaded_path:
                            media["images"].append(downloaded_path)

            # Extract videos (if applicable)
            video_elements = soup.select(".writing_view_box video")
            if video_elements:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                media_dir = os.path.join(current_dir, f"../../data/dcinside/{keyword}_{post_no}")
                videos_dir = os.path.join(media_dir, "videos")

                # Ensure directories exist
                os.makedirs(videos_dir, exist_ok=True)

                for video_el in video_elements:
                    video_url = video_el["src"]
                    if video_url:
                        video_path = os.path.join(videos_dir, self.sanitize_filename(video_url))
                        downloaded_path = self.download_file(video_url, video_path)
                        if downloaded_path:
                            media["videos"].append(downloaded_path)

            # Fetch comments
            comments = self.fetch_comments(keyword, post_no)

            return {
                "name": keyword,
                "no": post_no,
                "title": title,
                "views": views,
                "recommendations": recommendations,
                "content": content,
                "media": media,
                "comments": comments,
                "url": post_url,
                "collected_at": datetime.now()
            }
        except Exception as e:
            print(f"[DCInside] Failed to parse post details for URL: {post_url} -> {e}")
            return None

    def store_post(self, post):
        """
        Store a single post in MongoDB.
        """
        if not self.collection.find_one({"url": post["url"]}):
            self.collection.insert_one(post)
            print(f"[DCInside] Stored post: {post['title']}")
        else:
            print(f"[DCInside] Duplicate skipped: {post['title']}")
