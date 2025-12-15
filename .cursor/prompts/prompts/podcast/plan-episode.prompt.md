---
name: plan-episode
description: "Plan a comprehensive cinema podcast episode from topic to research strategy with systematic research framework and production roadmap"
agent: cursor-agent
model: GPT-4
tools:
  - search/web
argument-hint: "Episode topic or film title"
category: podcast
tags: podcast, planning, cinema, research, episode, strategy, framework, production, roadmap, systematic
---

# Plan Cinema Podcast Episode

**Pattern**: Episode Planning Framework | **Effectiveness**: High | **Use When**: Starting a new cinema podcast episode

## Purpose

Create a comprehensive episode plan that transforms a topic into a structured research and production roadmap, ensuring systematic coverage of cinema topics through multiple perspectives and sources.

## Required Context

**Topic Input**: `[EPISODE_TOPIC]` - The main film, director, genre, or cinema concept for this episode

**Episode Format**: `[EPISODE_FORMAT]` - Single film analysis, director retrospective, genre exploration, etc.

**Target Length**: `[TARGET_LENGTH]` - 30-60 minutes typical

## Reasoning Process

1. **Understand Topic Scope**: Break down the topic into researchable components
2. **Identify Perspectives**: Determine what angles (historical, critical, cultural, technical) to cover
3. **Plan Research Strategy**: Map out sources needed for comprehensive coverage
4. **Structure Episode Flow**: Design logical progression from introduction to conclusion

## Process

### Step 1: Topic Analysis
Break down the episode topic into key components:
- **Core Subject**: Main film/director/genre focus
- **Historical Context**: When/where it fits in cinema history
- **Key Themes**: Major concepts or movements represented
- **Controversies**: Debates or critical disagreements
- **Cultural Impact**: Broader influence on cinema/culture

### Step 2: Research Framework
Design a multi-source research approach:

**Primary Sources** (Must Include):
- The film(s) themselves (watch/re-watch)
- Director interviews/documentaries
- Academic/critical analysis
- Historical context materials

**Secondary Sources** (Recommended):
- Audience reception data
- Cultural commentary
- Technical analysis
- Comparative works

### Step 3: Episode Structure Planning
Create a logical flow for `[TARGET_LENGTH]` minutes:

**Opening (10%)**: Hook + Topic Introduction + Thesis
**Body (70%)**: Analysis + Examples + Discussion Points
**Personal Take (10%)**: Your unique perspective/opinion
**Conclusion (10%)**: Summary + Key Takeaways + Teasers

### Step 4: Research Action Plan
Generate specific research tasks:

**YouTube Collection Strategy**:
- Search terms for video content
- Channels/sources to prioritize
- Types of content needed (reviews, analysis, interviews)

**Blog/Critique Collection Strategy**:
- Key publications/websites to search
- Types of articles needed
- Quality criteria for selection

## Expected Output

### Episode Overview
**Title**: [Suggested episode title]
**Runtime**: [TARGET_LENGTH] minutes
**Core Thesis**: [Main argument/perspective]

### Research Roadmap
**Phase 1 - Foundation**:
- Watch/re-watch primary film(s)
- Read basic plot summaries and context
- Identify key themes and techniques

**Phase 2 - Deep Research**:
- Collect YouTube analysis videos
- Gather critical essays and blog posts
- Watch director interviews/documentaries
- Research historical context

**Phase 3 - Synthesis**:
- Analyze collected sources
- Identify patterns and disagreements
- Form personal analysis/opinion
- Structure episode narrative

### Content Outline
**Segment 1**: [Topic] - [Key Points] ([Time Allocation])
**Segment 2**: [Topic] - [Key Points] ([Time Allocation])
**Segment 3**: [Topic] - [Key Points] ([Time Allocation])

### Source Collection Targets
**YouTube Videos**: [Number] videos from [Types of channels]
**Blog Posts**: [Number] articles from [Types of publications]
**Additional Sources**: Books, interviews, etc.

## Usage Modes

