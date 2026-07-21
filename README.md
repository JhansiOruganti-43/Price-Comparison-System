# AI-Based Product Price Comparison and Recommendation System

An AI-powered smart shopping assistant that scans multiple online shopping platforms (Amazon, Flipkart, Myntra, Ajio, Meesho), identifies identical products using NLP (TF-IDF + Cosine Similarity), performs sentiment analysis on product reviews, and recommends the best overall deal using a multi-criteria weighted scoring algorithm.
---

## Project Workflow

### 1. Search Product
Users enter a product name in the search bar.
<img width="772" height="1020" alt="Screenshot 2026-06-23 175824" src="https://github.com/user-attachments/assets/17c053ed-ff0c-4a19-8771-de2c8e42ed17" />


### 2. Fetch Product Data
The Flask backend collects product information from multiple e-commerce platforms including Amazon, Flipkart, Meesho, Myntra, and Ajio.
<img width="772" height="1019" alt="Screenshot 2026-06-23 175834" src="https://github.com/user-attachments/assets/3028feda-2011-4558-9cfe-62df7bfcd83e" />


### 3. AI-Based Product Matching
Products with different naming formats are grouped together using TF-IDF and Cosine Similarity.
<img width="844" height="906" alt="Screenshot 2026-06-23 181037" src="https://github.com/user-attachments/assets/54740fb7-5431-449f-8ceb-783976507703" />


### 4. Compare & Recommend
The system compares prices, ratings, discounts, delivery fees, and customer sentiment to identify the best-value deal.
<img width="416" height="643" alt="image" src="https://github.com/user-attachments/assets/a6cef6f6-7629-4d4a-9dc3-90df01bde0a7" />


### 5. Search History & Analytics
Searches are stored in SQLite and displayed in the dashboard for quick access and analytics.
<img width="813" height="1019" alt="Screenshot 2026-06-23 180948" src="https://github.com/user-attachments/assets/1b7226c4-9859-4efb-bfc2-809ad23819e0" />

---

## Features

1. **Multi-Platform Search**: Searches across Amazon, Flipkart, Myntra, Ajio, and Meesho simultaneously.
2. **AI Same-Product Detection**: Clustered using a TF-IDF vectorizer + Cosine Similarity matching to group matching models with different names (e.g. "iPhone 15 Blue 128GB" and "Apple iPhone 15 (128 GB) - Blue") into a single visual page.
3. **AI Spec Matching**: Implements regex spec extraction (Storage size, RAM size, Clothing size) to prevent incorrect matches between different spec tiers of the same product.
4. **Weighted Recommendation Scoring**: Calculates an overall value score (out of 100) using a multi-criteria decision formula:
   - Price (40% weight - lower is better)
   - Product Rating (25% weight - higher is better)
   - Discount Percentage (15% weight - higher is better)
   - Delivery Fees (10% weight - lower is better)
   - Review Sentiment (10% weight - positive sentiment is better)
5. **Review Sentiment Analyzer**: Utilizes NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analyzer on customer feedback, falling back to a custom word-based classifier if offline.
6. **Premium UI/UX Dashboard**: Custom-designed responsive dark theme with frosted glass (glassmorphism), price comparison bar charts (Recharts), search query cache, and real-time saved alerts database.
7. **Database Caching & Alerts**: Stores search queries and results in a local SQLite database for instant caching. Enables users to configure custom Price Alert thresholds.

---

## Project Structure

```text
price_cmp/
├── backend/
│   ├── app.py              # Flask server and REST API routes
│   ├── models.py           # SQLAlchemy database models (SQLite)
│   ├── scraper.py          # Web scraper with dynamic mock data fallback
│   ├── matcher.py          # AI NLP product grouping/clustering
│   ├── recommender.py      # AI recommender scoring and sentiment analysis
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── package.json        # Frontend configuration and npm dependencies
│   ├── vite.config.js      # Vite build configuration
│   ├── index.html          # Web page wrapper and SEO tags
│   └── src/
│       ├── main.jsx        # React bootloader
│       ├── App.jsx         # Dashboard views, charts, alert modals & API triggers
│       └── index.css       # Core vanilla CSS design tokens & glassmorphic layout
└── run.bat                 # Windows double-clickable orchestrator script
```

---

## Technical Setup & Execution

### Prerequisites
1. **Python 3.13+** (using `py` launcher or `python` command)
2. **Node.js v20+** and **npm v10+**

### Easy Start (Windows)
Double-click the **`run.bat`** file in the root directory.
This script will:
1. Verify backend and frontend dependencies are present.
2. Start the Flask REST API on [http://localhost:5000](http://localhost:5000).
3. Start the Vite React development server on [http://localhost:5173](http://localhost:5173).
4. Automatically open your browser (or you can navigate to the dev server link).

### Manual Setup
If you prefer running services manually in separate terminals:

**1. Start Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**2. Start Frontend:**
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

---

## AI Mechanics in Depth

### Same Product Detection (Clustering)
- Standardizes product titles (lowercase, removes punctuation).
- Converts titles to numerical arrays using `TfidfVectorizer`.
- Runs pairwise `cosine_similarity` checks between scraped titles.
- Rejects items if they have conflicting specifications extracted via regex (e.g. `128GB` and `256GB` or sizes `M` and `L`).
- Connects high-similarity matching items into a single `ProductGroup`.

### Recommendation Score Formula
For any deal, the score $S$ is calculated as:
$$S = (0.40 \times S_{\text{price}} + 0.25 \times S_{\text{rating}} + 0.15 \times S_{\text{discount}} + 0.10 \times S_{\text{delivery}} + 0.10 \times S_{\text{sentiment}}) \times 100$$
Where:
- $S_{\text{price}} = 1 - \frac{Price - Price_{\text{min}}}{Price_{\text{max}} - Price_{\text{min}}}$
- $S_{\text{rating}} = \frac{Rating}{5}$
- $S_{\text{discount}} = \frac{Discount\%}{100}$
- $S_{\text{delivery}} = 1 - \frac{DeliveryFee}{DeliveryFee_{\text{max}}}$
- $S_{\text{sentiment}} = \frac{\text{Sentiment} + 1}{2}$

## Latest Update

Project documentation updated in July 2026.