# Text Processing Pipeline

Build a complete Text Processing Pipeline that scrapes real user reviews from Flipkart, preprocesses them, converts text into numerical features, and performs sentiment classification.

## Pipeline Overview

```
Data Collection → Preprocessing → Vocabulary → Feature Engineering → Analysis → Sentiment Classification
```

## Tasks

| Task | Description |
|------|-------------|
| **1. Preprocessing** | Lowercase, tokenization, remove punctuation & stopwords, lemmatization |
| **2. Vocabulary Creation** | Build vocabulary, analyze word frequencies, visualize top-20 words |
| **3. Feature Engineering** | One-Hot Encoding, Bag of Words (CountVectorizer), TF-IDF (TfidfVectorizer) |
| **4. Comparison Analysis** | Compare OHE vs BoW vs TF-IDF — sparsity, value types, use cases |
| **5. Sparse Matrix Analysis** | Analyze shape, sparsity %, memory usage, why sparse formats matter |
| **6. Real-world Questions** | Why BoW fails semantically, when to use BoW vs TF-IDF, TF-IDF limitations |
| **7. Sentiment Classification** | Logistic Regression & Naive Bayes on BoW + TF-IDF features, confusion matrix |

## Scraper

The scraper (`scraper.py`) uses **Playwright** to open a real Chromium browser and extract reviews from Flipkart product pages. It parses the rendered DOM by text structure (not CSS classes), making it resilient to Flipkart's frequent UI changes.

```bash
# Run from command line
python scraper.py <flipkart_product_reviews_url> [max_reviews] [output.csv]

# Example
python scraper.py "https://www.flipkart.com/some-product/product-reviews/itmXXX" 500 reviews.csv
```

From the notebook, it runs as a **subprocess** (Playwright's sync API conflicts with Jupyter's asyncio loop).

## Project Structure

```
text-processing-pipeline/
├── notebook.ipynb      # Main notebook with all 7 tasks
├── scraper.py          # Flipkart review scraper (Playwright)
├── requirements.txt    # Python dependencies
├── data/
│   └── raw/            # Scraped CSV files
└── README.md
```

## Dependencies

- **pandas**, **numpy** — data handling
- **nltk** — tokenization, stopwords, lemmatization
- **scikit-learn** — CountVectorizer, TfidfVectorizer, Logistic Regression, Naive Bayes
- **matplotlib**, **seaborn** — visualization
- **playwright** — browser-based scraping (bypasses Flipkart's reCAPTCHA)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Open notebook
jupyter notebook notebook.ipynb
```

## Insights & Results

### Dataset
- **Product:** Noise Masterbuds 2 (Flipkart)
- **Reviews scraped:** 74 (across 8 pages)
- **Rating distribution:** 5★: 65 | 4★: 3 | 2★: 2 | 1★: 4
- Heavily skewed towards positive — most buyers were satisfied

### Preprocessing
- All 74 reviews retained after cleaning (no empty results)
- Lemmatization effectively groups variants: *"sounds" → "sound"*, *"products" → "product"*
- Example: `"Sound quality is very good, with a nice balance of bass and clarity."` → `"sound quality good nice balance bass clarity"`

### Vocabulary
- **Total words:** 492 (with repetition)
- **Unique vocabulary:** 190 words
- **Top words:** `product` (29), `sound` (28), `quality` (19), `good` (19), `best` (19) — product-specific terms dominate

### Feature Engineering
- All three matrices share the same shape: **74 × 190**
- **Top TF-IDF words:** `product` (0.1047), `best` (0.0912), `good` (0.0898), `sound` (0.0841)
- TF-IDF down-weighted common words like `product` relative to their raw frequency, while boosting rarer discriminative words like `fabulous` and `super`

### Sparsity
- All matrices have **96.56% sparsity** (13,576 out of 14,060 elements are zeros)
- Sparse format (CSR) uses only **6.0 KB** vs dense format **109.8 KB** — an **18x memory saving**
- OHE stored as dense numpy array uses 54.9 KB (no sparse benefit since it's not in CSR format)

### Sentiment Classification
- **74 reviews** used: 68 positive (rating ≥ 4), 6 negative (rating ≤ 2)
- Train/test split: 59 / 15
- All 4 model combinations achieved **93.3% accuracy**:

| Model | Features | Accuracy |
|-------|----------|----------|
| Logistic Regression | BoW | 93.3% |
| Naive Bayes | BoW | 93.3% |
| Logistic Regression | TF-IDF | 93.3% |
| Naive Bayes | TF-IDF | 93.3% |

- Models correctly classified all positive reviews but struggled with negatives (only 1 negative in test set, misclassified by all models)
- The dataset is **highly imbalanced** (92% positive) — accuracy is high but negative recall is 0%. With more balanced data, TF-IDF would likely outperform BoW

### Key Takeaways
1. Traditional text representations (OHE, BoW, TF-IDF) are foundational but treat words independently — they cannot capture synonyms, word order, or context
2. TF-IDF is superior to BoW for most tasks because it automatically down-weights common words and highlights discriminative terms
3. Sparse matrix formats are essential at scale — even with just 74 documents, 96.5% of matrix values are zeros
4. Class imbalance significantly impacts model evaluation — high accuracy can be misleading when one class dominates
