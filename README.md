# AI Paper Writer - Advanced Trending Detection

Automatically generates LinkedIn posts from the **latest trending ML papers (2025+)** using a sophisticated multi-factor scoring system to identify genuinely trending research.

## How Our Trending Detection Works

### 🧠 The Problem with Simple "Trending" Lists

Most platforms use basic metrics like view counts or simple popularity rankings. These can be gamed, temporary, or misleading. Our system validates trending status through **multiple independent signals** to identify papers that are trending for legitimate reasons.

### 🎯 Our Multi-Factor Scoring System

We use a **two-layer validation approach**:

1. **Primary Trending Score** - Quantifies genuine trending potential
2. **External Validation Score** - Confirms trending status with independent signals
3. **Combined Total** - Ranks papers by comprehensive trending evidence

---

## 📊 Detailed Scoring Methodology

### Layer 1: Primary Trending Score

#### **GitHub Stars Component (Primary Signal)**
- **Formula**: `Raw GitHub Stars × 10 = Base Score`
- **Rationale**: GitHub stars indicate real developer engagement and practical utility
- **Why it matters**: Papers with implementations get adopted in the real world
- **Edge cases**: 
  - 0 stars = 0 points (common for very new papers)
  - High stars = Strong community validation

**Example**: 
- Paper with 5 GitHub stars = 50 points
- Paper with 0 GitHub stars = 0 points

#### **Recency Bonus (Temporal Relevance)**
- **≤7 days old**: +50 points (Breaking news level)
- **≤30 days old**: +25 points (Very fresh and relevant)  
- **≤90 days old**: +10 points (Still current)
- **>90 days old**: +0 points (Not truly "trending")

**Rationale**: Genuinely trending papers should be recent. This prevents old papers from appearing "trending" due to algorithmic quirks.

**Example**: 
- Paper published 5 days ago = +50 points
- Paper published 45 days ago = +10 points
- Paper published 6 months ago = +0 points

#### **Conference Bonus (Academic Validation)**
- **Top-tier venues**: +20 points
- **Venues**: ICLR, ICML, NeurIPS, AAAI, IJCAI, ACL, EMNLP
- **Rationale**: Papers at prestigious conferences have passed rigorous peer review

**Example**:
- Paper at ICLR 2025 = +20 points
- Paper at unknown conference = +0 points
- Preprint only = +0 points

### Layer 2: External Validation Score

#### **ArXiv Presence (+10 points)**
- **Signal**: Paper hosted on arxiv.org
- **Indicates**: Serious academic research with scholarly impact potential
- **Why it matters**: ArXiv is the gold standard for ML research dissemination

#### **Code Availability (+15 points)** 
- **Signal**: Has GitHub repository with any stars
- **Indicates**: Practical implementation exists beyond just theory
- **Why it matters**: Code availability accelerates adoption and real-world impact

#### **Conference Status (+5 points)**
- **Signal**: Any conference affiliation listed
- **Indicates**: Has undergone some form of peer review
- **Why it matters**: Shows the work has been formally validated

---

## 🔢 Scoring Examples

### Example 1: High-Scoring Trending Paper
```
Paper: "Revolutionary Transformer Architecture"
Published: 2025-01-05 (5 days ago)
GitHub Stars: 12
Conference: ICLR 2025
ArXiv: Yes

Trending Score Breakdown:
├─ GitHub Stars: 12 × 10 = 120 points
├─ Recency Bonus: ≤7 days = +50 points  
├─ Conference Bonus: ICLR = +20 points
└─ Trending Total: 190 points

Validation Score Breakdown:
├─ ArXiv Presence: +10 points
├─ Code Available: +15 points
├─ Conference Status: +5 points  
└─ Validation Total: 30 points

🎯 FINAL SCORE: 220 points
```

### Example 2: Medium-Scoring Paper
```
Paper: "Novel Optimization Method"
Published: 2025-02-20 (45 days ago)
GitHub Stars: 3
Conference: None
ArXiv: Yes

Trending Score Breakdown:
├─ GitHub Stars: 3 × 10 = 30 points
├─ Recency Bonus: ≤90 days = +10 points
├─ Conference Bonus: None = +0 points
└─ Trending Total: 40 points

Validation Score Breakdown:
├─ ArXiv Presence: +10 points
├─ Code Available: +15 points  
├─ Conference Status: +0 points
└─ Validation Total: 25 points

🎯 FINAL SCORE: 65 points
```

