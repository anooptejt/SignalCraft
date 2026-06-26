import csv
import json
import re
from datetime import datetime
from io import StringIO

from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session

from app.models.domain import CollectedItem, ContentIdea, ContentStatus, PerformanceMetric, PublishedPost, Source


class PersonalContentService:
    def __init__(self, db: Session):
        self.db = db

    def import_linkedin_history(self, raw_text: str) -> list[PublishedPost]:
        rows = self._parse_import_rows(raw_text)
        if not rows:
            raise ValueError("Paste at least one LinkedIn post row as JSON or CSV.")

        self._delete_sample_history()
        imported: list[PublishedPost] = []
        for row in rows:
            title = self._text(row, ["title", "post_title", "headline"]) or "Untitled LinkedIn post"
            content = self._text(row, ["content", "post", "text", "body", "caption"]) or title
            url = self._text(row, ["url", "link", "post_url"]) or f"signalcraft://personal/linkedin/{self._slug(title)}"
            tags = self._tags(row)
            published_at = self._date(row, ["published_at", "date", "created_at"])
            post = self._existing_personal_post(url, title)
            if post:
                post.title = title
                post.content = content
                post.url = url
                post.published_at = published_at
                post.topic_tags = tags
            else:
                post = PublishedPost(
                    platform="linkedin",
                    title=title,
                    url=url,
                    content=content,
                    published_at=published_at,
                    topic_tags=tags,
                )
                self.db.add(post)
                self.db.flush()

            views = self._int(row, ["impressions", "views", "reach"])
            likes = self._int(row, ["likes", "reactions"])
            comments = self._int(row, ["comments"])
            shares = self._int(row, ["shares", "reposts"])
            saves = self._int(row, ["saves"])
            engagement_rate = self._float(row, ["engagement_rate", "engagement"])
            if engagement_rate == 0 and views:
                engagement_rate = round(((likes + comments + shares + saves) / views) * 100, 2)

            self.db.add(
                PerformanceMetric(
                    post_id=post.id,
                    likes=likes,
                    comments=comments,
                    shares=shares,
                    saves=saves,
                    views=views,
                    engagement_rate=engagement_rate,
                )
            )
            imported.append(post)

        self._seed_external_story_patterns()
        self.db.commit()
        return self.top_linkedin_posts(limit=10)

    def seed_linkedin_history(self) -> list[PublishedPost]:
        existing = list(
            self.db.scalars(
                select(PublishedPost)
                .where(PublishedPost.platform == "linkedin")
                .where(PublishedPost.url.like("signalcraft://sample/linkedin/%"))
            )
        )
        if existing:
            return self.top_linkedin_posts(limit=10)

        samples = [
            {
                "slug": "cicd-before-obvious",
                "title": "What CI/CD felt like before it became obvious",
                "content": "I used to think CI/CD was mostly YAML. Then I saw it as a feedback loop that reduces fear before every release.",
                "topic_tags": ["CI/CD", "DevOps", "Beginner Guide"],
                "views": 18400,
                "likes": 420,
                "comments": 58,
                "shares": 37,
                "saves": 91,
                "engagement_rate": 3.29,
            },
            {
                "slug": "ai-agents-approval-gates",
                "title": "AI agents need approval gates, not blind autonomy",
                "content": "The most useful AI agent is not the one that does everything. It is the one that knows when to stop and ask.",
                "topic_tags": ["AI Agents", "HITL", "Platform Engineering"],
                "views": 15120,
                "likes": 390,
                "comments": 64,
                "shares": 42,
                "saves": 103,
                "engagement_rate": 3.96,
            },
            {
                "slug": "kubernetes-school-principal",
                "title": "Kubernetes explained like a school principal",
                "content": "A principal does not teach every class. They make sure every classroom has what it needs and keeps running.",
                "topic_tags": ["Kubernetes", "DevOps Stories for Kids", "Learning"],
                "views": 12680,
                "likes": 310,
                "comments": 44,
                "shares": 28,
                "saves": 76,
                "engagement_rate": 3.61,
            },
            {
                "slug": "parenting-pause",
                "title": "I am learning to pause before correcting",
                "content": "As a parent, I sometimes rush to correct. I am learning that a pause can teach more than a lecture.",
                "topic_tags": ["Parenting", "Learning Out Loud", "Emotional Intelligence"],
                "views": 9700,
                "likes": 260,
                "comments": 39,
                "shares": 14,
                "saves": 65,
                "engagement_rate": 3.9,
            },
        ]

        posts: list[PublishedPost] = []
        for sample in samples:
            post = PublishedPost(
                platform="linkedin",
                title=sample["title"],
                url=f"signalcraft://sample/linkedin/{sample['slug']}",
                content=sample["content"],
                published_at=datetime.utcnow(),
                topic_tags=sample["topic_tags"],
            )
            self.db.add(post)
            self.db.flush()
            self.db.add(
                PerformanceMetric(
                    post_id=post.id,
                    likes=sample["likes"],
                    comments=sample["comments"],
                    shares=sample["shares"],
                    saves=sample["saves"],
                    views=sample["views"],
                    engagement_rate=sample["engagement_rate"],
                )
            )
            posts.append(post)

        self._seed_external_story_patterns()
        self.db.commit()
        return self.top_linkedin_posts(limit=10)

    def top_linkedin_posts(self, limit: int = 5) -> list[PublishedPost]:
        return list(
            self.db.scalars(
                select(PublishedPost)
                .join(PerformanceMetric, PerformanceMetric.post_id == PublishedPost.id)
                .where(PublishedPost.platform == "linkedin")
                .order_by(desc(PerformanceMetric.views), desc(PerformanceMetric.engagement_rate))
                .limit(limit)
            )
        )

    def propose_articles_from_history(self) -> list[ContentIdea]:
        top_posts = self.top_linkedin_posts(limit=3)
        if not top_posts:
            top_posts = self.seed_linkedin_history()[:3]

        proposals: list[ContentIdea] = []
        for post in top_posts:
            metric = self._latest_metric(post.id)
            tags = [str(tag) for tag in (post.topic_tags or [])]
            primary_tag = tags[0] if tags else "personal brand"
            source_pattern = (
                f"Top LinkedIn post: {post.title}. "
                f"Impressions: {metric.views if metric else 0}; comments: {metric.comments if metric else 0}; "
                "reuse the learning-in-public angle, not the wording."
            )
            proposals.append(
                ContentIdea(
                    idea_type="linkedin_article",
                    title=f"From my experience: {primary_tag} without the confusion",
                    hook=self._hook_for_post(post),
                    problem=self._problem_for_tag(primary_tag),
                    angle=self._angle_for_post(post, primary_tag),
                    source_pattern=source_pattern,
                    hashtags=self._hashtags_for_tags(tags),
                    status=ContentStatus.draft,
                )
            )

        self.db.add_all(proposals)
        self.db.commit()
        for proposal in proposals:
            self.db.refresh(proposal)
        return proposals

    def _latest_metric(self, post_id: str) -> PerformanceMetric | None:
        return self.db.scalars(
            select(PerformanceMetric)
            .where(PerformanceMetric.post_id == post_id)
            .order_by(PerformanceMetric.captured_at.desc())
            .limit(1)
        ).first()

    def _delete_sample_history(self) -> None:
        sample_ids = list(
            self.db.scalars(
                select(PublishedPost.id)
                .where(PublishedPost.platform == "linkedin")
                .where(PublishedPost.url.like("signalcraft://sample/linkedin/%"))
            )
        )
        if not sample_ids:
            return
        self.db.execute(delete(PerformanceMetric).where(PerformanceMetric.post_id.in_(sample_ids)))
        self.db.execute(delete(PublishedPost).where(PublishedPost.id.in_(sample_ids)))

    def _parse_import_rows(self, raw_text: str) -> list[dict]:
        text = raw_text.strip()
        if not text:
            return []
        try:
            payload = json.loads(text)
            if isinstance(payload, dict):
                if isinstance(payload.get("posts"), list):
                    return [dict(item) for item in payload["posts"] if isinstance(item, dict)]
                return [payload]
            if isinstance(payload, list):
                return [dict(item) for item in payload if isinstance(item, dict)]
        except json.JSONDecodeError:
            pass

        reader = csv.DictReader(StringIO(text))
        return [dict(row) for row in reader if any((value or "").strip() for value in row.values())]

    def _existing_personal_post(self, url: str, title: str) -> PublishedPost | None:
        post = self.db.scalars(select(PublishedPost).where(PublishedPost.platform == "linkedin").where(PublishedPost.url == url).limit(1)).first()
        if post:
            return post
        return self.db.scalars(
            select(PublishedPost)
            .where(PublishedPost.platform == "linkedin")
            .where(PublishedPost.url.like("signalcraft://personal/linkedin/%"))
            .where(PublishedPost.title == title)
            .limit(1)
        ).first()

    def _text(self, row: dict, keys: list[str]) -> str | None:
        normalized = self._normalized_row(row)
        for key in keys:
            value = normalized.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
        return None

    def _int(self, row: dict, keys: list[str]) -> int:
        value = self._text(row, keys)
        if not value:
            return 0
        digits = re.sub(r"[^0-9]", "", value)
        return int(digits) if digits else 0

    def _float(self, row: dict, keys: list[str]) -> float:
        value = self._text(row, keys)
        if not value:
            return 0
        cleaned = re.sub(r"[^0-9.]", "", value)
        return float(cleaned) if cleaned else 0

    def _date(self, row: dict, keys: list[str]) -> datetime | None:
        value = self._text(row, keys)
        if not value:
            return None
        for date_format in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(value, date_format)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None

    def _tags(self, row: dict) -> list[str]:
        value = self._text(row, ["tags", "topic_tags", "hashtags", "topics"])
        if not value:
            return ["LinkedIn", "PersonalPost"]
        return [tag.strip().strip("#") for tag in re.split(r"[,;|]", value) if tag.strip()]

    def _normalized_row(self, row: dict) -> dict[str, str]:
        return {str(key).strip().lower().replace(" ", "_"): value for key, value in row.items()}

    def _slug(self, title: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        return slug[:80] or "post"

    def _seed_external_story_patterns(self) -> None:
        source = self.db.scalars(select(Source).where(Source.name == "LinkedIn public inspiration patterns").limit(1)).first()
        if not source:
            source = Source(
                name="LinkedIn public inspiration patterns",
                source_type="manual",
                category="external-patterns",
                collection_mode="manual",
            )
            self.db.add(source)
            self.db.flush()

        if self.db.scalar(select(CollectedItem).where(CollectedItem.source_id == source.id).limit(1)):
            return

        self.db.add_all(
            [
                CollectedItem(
                    source_id=source.id,
                    title="Public DevOps story pattern: before and after release anxiety",
                    platform="linkedin_external",
                    summary="Pattern only: relatable before-state, small operational shift, practical takeaway.",
                    raw_text="Do not copy. Extract the format: pain, turning point, practical checklist.",
                    engagement={"impressions": 22000, "comments": 80},
                    metadata_json={"usage": "pattern_only"},
                ),
                CollectedItem(
                    source_id=source.id,
                    title="Public AI agent pattern: autonomy needs boundaries",
                    platform="linkedin_external",
                    summary="Pattern only: challenge hype, show a real guardrail, explain where humans stay involved.",
                    raw_text="Do not copy. Use as a signal for audience concern around trust and control.",
                    engagement={"impressions": 18000, "comments": 65},
                    metadata_json={"usage": "pattern_only"},
                ),
            ]
        )

    def _hook_for_post(self, post: PublishedPost) -> str:
        title = post.title.lower()
        if "ai agent" in title:
            return "The real question is not whether AI agents can act. It is where they should stop."
        if "ci/cd" in title:
            return "CI/CD became easier for me when I stopped seeing it as YAML and started seeing it as confidence."
        if "kubernetes" in title:
            return "Kubernetes finally clicked when I explained it through a simple everyday story."
        if "parent" in " ".join(post.topic_tags or []).lower():
            return "I don't want to preach. I want to learn out loud from one small parenting moment."
        return "One of my best posts worked because it started from confusion, not expertise."

    def _problem_for_tag(self, primary_tag: str) -> str:
        if primary_tag.lower() in {"ci/cd", "devops"}:
            return "Beginners often learn commands before they understand the confidence loop behind delivery."
        if "ai" in primary_tag.lower():
            return "Teams want AI agents, but they do not always know what should remain human-approved."
        if "kubernetes" in primary_tag.lower():
            return "Kubernetes feels abstract until the control loop is explained with a familiar example."
        if "parent" in primary_tag.lower():
            return "Parents need honest reflections that do not shame them or pretend there is one perfect method."
        return "People respond to practical stories that admit the starting confusion."

    def _angle_for_post(self, post: PublishedPost, primary_tag: str) -> str:
        return (
            f"Expand the short post '{post.title}' into a Medium/LinkedIn article with a personal opening, "
            f"a simple explanation of {primary_tag}, one concrete example, and a takeaway for engineers or parents."
        )

    def _hashtags_for_tags(self, tags: list[str]) -> list[str]:
        normalized = [tag.replace("/", "").replace(" ", "") for tag in tags[:3]]
        if "LinkedIn" not in normalized:
            normalized.append("LearningInPublic")
        return normalized[:4]
