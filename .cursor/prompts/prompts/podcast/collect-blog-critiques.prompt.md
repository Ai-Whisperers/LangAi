---
name: collect-blog-critiques
description: "Collect and curate blog posts, essays, and critical analysis for cinema podcast research with systematic source evaluation and quality filtering"
agent: cursor-agent
model: GPT-4
tools:
  - search/web
argument-hint: "Episode topic and written analysis needs"
category: podcast
tags: podcast, blogs, critiques, research, cinema, analysis, sources, curation, quality, evaluation
---

# Collect Blog Posts and Critiques for Cinema Podcast

**Pattern**: Written Analysis Collection | **Effectiveness**: High | **Use When**: Gathering critical essays and blog analysis for cinema topics

## Purpose

Systematically collect, evaluate, and organize written analysis from blogs, critical essays, and film journalism to provide depth and scholarly perspective for cinema podcast episodes.

## Required Context

**Episode Topic**: `[EPISODE_TOPIC]` - The film, director, genre, or concept being researched

**Analysis Types Needed**: `[ANALYSIS_TYPES]` - Academic essays, professional reviews, cultural criticism, technical analysis, etc.

**Target Articles**: `[TARGET_COUNT]` - Number of articles to collect (typically 3-8)

**Publication Quality**: `[QUALITY_LEVEL]` - Academic, Professional, or General interest publications

## Reasoning Process

1. **Publication Hierarchy**: Identify credible sources by reputation and expertise
2. **Content Type Matching**: Match analysis types to episode research needs
3. **Depth Assessment**: Evaluate analytical depth vs. surface-level content
4. **Perspective Diversity**: Ensure range of critical viewpoints

## Process

### Step 1: Source Hierarchy Identification
Categorize publications by credibility and focus:

**Tier 1 - Academic/Scholarly (Highest Priority)**:
- Film Quarterly, Cinema Journal
- Academic journals and university publications
- Scholarly collections and anthologies

**Tier 2 - Professional Criticism (High Priority)**:
- The New York Times, The Guardian film sections
- Roger Ebert, The Criterion Collection essays
- Professional film critics and publications

**Tier 3 - Specialized Analysis (Medium Priority)**:
- Film analysis blogs (The Dissolve, MUBI Notebook)
- Technical analysis sites (American Cinematographer)
- Genre-specific publications

**Tier 4 - Cultural Commentary (Lower Priority)**:
- General interest blogs and essays
- Cultural analysis pieces
- Fan criticism and cultural impact discussions

### Step 2: Search Strategy Development
Create targeted search approaches:

**Academic Search Terms**:
- `"[EPISODE_TOPIC] film analysis scholarly"`
- `"[EPISODE_TOPIC] cinematic techniques academic"`
- `"[EPISODE_TOPIC] critical theory"`

**Professional Search Terms**:
- `"[EPISODE_TOPIC] review analysis"`
- `"[EPISODE_TOPIC] director analysis"`
- `"[EPISODE_TOPIC] cultural impact"`

**Blog/Essay Search Terms**:
- `"[EPISODE_TOPIC] deep analysis"`
- `"[EPISODE_TOPIC] essay"`
- `"[EPISODE_TOPIC] critique"`

### Step 3: Content Evaluation Framework
For each article, assess:

**Scholarly Rigor**:
- Use of film theory and terminology
- Citation of sources and references
- Engagement with existing scholarship
- Original analysis vs. summary

**Analytical Depth**:
- Specific scene analysis with timestamps
- Technical discussion (cinematography, editing, sound)
- Thematic exploration beyond plot summary
- Historical/cultural context provided

**Writing Quality**:
- Clear, articulate prose
- Logical argument structure
- Evidence-based claims
- Absence of grammatical/spelling errors

### Step 4: Content Type Balance
Ensure collection covers needed analysis types:

**Required Analysis Types**:
- **Formal Analysis**: Cinematography, editing, mise-en-scène
- **Thematic Analysis**: Deeper meanings, symbolism, motifs
- **Contextual Analysis**: Historical, cultural, biographical
- **Comparative Analysis**: Relationships to other works
- **Reception Analysis**: Critical and audience responses

## Expected Output

### Curated Article Collection

**Article 1**
**Title**: [Full article title]
**Author**: [Author name and credentials]
**Publication**: [Publication name and type]
**Date**: [Publication date]
**URL**: [Direct link]
**Why Selected**: [2-3 sentence rationale for inclusion]
**Key Arguments**: [3-5 main analytical points]
**Relevance to Episode**: [How it addresses episode research needs]

**Article 2**
[Same format as above]

### Collection Analysis
**Total Articles**: [COUNT] selected from [TOTAL] reviewed
**Analysis Types Covered**:
- Formal Analysis: [Articles that provide this]
- Thematic Analysis: [Articles that provide this]
- Contextual Analysis: [Articles that provide this]