### Example 3: Low-Scoring Paper
```
Paper: "Theoretical Analysis of X"
Published: 2024-08-15 (too old, filtered out)
OR
Published: 2025-03-01 (recent)
GitHub Stars: 0
Conference: None
ArXiv: Yes

Trending Score Breakdown:
├─ GitHub Stars: 0 × 10 = 0 points
├─ Recency Bonus: No stars = +25 points
├─ Conference Bonus: None = +0 points
└─ Trending Total: 25 points

Validation Score Breakdown:
├─ ArXiv Presence: +10 points
├─ Code Available: +0 points
├─ Conference Status: +0 points
└─ Validation Total: 10 points

🎯 FINAL SCORE: 35 points
```

---

## 🔍 Why This Approach Works

### **Multi-Signal Validation**
- **Single metrics can be gamed** - Our system requires multiple signals
- **Temporal relevance** - Only recent papers can be truly "trending"
- **Community validation** - GitHub stars show real developer interest
- **Academic rigor** - Conference/ArXiv presence validates quality

### **Transparent Scoring**
- **See exactly why** each paper was ranked
- **No black box algorithms** - every score component explained
- **Reproducible results** - same paper = same score

### **Edge Case Handling**
- **No recent papers**: Falls back to most recent trending papers
- **Missing data**: Graceful degradation (0 points for missing components)
- **Date parsing errors**: Excludes papers with unparseable dates
- **API failures**: Clear error messages and fallbacks

---

## 🚀 What it does

1. **Fetches recent trending papers** from Papers-with-Code API (2025+ only)
2. **Validates trending status** using our multi-factor scoring system
3. **Selects genuinely trending paper** with highest combined score
4. **Generates content** using OpenAI GPT with trending context:
   - Non-technical summary (≤250 words) with real-world analogy
   - Three industry impact "hot takes" focused on competitive advantages
5. **Outputs LinkedIn-ready post** with transparent trending metrics

## Prerequisites