### Comprehensive Planning Mode
For complete episode development from concept to production:
```
@plan-episode [EPISODE_TOPIC] --comprehensive --target-length 45

Focus: Full planning framework with research strategy and production roadmap
Time: 90-120 minutes
Output: Complete episode plan with all phases, timelines, and requirements
```

### Research-Focused Mode
For episodes requiring extensive research foundation:
```
@plan-episode [EPISODE_TOPIC] --research-heavy --target-length 60

Focus: Detailed research planning with source collection strategy
Time: 60-90 minutes
Output: Research-optimized plan with comprehensive source requirements
```

### Rapid Planning Mode
For time-constrained episode development:
```
@plan-episode [EPISODE_TOPIC] --rapid --target-length 30

Focus: Essential planning elements for quick episode execution
Time: 45-60 minutes
Output: Streamlined plan for efficient episode production
```

## Troubleshooting & Enhanced Validation

### Planning Challenges
**Scope creep**: Topic expands beyond manageable episode length
**Research overload**: Planning becomes research rather than planning research
**Timeline compression**: Unrealistic expectations for content depth vs. time available
**Angle uncertainty**: Difficulty identifying unique episode perspective

## Quality Criteria

- [ ] Topic broken into researchable components
- [ ] Multi-perspective approach planned
- [ ] Realistic research scope for time available
- [ ] Clear episode structure with time allocations
- [ ] Specific source collection strategy
- [ ] Personal angle identified
- [ ] Production timeline realistic
- [ ] Multiple usage modes support different planning approaches
- [ ] Troubleshooting guidance addresses common planning challenges
- [ ] Enhanced validation ensures systematic episode quality

## Examples

### Example 1: The Godfather Episode Planning

**Input Context**:
- Topic: The Godfather (1972) - Cinematic masterpiece analysis
- Episode Format: Single film deep-dive
- Target Length: 45 minutes
- Audience: Cinema enthusiasts with moderate technical knowledge

**Output Structure**:
```
Episode Overview
Title: "The Godfather: From Novel to Cinematic Masterpiece"
Runtime: 45 minutes
Core Thesis: Coppola's adaptation transcends the source material through visual storytelling that captures the soul of American ambition and corruption

Research Roadmap
Phase 1 - Foundation (2-3 days):
- Watch/re-watch primary film (The Godfather) - 2 hours
- Read Mario Puzo's source novel summary - 1 hour
- Basic historical context: 1970s America, Hollywood landscape - 2 hours
- Identify key themes: Family, power, corruption, American Dream - 1 hour

Phase 2 - Deep Research (4-5 days):
- Collect YouTube analysis videos: 6-8 videos from Film Analysis Academy, Three Movie Buffs, Cinema Scope - 8 hours
- Gather critical essays: 4-5 articles from academic journals, professional reviews - 6 hours
- Watch director interviews: Coppola's commentary and retrospective discussions - 4 hours
- Research technical aspects: Cinematography, editing techniques, sound design - 6 hours

Phase 3 - Synthesis & Personal Development (2-3 days):
- Analyze collected sources for patterns and insights - 4 hours
- Identify critical consensus vs. unique perspectives - 3 hours
- Form personal analysis and unique angle - 4 hours
- Structure episode narrative with smooth transitions - 3 hours
- Develop personal anecdotes and connection points - 2 hours

Content Outline
Segment 1: Historical Context & Opening Hook (10 minutes)
- 1970s America backdrop and cultural anxieties
- Mario Puzo novel origins and initial reception
- Francis Ford Coppola's vision and challenges
- Opening scene impact and revolutionary approach

Segment 2: Cinematic Techniques & Visual Mastery (20 minutes)
- Gordon Willis' groundbreaking cinematography (deep focus, shadows, lighting)
- Directorial choices and scene construction
- Sound design integration and Nino Rota's score
- Editing rhythm and narrative pacing
- Technical innovations that changed Hollywood

Segment 3: Thematic Depth & Character Analysis (10 minutes)
- Michael Corleone's transformation arc
- Family loyalty vs. moral corruption themes
- American Dream critique and capitalist commentary
- Ensemble performances and character authenticity

Segment 4: Cultural Impact & Personal Reflection (5 minutes)
- Lasting influence on cinema and pop culture
- Modern relevance and contemporary connections
- Personal viewing experience and emotional impact
- Final thoughts on why this film endures

Source Collection Targets
YouTube Videos: 7 videos (3 technical analysis, 2 thematic discussion, 2 cultural impact)
Blog Posts: 4 articles (2 academic essays, 2 professional reviews)
Additional Sources: Coppola interviews, behind-the-scenes documentaries
```