**Publication Distribution**:
- Academic: [Count]
- Professional Criticism: [Count]
- Specialized Analysis: [Count]

**Perspective Range**: [Conservative to radical viewpoints represented]

### Research Synthesis Notes
**Major Critical Debates**: [Areas where critics disagree]
**Emerging Consensus**: [Points most critics agree on]
**Unique Interpretations**: [Notable minority viewpoints]

## Usage Modes

### Comprehensive Collection Mode
For thorough research across all publication tiers:
```
@collect-blog-critiques [EPISODE_TOPIC] --comprehensive --target-count 6

Focus: Complete collection with quality evaluation and thematic balance
Time: 90-120 minutes
Output: Curated collection with detailed analysis and episode integration
```

### Targeted Analysis Mode
For specific analysis types or perspectives:
```
@collect-blog-critiques [EPISODE_TOPIC] --analysis-type "technical" --target-count 4

Focus: Specialized collection for particular analytical needs
Time: 60-90 minutes
Output: Focused collection optimized for specific episode requirements
```

### Rapid Research Mode
For time-constrained research needs:
```
@collect-blog-critiques [EPISODE_TOPIC] --rapid --target-count 3

Focus: Quality sources quickly identified and evaluated
Time: 45-60 minutes
Output: Essential collection with core insights for episode foundation
```

## Troubleshooting & Enhanced Validation

### Collection Challenges
**Limited sources available**: Use broader search terms, include adjacent topics
**Quality vs. quantity tension**: Prioritize 3 excellent sources over 8 mediocre ones
**Date relevance issues**: Note when older sources provide unique historical perspective
**Accessibility concerns**: Balance academic depth with audience-appropriate sources

## Quality Criteria

- [ ] Minimum [TARGET_COUNT] quality articles collected
- [ ] Sources from multiple credibility tiers
- [ ] All required analysis types represented
- [ ] Clear relevance to [EPISODE_TOPIC] established
- [ ] Publication dates noted for currency assessment
- [ ] Key arguments summarized for each article
- [ ] Balance between depth and accessibility
- [ ] Multiple usage modes support different research approaches
- [ ] Troubleshooting guidance addresses common collection challenges
- [ ] Enhanced validation ensures systematic source quality

## Examples

### Example 1: The Godfather Critical Analysis Collection

**Input Requirements**:
- Topic: The Godfather (1972)
- Analysis Types: Academic essays, professional reviews, cultural criticism
- Target Articles: 5 high-quality sources
- Quality Level: Professional to academic publications

**Output Structure**:
```
Curated Article Collection

Article 1
Title: "The Godfather and the American Dream: A Cinematic Deconstruction"
Author: Dr. Maria Sanchez (Film Studies, UCLA)
Publication: Cinema Journal (Academic)
Date: March 2018
URL: https://cinemajournal.example.com/godfather-analysis
Why Selected: Provides deep thematic analysis of American Dream motifs with strong theoretical framework
Key Arguments: Corruption as inevitable consequence of capitalist pursuit, family structure as microcosm of American society, Michael's transformation as loss of innocence
Relevance to Episode: Perfect foundation for thematic discussion, offers scholarly perspective on core episode questions

Article 2
Title: "Visual Style and Thematic Unity in Francis Ford Coppola's The Godfather"
Author: James Parker (Film Critic)
Publication: The New York Times (Professional)
Date: January 2022 (reprint of 1973 review)
URL: https://nytimes.com/godfather-visual-analysis
Why Selected: Contemporary professional review offering historical perspective on groundbreaking cinematography
Key Arguments: Revolutionary use of deep focus and long takes, integration of visual style with character psychology, influence on modern filmmaking
Relevance to Episode: Essential for technical analysis segment, provides credible professional perspective

Article 3
Title: "The Godfather: From Novel to Cinematic Masterpiece"
Author: Prof. Robert Thompson (Film History, University of Virginia)
Publication: Film Quarterly (Academic)
Date: Summer 2019
URL: https://filmquarterly.org/godfather-adaptation-analysis
Why Selected: Scholarly examination of adaptation process and directorial decisions
Key Arguments: Coppola's transformative adaptation choices, casting methodology, script development process, balance of commercial and artistic elements
Relevance to Episode: Addresses production context and creative decisions, valuable for behind-the-scenes discussion

Article 4
Title: "Cultural Impact: How The Godfather Reshaped American Cinema"
Author: Sarah Chen (Cultural Studies)
Publication: Cineaste Magazine (Specialized)
Date: Fall 2021
URL: https://cineaste.com/godfather-cultural-impact
Why Selected: Analysis of broader cultural significance and legacy
Key Arguments: Transformation of gangster genre, influence on subsequent crime films, reflection of 1970s American anxieties, lasting cultural resonance
Relevance to Episode: Provides context for modern relevance discussion, connects film to broader cinematic landscape

Article 5
Title: "Ensemble Performance and Character Development in The Godfather"
Author: Michael Rowe (Film Critic)
Publication: The Guardian (Professional)
Date: March 2022
URL: https://theguardian.com/godfather-ensemble-analysis
Why Selected: Focus on acting and character work that sets the film apart
Key Arguments: Brando's revolutionary performance approach, supporting cast depth, character arc complexity, naturalistic acting style
Relevance to Episode: Essential for performance analysis, offers accessible yet insightful perspective

Collection Analysis
Total Articles: 5 selected from 12 reviewed
Analysis Types Covered:
- Formal Analysis: Articles 2, 5 (cinematography, performance)
- Thematic Analysis: Articles 1, 4 (cultural themes, American Dream)
- Contextual Analysis: Articles 3, 4 (historical context, cultural impact)
- Comparative Analysis: Articles 1, 4 (relationship to American culture/cinema)

Publication Distribution:
- Academic: 2 (Film Quarterly, Cinema Journal)
- Professional Criticism: 2 (New York Times, The Guardian)
- Specialized Analysis: 1 (Cineaste Magazine)

Perspective Range: Conservative formalist analysis to progressive cultural critique
```

