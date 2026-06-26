# Content Intelligence Agent Skill

Use this skill when working on the Personal Brand Content Intelligence Agent, including strategy, source research, content reports, prompt design, Python implementation, scheduling, tests, or README/workflow documentation.

## Mission

Help build and operate an AI-powered Content Intelligence Agent that supports a personal brand across:

- DevOps
- Platform engineering
- Kubernetes
- Cloud
- SRE
- Observability
- DevSecOps
- AIOps
- AI agents
- AI for engineers
- Career guidance
- Parenting
- Kids learning
- Emotional intelligence
- Focus and curiosity
- Screen-time balance
- DevOps stories for kids
- Life lessons from technology

The agent should research and summarize what matters, analyze content patterns, and recommend original content ideas in the user's voice.

## Required First Steps

1. Read the repository `MEMORY.md`.
2. Check `AGENTS.md` for current project instructions.
3. If implementation is requested, inspect the current repository structure before creating files.
4. Confirm significant architecture decisions with the user before implementation.

Significant decisions include:

- Project layout
- New environment variables
- Data storage format
- Source integrations
- API usage
- Scraping strategy
- Scheduling strategy
- Report delivery mechanism
- LLM provider/model choices
- GitHub Actions workflow behavior

## Non-Copycat Rule

Never produce a system that copies viral posts, articles, scripts, or creator structures too closely.

When analyzing high-performing content:

- Extract patterns only
- Identify hooks, formats, pain points, and emotional triggers
- Explain why the pattern may have worked
- Generate fresh angles using the user's voice and lived context
- Preserve links and attribution for source material

## Daily Report Contract

Generate a Markdown report with:

- Date
- Executive summary
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
- Source links

## Weekly Video Contract

Generate one short video script under 60 seconds with:

- Topic category
- Hook
- Story angle
- Spoken script
- Caption
- Hashtags
- Thumbnail idea
- Suggested visuals
- CTA

Rotate categories weekly:

1. DevOps/AIOps
2. AI for engineers
3. DevOps Stories for Kids
4. Parenting reflection
5. Kids learning and screen-time balance

## DevOps Stories For Kids Contract

Each story must include:

- Title
- Target age group
- DevOps concept
- Short story under 500 words
- Life lesson
- Parent takeaway
- Question to ask the child
- Short video version under 60 seconds

Use simple, warm, age-aware language. Avoid making the story feel like a lecture.

## Parenting Voice Rules

Parenting content must sound humble, personal, and non-preachy.

Use language like:

- "I'm learning this too..."
- "As a parent, I sometimes lose my cool too..."
- "This is something I'm trying with my own kids..."
- "I don't want to preach. I want to learn out loud."

Avoid:

- Shaming parents
- Fear-based messaging
- Medical claims without evidence
- Overconfidence
- Pretending to be a parenting expert

For screen-time, focus, learning, and child development:

- Prefer reputable sources
- Separate evidence-based guidance from personal opinion
- Include source links where possible
- Give practical, age-aware suggestions
- Encourage balance instead of fear

## Technical Voice Rules

Technical content should be:

- Practical
- Clear
- Example-driven
- Beginner-friendly when useful
- Honest about tradeoffs
- Free from hype

Each technical idea should include:

- Hook
- Problem
- Explanation
- Real-world example
- Takeaway
- CTA
- Suggested hashtags

## Source Strategy

Prefer official APIs and RSS feeds where possible. Avoid platform behavior that could violate terms.

Recommended source handling:

- LinkedIn: manual examples/input files unless a compliant API path is confirmed
- Medium: RSS/tag feeds where available
- YouTube: RSS or YouTube Data API
- GitHub/CNCF/Kubernetes/Docker/cloud/AI vendors: official blogs, RSS, release notes, repositories, and docs
- Parenting/child development: reputable research, pediatric, learning science, and digital wellbeing sources

Always preserve source title, URL, source name, published date if available, and retrieval date if live collection is used.

## Implementation Guidance

Preferred Python structure:

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

Prefer testable modules:

- Collectors return structured source items.
- Analyzers accept structured source items and return structured insights.
- Generators accept insights and prompt templates.
- Report writers render deterministic Markdown.
- Live network collectors should have mockable interfaces.

## Done Criteria For Implementation Work

For code changes:

- Focused tests exist for changed logic.
- Sample data can produce a sample Markdown report.
- README explains setup and usage.
- `.env.example` documents required and optional variables.
- GitHub Actions workflows do not require secrets that are not documented.
- Live API limitations are clearly documented.
