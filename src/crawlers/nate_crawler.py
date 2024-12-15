import os
import hashlib
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.crawlers.base_crawler import BaseCrawler


class NateCrawler(BaseCrawler):
    def __init__(self, db_client):
        super().__init__()
        self.db_client = db_client
        self.collection = self.db_client.db["nate"]

    def fetch_posts(self, keyword, start_page, end_page):
        """
        Fetch posts for a specific keyword (board ID) from Nate Pann.
        """
        base_url = f"https://pann.nate.com/talk/{keyword}?type=3&page="
        for page in range(start_page, end_page + 1):
            print(f"[Nate Pann] Fetching page {page} for keyword {keyword}")
            html = self.get_html(base_url + str(page))
            if html:
                post_links = self.extract_post_links(html)
                print(f"[Nate Pann] Found {len(post_links)} post links on page {page} for keyword {keyword}")
                for link in post_links:
                    self.process_post(link, keyword)

    def extract_post_links(self, html_content):
        """
        Extract post links from a page's HTML content.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        post_links = []
        tbody = soup.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                h2 = tr.find("h2")
                if h2 and (a_tag := h2.find("a", href=True)):
                    post_links.append("https://pann.nate.com" + a_tag["href"])
        return post_links

    def process_post(self, post_url, keyword):
        """
        Process a single post by extracting content and storing it.
        """
        post_id = self.extract_post_id(post_url)
        html = self.get_html(post_url)
        if html:
            post_data = self.extract_post_content(html, post_url, keyword, post_id)
            if post_data:
                self.store_post(post_data)

    def extract_post_id(self, url):
        """
        Extract the post ID from the URL.
        """
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split("/")
        if len(path_parts) > 2:
            return path_parts[-1]  # '373645734' 부분 추출
        return "unknown_id"

    def extract_post_content(self, html_content, url, keyword, post_id):
        """
        Extract the content, media, and comments of a post.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        media = {"images": [], "videos": []}
        comments = []

        def download_media(media_url, folder, index=None):
            """
            Download media file and save it in the specified folder with a unique name.
            """
            os.makedirs(folder, exist_ok=True)  # Ensure the folder exists
            parsed_url = urlparse(media_url)
            filename = os.path.basename(parsed_url.path)  # 기본 파일 이름
            if not filename or filename == "download.jsp":  # 이름이 없거나 download.jsp인 경우
                filename = f"image_{index}.jpg" if index is not None else hashlib.md5(media_url.encode()).hexdigest() + ".jpg"
            elif '.' not in filename:  # 확장자가 없을 경우 기본 확장자로 저장
                filename += ".jpg"
            file_path = os.path.join(folder, filename)

            try:
                response = requests.get(media_url, stream=True)
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"[Nate Pann] Media saved: {file_path}")
                return file_path
            except Exception as e:
                print(f"[Nate Pann] Media download failed: {media_url} -> {e}")
                return None

        # 미디어 폴더 생성
        current_dir = os.path.dirname(os.path.abspath(__file__))
        media_dir = os.path.join(current_dir, f"../../data/nate/{keyword}_{post_id}/")
        images_dir = os.path.join(media_dir, "images")
        videos_dir = os.path.join(media_dir, "videos")

        # 이미지 다운로드
        for index, img_tag in enumerate(soup.select("div[id='contentArea'] img"), start=1):
            if img_url := img_tag.get("src"):
                media_path = download_media(img_url, images_dir, index)
                if media_path:
                    media["images"].append(media_path)

        # 동영상 다운로드
        for index, video_tag in enumerate(soup.select("div[id='contentArea'] video"), start=1):
            if video_url := video_tag.get("src"):
                media_path = download_media(video_url, videos_dir, index)
                if media_path:
                    media["videos"].append(media_path)

        # 댓글 수집
        comment_section = soup.find("div", class_="cmt_best")
        if comment_section:
            for comment_item in comment_section.find_all("dl", class_="cmt_item"):
                try:
                    author = comment_item.select_one("span.nameui").get_text(strip=True)
                    date = comment_item.select_one("dt.beple i").get_text(strip=True)
                    content = comment_item.select_one("dd.usertxt span").get_text(strip=True)
                    comments.append({
                        "author": author,
                        "date": date,
                        "content": content
                    })
                except Exception as e:
                    print(f"[Nate Pann] Error parsing comment: {e}")

        return {
            "title": soup.select_one("div.post-tit-info h1").get_text(strip=True) if soup.select_one("div.post-tit-info h1") else "No Title",
            "content": " ".join(soup.find("div", id="contentArea").stripped_strings) if soup.find("div", id="contentArea") else "No Content",
            "url": url,
            "post_id": post_id,
            "media": media,
            "comments": comments,
            "source": "nate",
            "keyword": keyword,
            "timestamp": datetime.utcnow()
        }

    def store_post(self, post):
        """
        Store post data in MongoDB, avoiding duplicates.
        """
        if not self.collection.find_one({"url": post["url"]}):
            self.collection.insert_one(post)
            print(f"[Nate Pann] Stored post: {post['title']}")
        else:
            print(f"[Nate Pann] Duplicate post skipped: {post['title']}")
