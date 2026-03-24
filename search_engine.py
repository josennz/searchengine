import json
import math
import re
import time
from collections import defaultdict

# Simple stop words list (no external deps)
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "its", "was", "are", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall", "can",
    "not", "no", "nor", "so", "yet", "both", "either", "neither", "each",
    "few", "more", "most", "other", "some", "such", "than", "too", "very",
    "just", "as", "also", "that", "this", "these", "those", "they", "them",
    "their", "there", "then", "when", "where", "which", "who", "whom",
    "what", "how", "if", "while", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "up", "down",
    "out", "off", "over", "under", "again", "further", "once", "here",
    "all", "any", "i", "me", "my", "we", "our", "you", "your", "he",
    "she", "his", "her", "him", "us", "s", "re", "ve", "ll", "d", "t"
}

# Minimal suffix-stripping stemmer (Porter-like, no NLTK needed)
def stem(word):
    if len(word) <= 3:
        return word
    suffixes = [
        ("ational", "ate"), ("tional", "tion"), ("enci", "ence"),
        ("anci", "ance"), ("izer", "ize"), ("ising", "ise"),
        ("izing", "ize"), ("ising", "ise"), ("ational", "ate"),
        ("alism", "al"), ("iveness", "ive"), ("fulness", "ful"),
        ("ousness", "ous"), ("ization", "ize"), ("isation", "ise"),
        ("ation", "ate"), ("ness", ""), ("ment", ""), ("ings", ""),
        ("ing", ""), ("edly", ""), ("edly", "ed"), ("ness", ""),
        ("ful", ""), ("ous", ""), ("ive", ""), ("ize", ""),
        ("ise", ""), ("ers", "er"), ("ies", "y"), ("ied", "y"),
        ("tion", "t"), ("sion", "s"), ("ness", ""), ("ed", ""),
        ("es", ""), ("er", ""), ("ly", ""), ("al", ""),
    ]
    for suffix, replacement in suffixes:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[:-len(suffix)] + replacement
    if word.endswith("s") and not word.endswith("ss") and len(word) > 4:
        return word[:-1]
    return word


def tokenize(text):
    """Clean, tokenize, remove stop words, and stem."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 1]
    tokens = [stem(t) for t in tokens]
    return tokens


class SearchEngine:
    def __init__(self):
        self.documents = []
        self.inverted_index = defaultdict(dict)   # term -> {doc_id: freq}
        self.doc_lengths = {}                      # doc_id -> token count
        self.avg_doc_length = 0
        self.vocabulary = set()

        # BM25 parameters
        self.k1 = 1.5
        self.b = 0.75

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------
    def load_corpus(self, path="corpus.json"):
        with open(path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
        self._build_index()

    def _build_index(self):
        total_length = 0
        for doc in self.documents:
            doc_id = doc["id"]
            tokens = tokenize(doc["title"] + " " + doc["text"])
            self.doc_lengths[doc_id] = len(tokens)
            total_length += len(tokens)

            freq_map = defaultdict(int)
            for token in tokens:
                freq_map[token] += 1

            for term, freq in freq_map.items():
                self.inverted_index[term][doc_id] = freq
                self.vocabulary.add(term)

        n = len(self.documents)
        self.avg_doc_length = total_length / n if n else 1

    # ------------------------------------------------------------------
    # BM25 scoring
    # ------------------------------------------------------------------
    def bm25_score(self, query_terms, doc_id):
        score = 0.0
        N = len(self.documents)
        dl = self.doc_lengths.get(doc_id, 0)

        for term in query_terms:
            if term not in self.inverted_index:
                continue
            postings = self.inverted_index[term]
            if doc_id not in postings:
                continue

            tf = postings[doc_id]
            df = len(postings)

            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
            tf_norm = (tf * (self.k1 + 1)) / (
                tf + self.k1 * (1 - self.b + self.b * dl / self.avg_doc_length)
            )
            score += idf * tf_norm
        return score

    # ------------------------------------------------------------------
    # TF-IDF scoring
    # ------------------------------------------------------------------
    def tfidf_score(self, query_terms, doc_id):
        score = 0.0
        N = len(self.documents)
        dl = self.doc_lengths.get(doc_id, 1)

        for term in query_terms:
            if term not in self.inverted_index:
                continue
            postings = self.inverted_index[term]
            if doc_id not in postings:
                continue

            tf = postings[doc_id] / dl          # normalized TF
            df = len(postings)
            idf = math.log(N / df)
            score += tf * idf
        return score

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def search(self, query, top_k=10):
        start = time.time()
        query_terms = tokenize(query)

        if not query_terms:
            return {"bm25": [], "tfidf": [], "query_terms": [], "time": 0.0}

        # Gather candidate docs (union of posting lists)
        candidates = set()
        for term in query_terms:
            if term in self.inverted_index:
                candidates.update(self.inverted_index[term].keys())

        # Score with both algorithms
        bm25_scores = []
        tfidf_scores = []

        doc_map = {doc["id"]: doc for doc in self.documents}

        for doc_id in candidates:
            bm25 = self.bm25_score(query_terms, doc_id)
            tfidf = self.tfidf_score(query_terms, doc_id)
            doc = doc_map[doc_id]
            entry = {
                "id": doc_id,
                "title": doc["title"],
                "text": doc["text"][:300] + "..." if len(doc["text"]) > 300 else doc["text"],
                "source": doc["source"],
                "category": doc["category"],
            }
            bm25_scores.append({**entry, "score": round(bm25, 4)})
            tfidf_scores.append({**entry, "score": round(tfidf, 6)})

        bm25_scores.sort(key=lambda x: x["score"], reverse=True)
        tfidf_scores.sort(key=lambda x: x["score"], reverse=True)

        elapsed = round((time.time() - start) * 1000, 2)  # ms

        return {
            "bm25": bm25_scores[:top_k],
            "tfidf": tfidf_scores[:top_k],
            "query_terms": query_terms,
            "time": elapsed,
        }

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------
    def stats(self):
        return {
            "total_documents": len(self.documents),
            "vocabulary_size": len(self.vocabulary),
            "avg_doc_length": round(self.avg_doc_length, 1),
        }

    def get_index_data(self):
        """Return top terms for index visualization."""
        terms = []
        for term, postings in self.inverted_index.items():
            terms.append({
                "term": term,
                "df": len(postings),
                "postings": {str(k): v for k, v in sorted(postings.items())}
            })
        terms.sort(key=lambda x: x["df"], reverse=True)
        return terms[:200]  # top 200 most common terms
