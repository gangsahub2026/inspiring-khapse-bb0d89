import json
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, parse_qs

SOURCE = "https://www.gen.go.kr/xboard/board.php?mode=list&tbnum=32"

KEYWORDS = [
    "강사", "진로", "인성교육", "집단상담",
    "청렴", "인권", "리더십", "소통", "CS"
]

EXCLUDE = ["기간제교사", "기간제 교사", "학원"]

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.href = None
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.text_parts = []

    def handle_data(self, data):
        if self.href is not None:
            self.text_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            title = " ".join(" ".join(self.text_parts).split())
            if title:
                self.links.append((title, self.href))
            self.href = None
            self.text_parts = []

def main():
    request = urllib.request.Request(
        SOURCE,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", errors="replace")

    parser = LinkParser()
    parser.feed(html)

    jobs = []
    seen = set()

    for title, link in parser.links:
        url = urljoin(SOURCE, link)
        params = parse_qs(urlparse(url).query)

        # 실제 게시글 링크만 수집
        if params.get("mode") != ["view"]:
            continue

        if "number" not in params:
            continue

        if not any(word in title for word in KEYWORDS):
                        continue
            
        if any(word in title for word in EXCLUDE):
                        continue

        if url in seen:
            continue

        seen.add(url)
        jobs.append({
            "title": title,
            "url": url,
            "source": "광주광역시교육청",
            "status": "확인 필요"
        })

    with open("jobs.json", "w", encoding="utf-8") as file:
        json.dump(jobs, file, ensure_ascii=False, indent=2)
    print(f"수집된 모집공고: {len(jobs)}건")
    print("jobs.json 저장 완료")
if __name__ == "__main__":
    main()

    

        

        

        

        
            
