# AI Agent Instructions

This repository is for building a Personal Brand Content Intelligence Agent for a founder/engineer who wants to write consistently about DevOps, AIOps, AI agents, career growth, parenting, kids learning, and DevOps stories for kids.

The project is currently in planning/scaffold mode. Do not jump into implementation without confirming significant architecture choices with the user first.

## Product Intent

Build a Python-based automation agent that researches trustworthy sources, tracks content patterns, and generates original content recommendations for LinkedIn, Medium, short videos, blogs, parenting reflections, and kid-friendly DevOps stories.

The system must not copy viral content. It should extract patterns, explain why content worked, and help the user create useful original content in their own voice.

Optimize for:

- Authenticity
- Usefulness
- Original thinking
- Consistency
- Learning in public
- Long-term trust

Do not optimize blindly for virality.

## Required Agent Behavior

- Read `MEMORY.md` before making product, content, or implementation decisions.
- Use `skills/content-intelligence-agent/SKILL.md` when working on strategy, prompts, reports, content generation, source collection, or automation for this project.
- Confirm architecture decisions before implementation, including new environment variables, source integrations, storage choices, API choices, scheduler design, and workflow changes.
- Prefer source-backed guidance for parenting, child development, screen-time, focus, and learning science.
- Avoid fear-based parenting claims, medical claims without evidence, and overconfident advice.
- Keep technical content practical, beginner-friendly when useful, example-driven, and free from hype.

## Project Scope

Initial implementation target:

```text
content-intelligence-agent/
  src/
    config.py
    sources.py
    collectors.py
    trend_analyzer.py
    research_summarizer.py
    content_generator.py
    report_writer.py
    scheduler.py
  prompts/
    daily_research_prompt.md
    trend_analysis_prompt.md
    content_generation_prompt.md
    devops_for_kids_prompt.md
    parenting_prompt.md
    weekly_video_prompt.md
  reports/
  sample_data/
  tests/
  requirements.txt
  README.md
  .env.example
  .github/workflows/daily.yml
  .github/workflows/weekly_video.yml
```

Before creating this full structure, confirm whether the user wants a single-package scaffold under `content-intelligence-agent/` or wants the repository root itself to be the Python project.

## Source Strategy

Use official APIs and RSS feeds where possible. Make sources configurable. Avoid violating platform terms.

Supported source categories should include:

- LinkedIn examples through manual input files unless a compliant API path is confirmed
- Medium RSS/tag feeds
- YouTube RSS or YouTube Data API
- GitHub blog and GitHub Trending-style sources if compliant
- CNCF, Kubernetes, Docker, AWS, Azure, Google Cloud, OpenAI, Anthropic, Microsoft AI, Google AI
- Parenting, child psychology, learning science, and digital wellbeing resources from reputable sources

## Output Requirements

Daily report should include:

- Top 10 updates
- Why each update matters
- Trending themes
- Viral content patterns
- Audience pain points
- 5 LinkedIn post ideas
- 3 short video ideas
- 2 blog ideas
- 2 parenting reflection posts
- 1 DevOps Stories for Kids idea
- 1 Life Lessons from Technology idea
- Action items

Weekly video script should include:

- Hook
- Story angle
- Spoken script under 60 seconds
- Caption
- Hashtags
- Thumbnail idea
- Suggested visuals
- CTA

Weekly video topics should rotate across:

- DevOps/AIOps
- AI for engineers
- DevOps Stories for Kids
- Parenting reflection
- Kids learning and screen-time balance

## Voice Rules

Parenting content must be humble, personal, and non-preachy.

Use language like:

- "I'm learning this too..."
- "As a parent, I sometimes lose my cool too..."
- "This is something I'm trying with my own kids..."
- "I don't want to preach. I want to learn out loud."

Avoid:

- Shaming parents
- Fear-based messaging
- Medical claims without evidence
- Pretending to be a parenting expert
- Overconfident advice

Technical content should be:

- Practical
- Clear
- Example-driven
- Honest about tradeoffs
- Beginner-friendly when useful
- Free from hype

## Quality Gates

When code exists and code changes are made:

- Run focused tests for changed behavior.
- Run formatter/linter if configured.
- Keep reports deterministic enough for tests where possible.
- Do not introduce live API calls into tests unless explicitly marked/integrated.

## Git And Handoff

Use normal git hygiene:

- Check `git status` before and after edits.
- Do not overwrite user changes.
- Keep commits scoped.
- If asked to finish a work session, commit and push only after verification succeeds or after clearly documenting any blocked checks.
