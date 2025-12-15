---
name: collect-youtube-sources
description: "Systematically collect and curate YouTube videos for cinema podcast episode research with quality evaluation and thematic optimization"
agent: cursor-agent
model: GPT-4
tools:
  - search/web
argument-hint: "Episode topic and research criteria"
category: podcast
tags: podcast, youtube, research, cinema, sources, curation, quality, evaluation, videos, content
---

# Collect YouTube Sources for Cinema Podcast

**Pattern**: Source Collection Framework | **Effectiveness**: High | **Use When**: Researching cinema topics using YouTube content

## Purpose

Systematically identify, evaluate, and curate high-quality YouTube videos that provide diverse perspectives on cinema topics for comprehensive podcast research.

## Required Context

**Episode Topic**: `[EPISODE_TOPIC]` - The film, director, genre, or concept being researched

**Research Criteria**: `[RESEARCH_CRITERIA]` - Specific angles or questions to address (e.g., "cinematic techniques", "historical context", "cultural impact")

**Target Videos**: `[TARGET_COUNT]` - Number of videos to collect (typically 5-10)

**Quality Standards**: `[QUALITY_LEVEL]` - Basic, Standard, or Premium source quality

## Reasoning Process

1. **Search Strategy Development**: Create comprehensive search terms and channel categories
2. **Quality Assessment Framework**: Establish criteria for video selection
3. **Diversity Planning**: Ensure multiple perspectives and expertise levels
4. **Relevance Filtering**: Focus on content that directly addresses research needs

## Process

### Step 1: Search Strategy Development
Create comprehensive search queries:

**Core Search Terms**:
- `"[EPISODE_TOPIC] analysis"`
- `"[EPISODE_TOPIC] explained"`
- `"[EPISODE_TOPIC] breakdown"`
- `"[EPISODE_TOPIC] cinematic techniques"`

**Advanced Search Combinations**:
- `"[EPISODE_TOPIC] [SPECIFIC_ASPECT]"` (e.g., "Godfather cinematography")
- `"[EPISODE_TOPIC] vs [COMPARISON]"` (e.g., "Godfather vs Goodfellas")
- `"[EPISODE_TOPIC] director commentary"`

### Step 2: Channel Categories & Priority
Identify and prioritize source types:

**Primary Sources (High Priority)**:
- Academic/Film School channels (Criterion, Kanopy)
- Professional film critics (Roger Ebert, etc.)
- Director interviews and behind-the-scenes
- Documentary content

**Secondary Sources (Medium Priority)**:
- Film analysis YouTubers (Three Movie Buffs, Lindsay Ellis)
- Educational content creators
- Film history channels

**Tertiary Sources (Lower Priority)**:
- Fan analyses and reactions
- Casual reviews and opinions

### Step 3: Video Evaluation Criteria
For each potential video, assess:

**Content Quality**:
- Accuracy of information presented
- Depth of analysis provided
- Use of specific examples from the film
- Citation of sources or evidence

**Presentation Quality**:
- Clear audio and video
- Professional editing and pacing
- Visual aids (clips, diagrams, text overlays)
- Speaker credibility and expertise

**Relevance to Episode**:
- Direct relationship to `[EPISODE_TOPIC]`
- Addresses `[RESEARCH_CRITERIA]`
- Provides unique perspective not covered elsewhere

### Step 4: Diversity & Balance
Ensure collected videos provide:

**Perspective Diversity**:
- Academic vs. popular analysis
- Technical vs. thematic focus
- Historical vs. contemporary viewpoints
- Positive vs. critical takes

**Content Type Balance**:
- Full analyses (15+ minutes)
- Short explainers (5-10 minutes)
- Specific technique breakdowns
- Historical context videos

## Expected Output

### Curated Video Collection

**Video 1**
**Title**: [Full video title]
**Channel**: [Creator name and subscriber count]
**Duration**: [Length]
**Why Selected**: [2-3 sentence rationale for inclusion]
**Key Takeaways**: [3-5 main points covered]
**Timestamp Notes**: [Important segments to reference]

**Video 2**
[Same format as above]

### Collection Analysis
**Total Videos**: [COUNT] selected from [TOTAL] reviewed
**Coverage Areas**:
- [AREA 1]: [Videos that cover this]
- [AREA 2]: [Videos that cover this]

**Gaps Identified**: [Topics not well covered by current selection]

**Recommended Additions**: [Suggestions for additional videos if needed]

### Research Notes
**Emerging Patterns**: [Common themes across videos]
**Contradictions**: [Areas where sources disagree]
**Unique Insights**: [Notable perspectives found]

## Usage Modes

### Comprehensive Collection Mode
For thorough video research across all creator types:
```
@collect-youtube-sources [EPISODE_TOPIC] --comprehensive --target-count 8

Focus: Complete collection with diverse perspectives and quality evaluation
Time: 90-120 minutes
Output: Curated video collection with detailed analysis and episode integration
```

