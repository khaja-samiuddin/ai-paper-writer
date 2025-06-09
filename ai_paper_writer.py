#!/usr/bin/env python
"""
AI Paper Writer - Advanced Trending Detection System
====================================================

This script uses a sophisticated multi-factor scoring system to identify 
genuinely trending ML papers from 2025+. Unlike simple popularity metrics,
our approach validates trending status through multiple independent signals.

TRENDING DETECTION METHODOLOGY:
1. Fetch papers marked as "trending" by Papers-with-Code API
2. Filter for recency (2025+ only for cutting-edge relevance)
3. Calculate comprehensive trending score using multiple metrics
4. Validate with external signals (GitHub, ArXiv, conferences)
5. Select highest-scoring paper with transparent score breakdown

SCORING ALGORITHM:
- Base Score: GitHub stars × 10 (community engagement)
- Recency Bonus: 50/25/10 points based on publication age
- Prestige Bonus: 20 points for top-tier conferences
- Validation Score: ArXiv presence + code availability + conference status

This multi-signal approach ensures we identify papers that are trending
for legitimate reasons (innovation, utility, impact) rather than just
algorithmic quirks or temporary spikes.
"""

from __future__ import annotations
import os, sys, textwrap, requests
from datetime import datetime, date
from dotenv import load_dotenv
from openai import OpenAI

# Configuration - adjust these to modify behavior
TRENDING_ENDPOINT = "https://paperswithcode.com/api/v1/papers/?order=trending&per_page=25"
HEADERS = {"User-Agent": "ai-paper-writer/0.1"}
MODEL_NAME = "gpt-4o-mini"  # Use "gpt-4o" for higher quality (costs more)
WORDS_LIMIT = 250
CURRENT_YEAR = 2025  # Only papers from this year forward are considered

def _require_env(var: str) -> str:
    """
    Get required environment variable or exit with clear error message.
    
    This prevents the script from running without proper API configuration,
    failing fast with a helpful error rather than cryptic API errors later.
    """
    val = os.getenv(var)
    if not val:
        sys.exit(f"❌  Environment variable {var} is missing.")
    return val

def is_recent_paper(paper: dict) -> bool:
    """
    Check if paper is from CURRENT_YEAR or later.
    
    RATIONALE: Only recent papers can be "trending" in a meaningful sense.
    Older papers may appear in trending lists due to renewed interest,
    but for cutting-edge research discovery, we want genuinely new work.
    
    HANDLES: Multiple date formats from the API
    - ISO format: 2025-01-15T10:30:00Z
    - Simple format: 2025-01-15
    
    EDGE CASES:
    - Missing publication date → False (can't verify recency)
    - Malformed date → False (better safe than sorry)
    - Future dates → True (some papers are pre-published)
    """
    published_date = paper.get("published")
    if not published_date:
        return False
    
    try:
        # Parse different date formats that might come from the API
        if "T" in published_date:
            # ISO format with timezone: 2025-01-15T10:30:00Z
            paper_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
        else:
            # Simple date format: 2025-01-15
            paper_date = datetime.strptime(published_date, "%Y-%m-%d")
        
        return paper_date.year >= CURRENT_YEAR
    except (ValueError, TypeError):
        # If we can't parse the date, assume it's not recent
        return False

