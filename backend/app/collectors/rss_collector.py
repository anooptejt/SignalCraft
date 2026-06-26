import feedparser


def collect_rss(url: str, limit: int = 10) -> list[dict]:
    feed = feedparser.parse(url)
    items: list[dict] = []
    for entry in feed.entries[:limit]:
        items.append(
            {
                "title": entry.get("title", "Untitled"),
                "platform": "rss",
                "url": entry.get("link"),
                "author": entry.get("author"),
                "summary": entry.get("summary"),
                "raw_text": entry.get("summary"),
                "metadata_json": {"feed": feed.feed.get("title", url)},
            }
        )
    return items