### Example 2: Independent Film Collection

**Input Requirements**:
- Topic: Moonlight (2016)
- Analysis Types: Cultural criticism, representation analysis, directorial studies
- Target Articles: 4 sources
- Quality Level: Professional publications with academic elements

**Output Structure**:
```
Curated Article Collection

Article 1
Title: "Moonlight: A New Standard for Queer Representation in Cinema"
Author: Dr. Jordan Williams (Queer Media Studies, NYU)
Publication: GLQ: A Journal of Lesbian and Gay Studies (Academic)
Date: May 2018
URL: https://glq.dukejournals.org/moonlight-representation
Why Selected: Scholarly analysis of LGBTQ+ representation and cultural significance
Key Arguments: Authentic portrayal of Black queer experience, intersectional approach to identity, cultural impact on queer cinema standards
Relevance to Episode: Foundation for representation discussion, academic credibility

Article 2
Title: "The Visual Poetry of Moonlight: Barry Jenkins' Cinematic Language"
Author: Emily Sanders (Film Critic)
Publication: RogerEbert.com (Professional)
Date: February 2017
URL: https://rogerebert.com/moonlight-visual-analysis
Why Selected: Detailed technical analysis from respected film critic
Key Arguments: Water symbolism, color theory, triptych structure, musical-visual integration
Relevance to Episode: Essential for visual analysis segment, accessible yet sophisticated

Article 3
Title: "Moonlight and the Politics of Respectability"
Author: Prof. Amanda Johnson (African American Studies)
Publication: Black Camera (Academic)
Date: Fall 2017
URL: https://blackcamera.iu.edu/moonlight-respectability
Why Selected: Intersectional analysis of race, sexuality, and class representation
Key Arguments: Challenge to respectability politics, authentic depiction of Black queer life, cultural specificity vs. universal appeal
Relevance to Episode: Adds depth to representation discussion, addresses complex social dynamics

Article 4
Title: "From Autobiography to Art: Barry Jenkins' Personal Vision"
Author: Richard Brody (Film Critic)
Publication: The New Yorker (Professional)
Date: February 2017
URL: https://newyorker.com/jenkins-moonlight-autobiography
Why Selected: Director-focused analysis with personal context
Key Arguments: Jenkins' autobiographical elements, artistic development, collaboration process, personal themes of identity and belonging
Relevance to Episode: Provides director insight, connects personal experience to universal themes

Collection Analysis
Total Articles: 4 selected from 8 reviewed
Analysis Types Covered:
- Representation Analysis: Articles 1, 3 (LGBTQ+ and racial representation)
- Formal Analysis: Article 2 (visual and technical elements)
- Contextual Analysis: Articles 1, 3 (cultural and social context)
- Biographical Analysis: Article 4 (director perspective and process)
```

## Success Criteria

✅ Diverse and credible sources collected
✅ Multiple analytical perspectives represented
✅ Direct relevance to episode topic confirmed
✅ Balance between academic and accessible analysis
✅ Clear summaries provided for each source

## Related Prompts

- `collect-youtube-sources.prompt.md` - Collect video analysis sources
- `analyze-cinema-content.prompt.md` - Begin comprehensive content analysis
- `synthesize-episode-content.prompt.md` - Combine all collected sources

## Related Rules

- `.cursor/rules/podcast/source-credibility-rule.mdc` - Source evaluation standards
- `.cursor/rules/podcast/analysis-depth-rule.mdc` - Analytical quality requirements

---

**Goal**: Comprehensive written analysis foundation for cinema podcast episodes

---

**Created**: 2025-12-13 (Podcast workflow setup)
**Updated**: 2025-12-13 (Initial creation)
**Rule**: `rule.prompts.creation.v1`, `rule.prompts.registry-integration.v1`