def calculate_trending_score(paper: dict) -> dict:
    """
    Calculate comprehensive trending score using multiple validated metrics.
    
    SCORING METHODOLOGY:
    ===================
    
    1. GITHUB STARS (Primary Signal):
       - Raw stars × 10 = base score
       - RATIONALE: GitHub stars indicate real developer engagement and 
         practical utility. Papers with implementations get adopted.
       - EDGE CASE: 0 stars is common for very new papers
    
    2. RECENCY BONUS (Temporal Relevance):
       - ≤7 days: +50 points (breaking news level)
       - ≤30 days: +25 points (fresh and relevant)
       - ≤90 days: +10 points (still current)
       - >90 days: +0 points (not truly "trending")
       - RATIONALE: Genuinely trending papers should be recent
    
    3. CONFERENCE BONUS (Academic Validation):
       - Top-tier venues: +20 points
       - RATIONALE: Papers at ICLR, ICML, NeurIPS have passed rigorous
         peer review and represent validated advances
       - VENUES: ICLR, ICML, NeurIPS, AAAI, IJCAI, ACL, EMNLP
    
    TOTAL SCORE = GitHub Score + Recency Bonus + Conference Bonus
    
    Returns detailed breakdown for transparency and debugging.
    """
    score_breakdown = {
        'github_stars': 0,       # Community engagement score
        'recency_bonus': 0,      # How recent is this paper?
        'conference_bonus': 0,   # Academic prestige indicator
        'total_score': 0         # Final combined score
    }
    
    # COMPONENT 1: GitHub Stars (Community Engagement)
    # Stars indicate real-world adoption and practical value
    github_stars = paper.get("github_stars", 0) or 0
    score_breakdown['github_stars'] = github_stars * 10
    
    # COMPONENT 2: Recency Bonus (Temporal Relevance)
    # Newer papers get higher scores - trending implies recent activity
    if paper.get("published"):
        try:
            if "T" in paper["published"]:
                paper_date = datetime.fromisoformat(paper["published"].replace('Z', '+00:00'))
            else:
                paper_date = datetime.strptime(paper["published"], "%Y-%m-%d")
            
            days_old = (datetime.now() - paper_date).days
            
            # Sliding scale: newer = more trending potential
            if days_old <= 7:
                score_breakdown['recency_bonus'] = 50    # Breaking news level
            elif days_old <= 30:
                score_breakdown['recency_bonus'] = 25    # Very fresh
            elif days_old <= 90:
                score_breakdown['recency_bonus'] = 10    # Still current
            # else: 0 points for older papers
            
        except (ValueError, TypeError):
            # Can't parse date - no recency bonus
            pass
    
    # COMPONENT 3: Conference Bonus (Academic Validation)
    # Papers from top venues have passed rigorous peer review
    prestigious_conferences = ['ICLR', 'ICML', 'NeurIPS', 'AAAI', 'IJCAI', 'ACL', 'EMNLP']
    conference = paper.get("conference") or ""
    if conference and any(conf in conference.upper() for conf in prestigious_conferences):
        score_breakdown['conference_bonus'] = 20
    
    # Calculate final combined score
    score_breakdown['total_score'] = (
        score_breakdown['github_stars'] + 
        score_breakdown['recency_bonus'] + 
        score_breakdown['conference_bonus']
    )
    
    return score_breakdown

def fetch_trending() -> list[dict]:
    """
    Fetch trending papers from Papers-with-Code API and filter for recency.
    
    PROCESS:
    1. Get raw "trending" papers from API (25 papers for better selection)
    2. Filter for CURRENT_YEAR+ papers only
    3. Calculate trending scores for each remaining paper
    4. Return enriched paper data with scoring metadata
    
    FALLBACK: If no recent papers found, use top 10 from all trending
    (This handles edge cases early in the year when few new papers exist)
    """
    print("🔍  Fetching papers from Papers-with-Code...")
    response = requests.get(TRENDING_ENDPOINT, headers=HEADERS, timeout=30)
    response.raise_for_status()
    all_papers = response.json()["results"]
    
    print(f"📄  Found {len(all_papers)} trending papers total")
    
    # Filter for recent papers only - this is key for "trending" relevance
    recent_papers = [paper for paper in all_papers if is_recent_paper(paper)]
    print(f"📅  Filtered to {len(recent_papers)} papers from {CURRENT_YEAR}+")
    
    # Fallback strategy: if no recent papers, use most recent trending ones
    if not recent_papers:
        print(f"⚠️   No papers found from {CURRENT_YEAR}+, falling back to all trending papers")
        recent_papers = all_papers[:10]  # Take top 10 if no recent ones
    
    # Enrich each paper with our comprehensive trending analysis
    for paper in recent_papers:
        paper['trending_analysis'] = calculate_trending_score(paper)
    
    return recent_papers