### Example 2: Independent Film Episode Planning

**Input Context**:
- Topic: Moonlight (2016) - Identity, representation, and visual storytelling
- Episode Format: Contemporary film analysis with social impact focus
- Target Length: 35 minutes
- Audience: General podcast listeners interested in social issues and film

**Output Structure**:
```
Episode Overview
Title: "Moonlight: Illuminating the Shadows of Identity"
Runtime: 35 minutes
Core Thesis: Barry Jenkins' Moonlight transcends traditional coming-of-age narratives to create a revolutionary exploration of Black queer identity through poetic visual storytelling

Research Roadmap
Phase 1 - Foundation (2 days):
- Watch Moonlight and research Barry Jenkins' background - 3 hours
- Read basic plot summary and awards context - 1 hour
- Understand LGBTQ+ representation in cinema history - 2 hours
- Identify key themes: Identity formation, belonging, masculinity - 1 hour

Phase 2 - Deep Research (3-4 days):
- Collect YouTube analysis: 5-6 videos from film critics and cultural commentators - 6 hours
- Gather written analysis: 3-4 articles on representation and visual style - 4 hours
- Watch Jenkins interviews and director commentary - 3 hours
- Research intersectional themes: Race, sexuality, class in modern cinema - 4 hours

Phase 3 - Synthesis & Personal Development (2 days):
- Synthesize representation analysis with visual technique discussion - 3 hours
- Form personal perspective on film's cultural significance - 2 hours
- Structure accessible narrative for general audience - 3 hours
- Develop connection points for listeners - 2 hours

Content Outline
Segment 1: Introduction & Context (8 minutes)
- Film's premise and initial reception
- Barry Jenkins' background and artistic vision
- Cultural moment: Post-Obama representation discussions
- Opening sequence and visual poetry introduction

Segment 2: Visual Storytelling & Technique (12 minutes)
- Triptych structure and identity formation metaphor
- Water and light symbolism throughout
- Color theory and emotional temperature
- Non-verbal storytelling techniques
- Collaboration with composer Nicholas Britell

Segment 3: Representation & Identity Themes (10 minutes)
- Authentic portrayal of Black queer experience
- Intersectionality: Race, sexuality, and class
- Challenge to traditional masculinity norms
- Community and belonging exploration
- Personal growth through three life stages

Segment 4: Cultural Impact & Reflection (5 minutes)
- Awards success and Oscar significance
- Influence on queer cinema representation
- Modern relevance for identity discussions
- Personal response and emotional resonance

Source Collection Targets
YouTube Videos: 5 videos (2 visual analysis, 2 representation discussion, 1 director interview)
Blog Posts: 3 articles (1 academic analysis, 2 cultural criticism pieces)
Additional Sources: Oscar acceptance speeches, diversity in Hollywood discussions
```

## Success Criteria

✅ Comprehensive research plan created
✅ Episode structure clearly defined
✅ Source collection strategy specific and actionable
✅ Personal perspective angle identified
✅ Timeline realistic for available time

## Related Prompts

- `collect-youtube-sources.prompt.md` - Execute YouTube research phase
- `collect-blog-critiques.prompt.md` - Execute blog/critique research phase
- `analyze-cinema-content.prompt.md` - Begin content analysis phase

## Related Rules

- `.cursor/rules/podcast/content-research-rule.mdc` - Research standards
- `.cursor/rules/podcast/episode-structure-rule.mdc` - Episode planning standards

---

**Goal**: Systematic, well-researched cinema podcast episodes

---

**Created**: 2025-12-13 (Podcast workflow setup)
**Updated**: 2025-12-13 (Initial creation)
**Rule**: `rule.prompts.creation.v1`, `rule.prompts.registry-integration.v1`
