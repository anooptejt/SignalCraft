from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.domain import CollectedItem, ContentIdea, ContentStatus, PerformanceMetric, PublishedPost, Source


class PersonalContentService:
    def __init__(self, db: Session):
        self.db = db

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
