import requests


def fetch_comments_via_post(post_id, post_no, page=1):
    """
    Fetch comments from DCInside using a POST request.
    """
    url = "https://gall.dcinside.com/board/comment/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://gall.dcinside.com",
        "Referer": f"https://gall.dcinside.com/mgallery/board/view/?id={post_id}&no={post_no}&exception_mode=recommend&page=1",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "DNT": "1",
    }

    # 실제 요청 데이터
    data = {
        "id": post_id,
        "no": post_no,
        "cmt_id": post_id,
        "cmt_no": post_no,
        "focus_cno": "",
        "focus_pno": "",
        "e_s_n_o": "3eabc219ebdd65fe3eef85e7",  # e_s_n_o 값이 필요할 경우 업데이트 필요
        "comment_page": page,
        "sort": "",
        "prevCnt": "",
        "board_type": "",
        "_GALLTYPE_": "M",
    }

    # 쿠키 설정 (필요 시)
    cookies = {
        "PHPSESSID": "f8846bfb2032708f463449e609139df3",  # 실제 세션 ID로 교체 필요
        # 기타 쿠키 값 추가
    }

    try:
        response = requests.post(url, headers=headers, data=data, cookies=cookies)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리

        # JSON 데이터 파싱
        json_data = response.json()
        if "comments" in json_data:
            comments = json_data["comments"]
            return [
                {
                    "author": comment.get("name", "Unknown"),
                    "content": comment.get("memo", "No Content"),
                    "date": comment.get("reg_date", "Unknown"),
                }
                for comment in comments
            ]
        else:
            print("No comments found in the response.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching comments: {e}")
        return []


if __name__ == "__main__":
    # 게시판 ID 및 게시글 번호
    post_id = "yoonsy"
    post_no = "62649"

    print(f"Fetching comments for post ID: {post_id}, Post No: {post_no}")
    comments = fetch_comments_via_post(post_id, post_no)

    if comments:
        print("[Comments]")
        for i, comment in enumerate(comments, start=1):
            print(f"{i}. Author: {comment['author']}")
            print(f"   Content: {comment['content']}")
            print(f"   Date: {comment['date']}")
            print()
    else:
        print("[No comments found]")