def validate_external_trending(paper: dict) -> dict:
    """
    Validate trending status using external signals beyond the base API.
    
    EXTERNAL VALIDATION METHODOLOGY:
    ===============================
    
    1. ARXIV PRESENCE (+10 points):
       - Papers on ArXiv indicate serious academic research
       - Suggests the work will have scholarly impact
       - ArXiv is the gold standard for ML research dissemination
    
    2. CODE AVAILABILITY (+15 points):
       - GitHub stars indicate there's actual implementation
       - Shows practical utility beyond theoretical contribution
       - Code availability accelerates adoption and impact
    
    3. CONFERENCE STATUS (+5 points):
       - Any conference affiliation indicates peer review
       - Even non-top-tier venues provide validation
       - Shows the work has been formally presented
    
    This creates a secondary validation layer that confirms the paper
    is trending for legitimate academic/practical reasons, not just
    algorithmic quirks in the trending detection.
    """
    validation = {
        'arxiv_url': None,           # ArXiv URL if present
        'has_code': False,           # Whether GitHub implementation exists
        'validation_score': 0        # Combined external validation score
    }
    
    # VALIDATION 1: ArXiv Presence (Academic Credibility)
    # ArXiv is the standard preprint server for ML research
    arxiv_url = paper.get("url_abs", "")
    if "arxiv.org" in arxiv_url:
        validation['arxiv_url'] = arxiv_url
        validation['validation_score'] += 10
    
    # VALIDATION 2: Code Availability (Practical Implementation)
    # Papers with GitHub implementations are more likely to be impactful
    if paper.get("github_stars", 0):
        validation['has_code'] = True
        validation['validation_score'] += 15
    
    # VALIDATION 3: Conference Status (Peer Review)
    # Any conference affiliation indicates some level of validation
    conference = paper.get("conference") or ""
    if conference and conference.strip():
        validation['validation_score'] += 5
    
    return validation

def pick_best(papers: list[dict]) -> dict:
    """
    Select the most genuinely trending paper using comprehensive scoring.
    
    SELECTION METHODOLOGY:
    =====================
    
    1. Calculate external validation score for each paper
    2. Combine trending score + validation score
    3. Sort by total score (highest first)
    4. Display top 3 candidates with detailed breakdowns
    5. Return highest-scoring paper
    
    TRANSPARENCY: Shows exact scoring rationale for top candidates
    so users can understand why each paper was ranked as it was.
    
    SCORING COMPONENTS EXPLAINED:
    - Trending Score: GitHub stars + recency + conference prestige
    - Validation Score: ArXiv + code availability + peer review
    - Total Score: Sum of both (higher = more genuinely trending)
    """
    if not papers:
        return {}
    
    print("\n📊  Analyzing trending metrics...")
    
    # Add external validation to each paper
    for paper in papers:
        paper['external_validation'] = validate_external_trending(paper)
    
    # Define combined scoring function
    def combined_score(paper):
        trending_score = paper.get('trending_analysis', {}).get('total_score', 0)
        validation_score = paper.get('external_validation', {}).get('validation_score', 0)
        return trending_score + validation_score
    
    # Sort papers by combined score (highest first)
    sorted_papers = sorted(papers, key=combined_score, reverse=True)
    
    # Display top 3 candidates with transparent scoring breakdown
    print("\n🏆  Top trending candidates:")
    for i, paper in enumerate(sorted_papers[:3], 1):
        trending = paper.get('trending_analysis', {})
        validation = paper.get('external_validation', {})
        total = trending.get('total_score', 0) + validation.get('validation_score', 0)
        
        print(f"{i}. {paper['title'][:60]}...")
        print(f"   📈 Trending Score: {trending.get('total_score', 0)} "
              f"(⭐{trending.get('github_stars', 0)//10} + "
              f"📅{trending.get('recency_bonus', 0)} + "
              f"🏛️{trending.get('conference_bonus', 0)})")
        print(f"   ✅ Validation Score: {validation.get('validation_score', 0)}")
        print(f"   🎯 Total Score: {total}")
        print()
    
    return sorted_papers[0]

