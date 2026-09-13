from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import json, os, sqlite3
from predict import predict_price

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "database", "predictions.db")
DATASET = os.path.join(BASE, "dataset.csv")
METRICS = os.path.join(BASE, "model_metrics.json")
EVALUATION = os.path.join(BASE, "evaluation.pkl")

def init_db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        location TEXT, area REAL, bedrooms INTEGER, bathrooms INTEGER,
        furnishing TEXT, property_type TEXT, predicted_price REAL)""")
    con.commit(); con.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.get_json()
    required = ["Location","Area","Bedrooms","Bathrooms","Floors","Property_Age",
                "Parking","Kitchen","Balcony","Furnishing","Property_Type","Construction_Quality"]
    if not all(k in data for k in required):
        return jsonify({"error":"Please provide all property details."}), 400
    try:
        data["Area"]=float(data["Area"])
        data["Bedrooms"]=int(data["Bedrooms"])
        data["Bathrooms"]=int(data["Bathrooms"])
        data["Floors"]=int(data["Floors"])
        data["Property_Age"]=int(data["Property_Age"])
        data["Balcony"]=int(data["Balcony"])
        if data["Area"] <= 0 or min(data["Bedrooms"],data["Bathrooms"],data["Floors"],data["Balcony"]) < 0:
            raise ValueError()
        price = predict_price(data)
        df = pd.read_csv(DATASET)
        loc_avg = float(df[df.Location==data["Location"]]["Price"].mean())
        if np.isnan(loc_avg): loc_avg=float(df.Price.mean())
        lower, upper = price*0.94, price*1.06
        con=sqlite3.connect(DB)
        con.execute("INSERT INTO predictions(location,area,bedrooms,bathrooms,furnishing,property_type,predicted_price) VALUES(?,?,?,?,?,?,?)",
                    (data["Location"],data["Area"],data["Bedrooms"],data["Bathrooms"],data["Furnishing"],data["Property_Type"],price))
        con.commit(); con.close()
        return jsonify({"price":price,"lower":lower,"upper":upper,"market_average":loc_avg,
                        "difference_pct":((price-loc_avg)/loc_avg*100 if loc_avg else 0)})
    except Exception as e:
        app.logger.exception("Prediction Error")
        return jsonify({"error":f"Prediction failed: {type(e).__name__}: {e}"}), 500

@app.route("/api/analytics")
def analytics():
    df=pd.read_csv(DATASET)
    location=df.groupby("Location")["Price"].mean().sort_values(ascending=False)
    return jsonify({
        "total":len(df),"average":float(df.Price.mean()),"minimum":float(df.Price.min()),
        "maximum":float(df.Price.max()),"avg_area":float(df.Area.mean()),
        "locations":location.index.tolist(),"location_prices":location.values.tolist(),
        "area":df.Area.tolist(),"price":df.Price.tolist(),
        "bedrooms":df.groupby("Bedrooms")["Price"].mean().index.tolist(),
        "bedroom_prices":df.groupby("Bedrooms")["Price"].mean().values.tolist()
    })

@app.route("/api/model-performance")
def performance():
    with open(METRICS) as f: return jsonify(json.load(f))

@app.route("/api/evaluation")
def evaluation():
    d=__import__("joblib").load(EVALUATION)
    return jsonify({"actual":d["test_actual"],"predicted":d["test_predicted"]})

@app.route("/api/history")
def history():
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row
    rows=[dict(r) for r in con.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 50")]
    con.close(); return jsonify(rows)

@app.route("/api/history/clear", methods=["DELETE"])
def clear_history():
    con=sqlite3.connect(DB); con.execute("DELETE FROM predictions"); con.commit(); con.close()
    return jsonify({"ok":True})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=False)