### Thematic Focus Mode
For videos addressing specific themes or techniques:
```
@collect-youtube-sources [EPISODE_TOPIC] --theme "cinematography" --target-count 5

Focus: Specialized collection for particular analytical angles
Time: 60-90 minutes
Output: Theme-optimized collection with deep technical insights
```

### Rapid Research Mode
For time-constrained video research needs:
```
@collect-youtube-sources [EPISODE_TOPIC] --rapid --target-count 4

Focus: Quality videos quickly identified and evaluated
Time: 45-60 minutes
Output: Essential video collection for episode foundation
```

## Troubleshooting & Enhanced Validation

### Collection Challenges
**Algorithm bias**: YouTube recommendations may limit perspective diversity
**Quality inconsistency**: Popular videos may not be most analytically rigorous
**Time sensitivity**: Video content changes frequently, timestamps may become invalid
**Creator credibility**: Influencers vs. experts may require different evaluation approaches

## Quality Criteria

- [ ] Minimum [TARGET_COUNT] high-quality videos collected
- [ ] Sources span multiple perspectives and expertise levels
- [ ] All videos directly relevant to [EPISODE_TOPIC]
- [ ] Mix of video lengths and depths
- [ ] Clear rationale provided for each selection
- [ ] Coverage gaps identified and addressed
- [ ] Timestamps noted for key segments
- [ ] Multiple usage modes support different research approaches
- [ ] Troubleshooting guidance addresses common collection challenges
- [ ] Enhanced validation ensures systematic video quality

## Examples

### Example 1: The Godfather Cinematography Research

**Input Criteria**:
- Topic: The Godfather (1972) - Focus on cinematic techniques
- Target Videos: 6 high-quality analysis videos
- Quality Standards: Professional channels with technical expertise
- Research Focus: Cinematography, editing, visual storytelling

**Output Structure**:
```
Curated Video Collection

Video 1
Title: "The Godfather: A Masterclass in Cinematography"
Channel: Film Analysis Academy (150K subscribers)
Duration: 18:45
Why Selected: Comprehensive technical breakdown from established educational channel with strong credibility in film analysis
Key Takeaways: Revolutionary deep focus techniques allowing multiple narrative planes, strategic long takes building tension, masterful shadow and lighting work establishing moral ambiguity
Timestamp Notes: 5:30-8:15 (deep focus examples), 12:00-15:30 (lighting symbolism), 16:00-18:45 (editing philosophy)

Video 2
Title: "Godfather Cinematography Secrets Revealed"
Channel: Cinematic Techniques (89K subscribers)
Duration: 12:20
Why Selected: Focuses specifically on technical execution with concrete examples, complements broader analysis with detailed technique breakdowns
Key Takeaways: Camera movement patterns, lens choice rationale, practical lighting challenges overcome, color theory application
Timestamp Notes: 2:15-5:00 (camera techniques), 7:30-10:15 (lighting challenges), 11:00-12:20 (color symbolism)

Video 3
Title: "The Visual Language of The Godfather - Gordon Willis Interview"
Channel: American Cinematographer (45K subscribers)
Duration: 22:10
Why Selected: Primary source interview with actual cinematographer provides authentic insight into intentional creative choices
Key Takeaways: Willis' approach to visual storytelling, collaboration with Coppola, technical challenges of 1970s production, philosophical approach to lighting design
Timestamp Notes: 3:20-8:45 (lighting philosophy), 12:15-16:30 (Coppola collaboration), 18:00-22:10 (technical innovations)

Video 4
Title: "Editing The Godfather: Rhythm and Pacing"
Channel: Film Editing Pro (67K subscribers)
Duration: 15:35
Why Selected: Specialized focus on editing techniques often overlooked in general analysis, provides technical depth for post-production discussion
Key Takeaways: Sound design integration with cuts, parallel action sequencing, pacing variations for emotional impact, invisible editing techniques
Timestamp Notes: 4:10-7:25 (parallel editing), 9:45-12:00 (sound bridges), 13:15-15:35 (pacing theory)

Video 5
Title: "The Godfather's Opening Scene - Frame by Frame Analysis"
Channel: Frame Analysis (92K subscribers)
Duration: 14:20
Why Selected: Detailed examination of most iconic sequence provides concrete examples for technical discussion, strong educational value
Key Takeaways: Shot composition analysis, symbolic elements in frame, performance timing with camera, establishing shot significance
Timestamp Notes: 1:45-5:10 (shot composition), 7:20-10:35 (symbolic analysis), 11:50-14:20 (performance-camera relationship)

Video 6
Title: "How The Godfather Changed Hollywood Cinematography"
Channel: Cinema History (134K subscribers)
Duration: 16:50
Why Selected: Provides historical context and lasting influence, connects technical analysis to broader cinematic impact
Key Takeaways: Industry-wide adoption of techniques, influence on modern cinematography, technical innovations that became standards
Timestamp Notes: 2:30-6:15 (industry impact), 8:45-12:20 (technique adoption), 14:00-16:50 (modern influence)

Collection Analysis
Total Videos: 6 selected from 15 reviewed
Coverage Areas:
- Technical Cinematography: Videos 1, 2, 3 (camera, lighting, techniques)
- Editing and Post-Production: Video 4 (editing techniques, sound design)
- Scene Analysis: Video 5 (detailed sequence breakdown)
- Historical Impact: Video 6 (industry influence, legacy)

Gaps Identified: Limited coverage of production design and costume analysis, some overlap in basic technique discussion

Recommended Additions: One video on production design, additional content on sound design beyond editing context
```

