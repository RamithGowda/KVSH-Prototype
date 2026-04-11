from flask import Flask, request, jsonify, render_template_string
from engine import recommend

app = Flask(__name__)

HTML = open("index.html").read()

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/recommend", methods=["POST"])
def get_recommendation():
    data = request.json

    category     = data.get("category", "default")
    amount       = float(data.get("amount", 0))
    user_cards   = data.get("cards", [])
    caps_used    = data.get("caps_used", {})   # e.g. {"hdfc_millennia": 700}

    if amount <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400
    if not user_cards:
        return jsonify({"error": "Select at least one card"}), 400

    result = recommend(category, amount, user_cards, caps_used)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
