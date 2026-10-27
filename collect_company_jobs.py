
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

# 기업교육 전문강사 모집 검색어
KEYWORDS = [
    "기업교육 프리랜서 강사 모집",
    "신입사원 교육 강사 모집",
    "리더십 소통 CS 강사 모집",
    "기업교육 협력강사 모집",
]

# 교과 교사 채용 등 제외
EXCLUDE = [
    "기간제교사",
    "기간제 교사",
    "초등 정교사",
    "중등 정교사",
]

jobs = []
seen = set()
now = datetime.now(timezone.utc)
recent = now - timedelta(days=30)

for keyword in KEYWORDS:
    params = urllib.parse.urlencode({
        "q": keyword,
        "hl": "ko",
        "gl": "KR",
        "ceid": "KR:ko",
    })
    url = "https://news.google.com/rss/search?" + params

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            root = ET.fromstring(response.read())
        print("RSS 검색 결과 수:", len(root.findall(".//item")), "건 / 검색어:", keyword)
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub_date = item.findtext("pubDate") or ""

            if not title or not link:
                continue

            if not any(word in title for word in ["강사", "강의"]):
                continue

            if not any(word in title for word in ["모집", "채용", "위촉"]):
                continue

            if any(word in title for word in EXCLUDE):
                continue

            try:
                published = parsedate_to_datetime(pub_date)
                if published.astimezone(timezone.utc) < recent:
                    continue
                posted = published.strftime("%Y-%m-%d")
            except (ValueError, TypeError, IndexError):
                continue

            if link in seen:
                continue

            seen.add(link)

            jobs.append({
                "title": title,
                "url": link,
                "agency": "검색 결과 - 원문 확인 필요",
                "region": "",
                "field": "기업교육",
                "posted": posted,
                "deadline": "",
                "type": "company",
                "status": "마감일 확인 필요",
            })

    except Exception as error:
        print("검색 실패:", keyword, error)

jobs.sort(key=lambda x: x["posted"], reverse=True)

with open("company_jobs.json", "w", encoding="utf-8") as file:
    json.dump(jobs, file, ensure_ascii=False, indent=2)

print("기업교육 관련 검색 결과:", len(jobs), "건")
print("company_jobs.json 저장 완료")