### Example 2: Independent Film Visual Style Research

**Input Criteria**:
- Topic: Moonlight (2016) - Focus on visual storytelling and symbolism
- Target Videos: 5 analysis videos
- Quality Standards: Mix of professional and specialized analysis
- Research Focus: Visual motifs, color theory, symbolic elements

**Output Structure**:
```
Curated Video Collection

Video 1
Title: "The Visual Poetry of Moonlight: Water, Light, and Identity"
Channel: Indie Film Analysis (78K subscribers)
Duration: 19:30
Why Selected: Comprehensive examination of visual motifs central to the film's themes, strong analytical depth
Key Takeaways: Water symbolism throughout triptych, color temperature changes reflecting emotional states, mirror imagery for identity exploration
Timestamp Notes: 3:15-7:45 (water symbolism), 10:20-14:10 (color theory), 15:50-19:30 (identity motifs)

Video 2
Title: "Barry Jenkins' Cinematography in Moonlight"
Channel: Cinematography Studies (56K subscribers)
Duration: 16:40
Why Selected: Technical focus on Jenkins' directorial vision and collaboration with cinematographer, provides production insight
Key Takeaways: James Laxton's camera work, underwater shooting techniques, lighting design for emotional authenticity
Timestamp Notes: 2:50-6:20 (camera techniques), 8:15-11:30 (lighting approach), 13:00-16:40 (production challenges)

Video 3
Title: "Symbolism in Moonlight - A Complete Guide"
Channel: Film Symbolism (43K subscribers)
Duration: 21:15
Why Selected: Specialized analysis of symbolic elements provides foundation for thematic discussion
Key Takeaways: Recurring motifs (fish, butterflies, wolves), color symbolism (blue/teal vs. warmer tones), architectural symbolism
Timestamp Notes: 4:30-9:15 (animal symbolism), 11:45-15:20 (color symbolism), 17:00-21:15 (architectural metaphors)

Video 4
Title: "Moonlight: The Power of Visual Storytelling"
Channel: Visual Film Analysis (91K subscribers)
Duration: 14:55
Why Selected: Accessible yet sophisticated analysis suitable for podcast audience, good production quality
Key Takeaways: Non-verbal storytelling techniques, visual metaphors for emotional states, triptych structure's visual logic
Timestamp Notes: 2:20-6:00 (non-verbal storytelling), 7:45-10:30 (emotional metaphors), 12:00-14:55 (structure analysis)

Video 5
Title: "Cinematography Breakdown: Moonlight's Most Powerful Scenes"
Channel: Scene Breakdown (67K subscribers)
Duration: 18:20
Why Selected: Practical examples for discussion, scene-by-scene analysis provides concrete reference points
Key Takeaways: Drug deal sequence lighting, beach scene composition, school fight cinematography, final confrontation visuals
Timestamp Notes: 3:40-7:15 (drug deal scene), 9:00-12:25 (beach sequence), 14:10-16:45 (fight scene), 17:00-18:20 (finale analysis)

Collection Analysis
Total Videos: 5 selected from 12 reviewed
Coverage Areas:
- Visual Motifs: Videos 1, 3 (symbolism, recurring imagery)
- Technical Cinematography: Videos 2, 5 (camera work, specific scenes)
- Directorial Vision: Videos 2, 4 (Jenkins' approach, visual storytelling)

Gaps Identified: Limited coverage of editing techniques, minimal discussion of sound design integration
Recommended Additions: Video focused on editing rhythm and pacing, content about score-visual synchronization
```

## Success Criteria

✅ Comprehensive video collection assembled
✅ Quality sources prioritized over quantity
✅ Research gaps clearly identified
✅ Diverse perspectives represented
✅ Specific timestamps noted for reference

## Related Prompts

- `plan-episode.prompt.md` - Initial episode planning
- `collect-blog-critiques.prompt.md` - Collect written analysis sources
- `analyze-cinema-content.prompt.md` - Begin analysis of collected sources

## Related Rules

- `.cursor/rules/podcast/source-quality-rule.mdc` - Source evaluation standards
- `.cursor/rules/podcast/research-diversity-rule.mdc` - Ensuring multiple perspectives

---

**Goal**: High-quality, diverse YouTube research sources for cinema analysis

---

**Created**: 2025-12-13 (Podcast workflow setup)
**Updated**: 2025-12-13 (Initial creation)
**Rule**: `rule.prompts.creation.v1`, `rule.prompts.registry-integration.v1`
