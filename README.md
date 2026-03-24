# 🎮 GameSearch — Mini Web Search Engine

**Lab 2.1 — Information Retrieval**

---

## Student
JOSE MANUEL NUÑEZ MITCHEL

---

## Domain: Video Games
I chose video games because it is a domain with rich, diverse text — reviews contain technical language (mechanics, systems, genres), narrative descriptions, and proper nouns (titles, characters, studios). This makes it a great corpus for testing retrieval algorithms, since queries can range from specific (e.g., "BM25 Elden Ring FromSoftware") to general (e.g., "open world RPG").

---

## Enhancement: E — TF-IDF vs BM25 Side-by-Side Comparison
Both ranking algorithms are computed for every query and displayed in parallel columns. This allows the user to see directly how each algorithm ranks documents differently for the same query. BM25 applies term frequency saturation and document length normalization (via k1=1.5, b=0.75), while TF-IDF uses normalized raw frequency against inverse document frequency. Differences in ranking reveal each algorithm's strengths and weaknesses.

---

## Project Structure

```
my-search-engine/
├── README.md
├── corpus.json          # 25 real video game documents with sources
├── search_engine.py     # Tokenizer, inverted index, BM25, TF-IDF
├── app.py               # Flask web server
├── templates/
│   ├── index.html       # Main search interface
│   └── index_view.html  # Inverted index visualization
├── static/
│   ├── style.css
│   └── main.js
└── requirements.txt
```

---

## How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USER/my-search-engine.git
cd my-search-engine
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
python app.py
```

### 5. Open your browser
```
http://127.0.0.1:5000
```

---

## Search Engine Components

| Component | Implementation |
|---|---|
| Tokenization | Regex-based, lowercase, removes punctuation |
| Stop words | Custom set of ~70 common English stop words |
| Stemming | Custom suffix-stripping stemmer (no external libraries) |
| Inverted Index | Dictionary of term → {doc_id: frequency} |
| BM25 | k1=1.5, b=0.75, standard Okapi BM25 formula |
| TF-IDF | Normalized TF × log(N/df) |
| Web Interface | Flask + vanilla JS, dark theme |

---

## Example Queries to Try
- `open world RPG`
- `FromSoftware difficult boss combat`
- `Nintendo Switch platformer`
- `battle royale multiplayer`
- `indie game farming simulation`

---

## Screenshots

<img width="1390" height="675" alt="image" src="https://github.com/user-attachments/assets/e4f6e6bd-5660-43e1-aac6-49137475af56" />


---

## Notes
- No external search libraries (Whoosh, Elasticsearch, Lucene) were used.
- The stemmer and stop word list are implemented from scratch.
- All 25 corpus documents are real, sourced from Wikipedia.
