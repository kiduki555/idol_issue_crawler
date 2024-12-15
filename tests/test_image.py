import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from urllib.parse import urlparse
import hashlib


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


def get_html(url):
    """
    Fetch HTML content from a URL with custom headers.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Referer": "https://gall.dcinside.com/",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def download_file(url, save_path):
    """
    Download a file from the given URL and save it to the specified path with the correct extension.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Referer": "https://gall.dcinside.com/",
        }
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Get Content-Type to determine the file extension
        content_type = response.headers.get("Content-Type", "")
        if "image/jpeg" in content_type:
            extension = ".jpg"
        elif "image/png" in content_type:
            extension = ".png"
        elif "image/gif" in content_type:
            extension = ".gif"
        else:
            extension = ".jpg"  # Default: No extension if unknown

        # Sanitize file name and apply extension
        sanitized_filename = sanitize_filename(url) + extension
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


def fetch_images_with_requests(post_url):
    """
    Fetch images using requests and BeautifulSoup.
    """
    try:
        html = get_html(post_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        # Select images
        image_elements = soup.select(".writing_view_box img")
        if not image_elements:
            print(f"[Image Test] No images found in the post: {post_url}")
            return []

        # Prepare directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        post_id = post_url.split("id=")[1].split("&")[0]
        post_no = post_url.split("no=")[1].split("&")[0]
        media_dir = f"data/{post_id}_{post_no}"
        images_dir = os.path.join(current_dir, media_dir, "images")

        # Download images
        downloaded_images = []
        for img_el in image_elements:
            img_url = img_el.get("src")
            if not img_url:
                continue
            image_path = os.path.join(images_dir, sanitize_filename(img_url))
            downloaded_path = download_file(img_url, image_path)
            if downloaded_path:
                downloaded_images.append(downloaded_path)

        return downloaded_images
    except Exception as e:
        print(f"[Image Test] Error fetching images with requests: {e}")
        return []


def fetch_images_with_selenium(post_url):
    """
    Fetch images using Selenium for dynamic content loading.
    """
    try:
        driver = webdriver.Chrome()  # ChromeDriver 설치 필요
        driver.get(post_url)
        time.sleep(3)  # Wait for page to load

        # Select images
        images = driver.find_elements(By.CSS_SELECTOR, ".writing_view_box img")
        downloaded_images = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        post_id = post_url.split("id=")[1].split("&")[0]
        post_no = post_url.split("no=")[1].split("&")[0]
        media_dir = f"data/{post_id}_{post_no}"
        images_dir = os.path.join(current_dir, media_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        for img in images:
            img_url = img.get_attribute("src")
            if not img_url:
                continue
            image_path = os.path.join(images_dir, sanitize_filename(img_url))
            downloaded_path = download_file(img_url, image_path)
            if downloaded_path:
                downloaded_images.append(downloaded_path)

        driver.quit()
        return downloaded_images
    except Exception as e:
        print(f"[Image Test] Error fetching images with Selenium: {e}")
        return []


if __name__ == "__main__":
    # Example post URL
    post_url = "https://gall.dcinside.com/mgallery/board/view/?id=yoonsy&no=62687&exception_mode=recommend&page=1"

    print("[Image Test] Fetching images with requests...")
    images_requests = fetch_images_with_requests(post_url)
    if images_requests:
        print("[Image Test] Downloaded Images with requests:")
        for image in images_requests:
            print(image)
    else:
        print("[Image Test] No images downloaded using requests.")

    print("\n[Image Test] Fetching images with Selenium...")
    images_selenium = fetch_images_with_selenium(post_url)
    if images_selenium:
        print("[Image Test] Downloaded Images with Selenium:")
        for image in images_selenium:
            print(image)
    else:
        print("[Image Test] No images downloaded using Selenium.")
