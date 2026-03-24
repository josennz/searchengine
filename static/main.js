const queryInput = document.getElementById("query");
const searchBtn = document.getElementById("search-btn");
const bm25Div = document.getElementById("bm25-results");
const tfidfDiv = document.getElementById("tfidf-results");
const metaDiv = document.getElementById("search-meta");
const container = document.getElementById("results-container");
const noResults = document.getElementById("no-results");
const loading = document.getElementById("loading");

function highlight(text, terms) {
  if (!terms || terms.length === 0) return text;
  const escaped = terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  const regex = new RegExp(`(${escaped.join("|")})`, "gi");
  return text.replace(regex, "<mark>$1</mark>");
}

function renderCard(item, rank, scoreClass, scoreLabel) {
  const highlightedText = highlight(item.text, window._queryTerms || []);
  const highlightedTitle = highlight(item.title, window._queryTerms || []);
  return `
    <div class="result-card">
      <div class="result-rank">#${rank}</div>
      <div class="result-title">${highlightedTitle}</div>
      <div class="result-meta">
        <span class="result-score ${scoreClass}">${scoreLabel}: ${item.score}</span>
        <span class="result-category">${item.category}</span>
      </div>
      <div class="result-text">${highlightedText}</div>
      <div class="result-source"><a href="${item.source}" target="_blank" rel="noopener">Source ↗</a></div>
    </div>`;
}

async function doSearch() {
  const q = queryInput.value.trim();
  if (!q) return;

  loading.classList.remove("hidden");
  container.classList.add("hidden");
  noResults.classList.add("hidden");
  metaDiv.classList.add("hidden");

  try {
    const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
    const data = await res.json();

    loading.classList.add("hidden");

    if (!data.bm25 || data.bm25.length === 0) {
      noResults.classList.remove("hidden");
      return;
    }

    window._queryTerms = data.query_terms || [];

    metaDiv.textContent = `Query: "${q}" → tokens: [${data.query_terms.join(", ")}] — searched in ${data.time} ms`;
    metaDiv.classList.remove("hidden");

    bm25Div.innerHTML = data.bm25
      .map((item, i) => renderCard(item, i + 1, "bm25-score", "BM25"))
      .join("");

    tfidfDiv.innerHTML = data.tfidf
      .map((item, i) => renderCard(item, i + 1, "tfidf-score", "TF-IDF"))
      .join("");

    container.classList.remove("hidden");

  } catch (err) {
    loading.classList.add("hidden");
    noResults.classList.remove("hidden");
    console.error(err);
  }
}

searchBtn.addEventListener("click", doSearch);
queryInput.addEventListener("keydown", e => { if (e.key === "Enter") doSearch(); });