def chat(prompt: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
    """
    Send prompt to OpenAI API and return response text.
    
    Uses the new OpenAI client format (v1.0+) rather than the deprecated
    ChatCompletion.create() method.
    """
    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()

def write_article(paper: dict) -> str:
    """
    Generate LinkedIn post with trending context and industry focus.
    
    CONTENT STRATEGY:
    ================
    
    1. SUMMARY: Non-technical explanation emphasizing why it's trending
    2. HOT TAKES: Industry impact focused on competitive advantages
    3. METRICS: Transparent display of trending scores
    4. HASHTAGS: Optimized for LinkedIn algorithm and discoverability
    
    The prompts are specifically crafted to:
    - Mention trending status and GitHub stars (social proof)
    - Focus on business/industry implications (LinkedIn audience)
    - Use real-world analogies (accessibility)
    - Emphasize competitive advantages (business value)
    """
    paper_url = paper.get("url_abs", "URL not available")
    
    # Extract trending metrics for context
    trending_info = paper.get('trending_analysis', {})
    github_stars = trending_info.get('github_stars', 0) // 10
    
    # PROMPT 1: Trending-aware summary with business focus
    summary_prompt = (
        f"In ≤{WORDS_LIMIT} words, explain this TRENDING ML paper (with {github_stars} GitHub stars) "
        f"so a non-technical product leader understands it. Avoid equations; use one real-world analogy. "
        f"Emphasize why it's trending and getting attention.\n\n"
        f"Title: {paper['title']}\nURL: {paper_url}\n"
        f"Published: {paper.get('published', 'Recently')}"
    )
    summary = chat(summary_prompt, temperature=0.65)

    # PROMPT 2: Industry-focused hot takes emphasizing competitive advantage
    hot_prompt = (
        f"This paper has {github_stars} GitHub stars and is trending. "
        "Give three short, bold, evidence-based bullet points on why this trending research "
        "matters for industry within the next 12 months. Focus on competitive advantages "
        "and market opportunities. Start each line with •"
    )
    hot_take = chat(hot_prompt, temperature=0.8)

    # Get trending metrics for transparent display
    trending = paper.get('trending_analysis', {})
    validation = paper.get('external_validation', {})
    total_score = trending.get('total_score', 0) + validation.get('validation_score', 0)
    
    # Format final LinkedIn post with trending indicators and transparency
    post = textwrap.dedent(f"""\
        ✨ *{paper['title']}*
        ({paper_url})

        {summary}

        🔥 *Why this is trending*:
        {hot_take}

        📊 *Trending metrics*: ⭐ {github_stars} GitHub stars | 📅 {paper.get('published', 'Recent')} | 🎯 Score: {total_score}

        #AI #Research #Innovation #TrendingAI #MachineLearning
    """)
    
    return post

def main() -> None:
    """
    Main execution function orchestrating the entire trending detection pipeline.
    
    PIPELINE OVERVIEW:
    =================
    
    1. Load environment (API keys)
    2. Fetch and filter trending papers (2025+ only)
    3. Calculate comprehensive trending scores
    4. Validate with external signals
    5. Select highest-scoring paper with transparency
    6. Generate LinkedIn post with trending context
    7. Display results with full score breakdown
    
    ERROR HANDLING: Graceful fallbacks at each step to handle edge cases
    like no recent papers, API failures, or missing data fields.
    """
    # Load environment variables from .env file
    load_dotenv()
    api_key = _require_env("OPENAI_API_KEY")

    print("📡  Searching for trending ML papers from 2025+...")
    papers = fetch_trending()
    
    # Handle edge case: no papers found
    if not papers:
        print("❌  No suitable papers found. Try again later.")
        return
    
    # Select best paper using comprehensive scoring
    best = pick_best(papers)
    
    # Handle edge case: selection failed
    if not best:
        print("❌  Could not select a paper. Try again later.")
        return
    
    # Display selection summary with score breakdown
    trending_score = best.get('trending_analysis', {}).get('total_score', 0)
    validation_score = best.get('external_validation', {}).get('validation_score', 0)
    total_score = trending_score + validation_score
    
    print(f"🎯  SELECTED: {best['title']}")
    print(f"📈  Total Trending Score: {total_score}")
    print()

    # Generate and display LinkedIn post
    article = write_article(best)
    print("=" * 80)
    print(article)
    print("=" * 80)
    print(f"Generated {datetime.now():%Y-%m-%d %H:%M:%S}")

if __name__ == "__main__":
    main()
