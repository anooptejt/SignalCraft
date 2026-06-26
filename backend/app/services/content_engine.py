from app.models.domain import CollectedItem, ContentIdea


class ContentEngine:
    def extract_patterns(self, items: list[CollectedItem]) -> list[str]:
        patterns: list[str] = []
        titles = " ".join(item.title.lower() for item in items)
        if "kubernetes" in titles or "platform" in titles:
            patterns.append("Practical infrastructure topics work best when tied to a simple daily workflow.")
        if "ai" in titles or "agent" in titles:
            patterns.append("AI agent content needs concrete workflows and guardrails to avoid hype.")
        if "parent" in titles or "screen" in titles:
            patterns.append("Parenting posts should lead with humility and one practical experiment.")
        if not patterns:
            patterns.append("Beginner-friendly explanations with a clear before/after example are reusable.")
        return patterns

    def generate_ideas(self, patterns: list[str]) -> list[ContentIdea]:
        ideas = [
            ContentIdea(
                idea_type="linkedin",
                title="What CI/CD feels like before it becomes obvious",
                hook="CI/CD is not just automation. It is a calmer way to ship changes.",
                problem="Beginners often see pipelines as YAML instead of a feedback loop.",
                angle="Explain CI/CD through the journey from manual deploy anxiety to repeatable releases.",
                source_pattern=patterns[0],
                hashtags=["DevOps", "CICD", "SoftwareEngineering"],
            ),
            ContentIdea(
                idea_type="short_video",
                title="Kubernetes as a school principal",
                hook="Imagine a school where every classroom has exactly the help it needs.",
                problem="Kubernetes feels abstract to beginners and kids.",
                angle="Use a school principal story to explain scheduling and desired state.",
                source_pattern="DevOps Stories for Kids",
                hashtags=["Kubernetes", "DevOpsForKids", "Learning"],
            ),
            ContentIdea(
                idea_type="parenting_reflection",
                title="I am learning to pause before correcting",
                hook="As a parent, I sometimes lose my cool too.",
                problem="Parents need honest, non-shaming reflections around patience.",
                angle="Share one small pause habit and separate personal experience from advice.",
                source_pattern="Humble parenting voice",
                hashtags=["Parenting", "MindfulParenting", "LearningOutLoud"],
            ),
        ]
        return ideas

    def build_report(self, items: list[CollectedItem], patterns: list[str], ideas: list[ContentIdea]) -> str:
        lines = [
            "# SignalCraft Daily Content Intelligence",
            "",
            "## Executive Summary",
            "Today focuses on turning noisy signals into practical, original content ideas across engineering and parenting.",
            "",
            "## Top Updates",
        ]
        for index, item in enumerate(items[:10], start=1):
            source = item.platform or "source"
            lines.append(f"{index}. **{item.title}** ({source})")
            if item.url:
                lines.append(f"   - Source: {item.url}")
            lines.append("   - Why it matters: This can become a simple, useful explanation or reflection for your audience.")

        lines.extend(["", "## Trending Patterns"])
        lines.extend(f"- {pattern}" for pattern in patterns)

        lines.extend(["", "## Content Ideas"])
        for idea in ideas:
            lines.append(f"- **{idea.title}** [{idea.idea_type}]: {idea.hook}")

        lines.extend(
            [
                "",
                "## Action Items",
                "- Pick one LinkedIn idea and draft it in your own voice.",
                "- Add 3-5 LinkedIn examples manually for stronger pattern analysis.",
                "- Record one short DevOps Stories for Kids concept this week.",
            ]
        )
        return "\n".join(lines)
