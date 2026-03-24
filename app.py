from flask import Flask, render_template, request, jsonify
from search_engine import SearchEngine

app = Flask(__name__)

engine = SearchEngine()
engine.load_corpus("corpus.json")

@app.route("/")
def index():
    stats = engine.stats()
    return render_template("index.html", stats=stats)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400
    results = engine.search(query, top_k=10)
    return jsonify(results)

@app.route("/index-view")
def index_view():
    stats = engine.stats()
    index_data = engine.get_index_data()
    return render_template("index_view.html", stats=stats, index_data=index_data)

if __name__ == "__main__":
    app.run(debug=True)
