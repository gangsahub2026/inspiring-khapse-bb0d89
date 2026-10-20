import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

SOURCE = "https://www.gen.go.kr/xboard/board.php?mode=list&tbnum=32"

KEYWORDS = [
    "강사", "진로", "인성교육", "집단상담",
    "학교폭력", "청렴", "인권", "리더십",
    "소통", "CS"
]

EXCLUDE = ["기간제교사", "기간제 교사"]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.href = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")

    def handle_data(self, data):
        title = data.strip()
        if self.href and title:
            self.links.append((title, self.href))

    def handle_endtag(self, tag):
        if tag == "a":
            self.href = None


def main():
    request = urllib.request.Request(
        SOURCE,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", errors="replace")

    parser = LinkParser()
    parser.feed(html)

    print("강사허브 모집공고 수집 시험")

    for title, link in parser.links:
        if any(word in title for word in KEYWORDS):
            if not any(word in title for word in EXCLUDE):
                print(title)
                print(urljoin(SOURCE, link))
                print("---")


if __name__ == "__main__":
    main()