- **Python 3.8 or higher**
- **OpenAI API Key** (get one at [platform.openai.com](https://platform.openai.com))
- **Internet connection** (for API calls)

## Setup Instructions

### 1. Clone or Download

```bash
# Option A: If you have git
git clone <repository-url>
cd ai-paper-writer

# Option B: Download the files manually
# Download ai_paper_writer.py to your desired folder
```

### 2. Create Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install openai requests python-dotenv
```

### 4. Set Up OpenAI API Key

Create a `.env` file in the same directory as `ai_paper_writer.py`:

```bash
# Create .env file
touch .env  # On macOS/Linux
echo. > .env  # On Windows
```

Add your OpenAI API key to the `.env` file:

```env
OPENAI_API_KEY=your_actual_api_key_here
```

**⚠️ Important:**
- Replace `your_actual_api_key_here` with your actual OpenAI API key
- Never commit the `.env` file to version control
- Keep your API key secret

### 5. Run the Script

```bash
python ai_paper_writer.py
```

## Expected Output

```
📡  Searching for trending ML papers from 2025+...
🔍  Fetching papers from Papers-with-Code...
📄  Found 25 trending papers total
📅  Filtered to 8 papers from 2025+

📊  Analyzing trending metrics...

🏆  Top trending candidates:
1. Revolutionary Transformer Architecture for Real-Time Processing...
   📈 Trending Score: 190 (⭐120 + 📅50 + 🏛️20)
   ✅ Validation Score: 30
   🎯 Total Score: 220

2. Efficient Large Language Model Training with Quantum Computing...
   📈 Trending Score: 80 (⭐30 + 📅25 + 🏛️0)
   ✅ Validation Score: 25
   🎯 Total Score: 105

3. Zero-Shot Learning for Computer Vision Applications...
   📈 Trending Score: 40 (⭐0 + 📅25 + 🏛️0)
   ✅ Validation Score: 15
   🎯 Total Score: 55

🎯  SELECTED: Revolutionary Transformer Architecture for Real-Time Processing
📈  Total Trending Score: 220

================================================================================
✨ *Revolutionary Transformer Architecture for Real-Time Processing*
(https://arxiv.org/abs/2025.xxxxx)

[Generated summary explaining why this trending paper matters...]

🔥 *Why this is trending*:
• [Industry impact focused on competitive advantages]
• [Market opportunities and implementation potential]
• [Timeline for adoption and business value]

📊 *Trending metrics*: ⭐ 12 GitHub stars | 📅 2025-01-05 | 🎯 Score: 220

#AI #Research #Innovation #TrendingAI #MachineLearning
================================================================================
Generated 2025-01-XX 12:34:56
```

## Configuration Options

You can modify these settings in `ai_paper_writer.py`:

```python
MODEL_NAME = "gpt-4o-mini"     # Change to "gpt-4o" for better quality (higher cost)
WORDS_LIMIT = 250              # Adjust summary length
CURRENT_YEAR = 2025            # Change year filter (e.g., 2024 for more papers)

# Advanced: Modify scoring weights in calculate_trending_score()
github_multiplier = 10         # Currently: stars × 10
recency_bonus_values = [50, 25, 10]  # [≤7days, ≤30days, ≤90days]
conference_bonus = 20          # Points for top-tier venues
```

## Troubleshooting

### Error: `command not found: python`
- Try `python3` instead of `python`
- Make sure Python is installed: [python.org/downloads](https://python.org/downloads)

### Error: `Environment variable OPENAI_API_KEY is missing`
- Check that `.env` file exists in the same directory as the script
- Verify the API key is correctly formatted in `.env`
- Ensure there are no extra spaces around the `=` sign

### Error: `API key authentication failed`
- Verify your OpenAI API key is valid
- Check you have sufficient credits in your OpenAI account
- Visit [platform.openai.com/api-keys](https://platform.openai.com/api-keys) to manage keys

### Error: `requests.exceptions.ConnectionError`
- Check your internet connection
- The Papers-with-Code API might be temporarily down

### Warning: `No papers found from 2025+, falling back to all trending papers`
- **This is normal** early in the year when few 2025 papers exist
- The script automatically falls back to the most recent trending papers
- You can change `CURRENT_YEAR = 2024` to get more results

### All papers have low trending scores
- **This indicates genuine trending papers are rare** (which is realistic!)
- The script still selects the best available option
- Consider adjusting the year filter or running at different times
- Low scores often mean papers are genuinely new (0 GitHub stars yet)

### Understanding Score Interpretations
- **200+ points**: Genuinely viral/trending paper with strong signals
- **100-200 points**: Solid trending paper with good validation
- **50-100 points**: Moderate trending signals
- **<50 points**: Weak trending signals but still the best available

## Advanced: Customizing the Scoring Algorithm

### Adjusting Score Weights

You can modify the scoring algorithm by editing these functions in `ai_paper_writer.py`:

```python
def calculate_trending_score(paper: dict) -> dict:
    # Modify these values to change scoring behavior:
    
    # GitHub stars multiplier (currently 10)
    score_breakdown['github_stars'] = github_stars * 10
    
    # Recency bonus values (currently 50/25/10)
    if days_old <= 7:
        score_breakdown['recency_bonus'] = 50    # Adjust this
    elif days_old <= 30:
        score_breakdown['recency_bonus'] = 25    # Adjust this
    elif days_old <= 90:
        score_breakdown['recency_bonus'] = 10    # Adjust this
    
    # Conference bonus (currently 20)
    score_breakdown['conference_bonus'] = 20     # Adjust this

def validate_external_trending(paper: dict) -> dict:
    # Modify validation score weights:
    validation['validation_score'] += 10  # ArXiv presence
    validation['validation_score'] += 15  # Code availability  
    validation['validation_score'] += 5   # Conference status
```

### Adding New Scoring Components

You can extend the scoring system by adding new factors:

1. **Twitter mentions**: Check for social media buzz
2. **Citation count**: Academic impact indicator
3. **Author reputation**: H-index or previous paper impact
4. **Implementation complexity**: Ease of reproduction

## File Structure

```
ai-paper-writer/
├── ai_paper_writer.py    # Main script with enhanced trending detection
├── .env                  # API key (create this)
├── README.md            # This comprehensive guide
└── venv/                # Virtual environment (created during setup)
```

## Running on Different Computers

To run this on a new computer:

1. **Copy these files:**
   - `ai_paper_writer.py`
   - `README.md`
   - `.env` (contains your API key)

2. **Follow setup steps 2-5** from above

3. **That's it!** The script should work identically

## API Costs

- **GPT-4o-mini**: ~$0.01-0.02 per run
- **GPT-4o**: ~$0.10-0.20 per run

The script makes 2 API calls per run (summary + hot takes).

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed correctly
3. Verify your Python version: `python --version` (should be 3.8+)
4. **Check the trending analysis output** for debugging information
5. Try running with verbose error output: `python -v ai_paper_writer.py`

## Understanding Your Results

The script provides complete transparency into its decision-making process. Use the detailed score breakdowns to understand:

- **Why** each paper was ranked as it was
- **Which signals** contributed most to the trending status
- **How reliable** the trending detection is for each candidate
- **Whether** the selected paper has strong validation signals

This transparency allows you to make informed decisions about which papers to feature and helps you understand the current state of trending ML research. 