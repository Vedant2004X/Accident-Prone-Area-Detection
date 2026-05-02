[README (1).md](https://github.com/user-attachments/files/27295569/README.1.md)
# 🚨 Accident Prone Area Detection System

An end-to-end ML web application that detects accident-prone zones on a route and predicts crash severity in real time. Built with Flask, DBSCAN clustering, and a Random Forest classifier trained on real accident data.

---

## 🎯 What It Does

- Plots **accident black spots** on an interactive map using DBSCAN clustering
- Takes a **start and end location**, fetches the real driving route via OpenRouteService API
- Checks if the route passes through any danger zones and returns **HIGH / MEDIUM / LOW** risk alerts
- Predicts **crash severity** (Slight / Serious / Fatal) using a trained Random Forest model
- Supports **place name search** via geocoding (e.g. "Pune" → lat/lng)

---

## 🗂️ Project Structure

```
accident-detection/
│
├── app/
│   ├── __init__.py         # Flask app factory
│   ├── routes.py           # API endpoints
│   └── templates/
│       └── index.html      # Frontend (Leaflet.js map UI)
│
├── ml/
│   ├── clustering.py       # DBSCAN black spot detection
│   ├── preprocess.py       # Data cleaning & encoding
│   ├── risk_model.py       # Random Forest training & prediction
│   └── route_checker.py    # Route fetching + danger zone matching
│
├── data/
│   ├── accidents.csv           # Raw accident dataset
│   ├── cleaned_accidents.csv   # After preprocessing
│   ├── geocoded_accidents.csv  # With lat/lng coordinates
│   └── black_spots.json        # DBSCAN output (precomputed clusters)
│
├── models/
│   ├── risk_model.pkl      # Trained Random Forest model
│   └── feature_cols.pkl    # Feature column names
│
├── app.py                  # Entry point
└── requirements.txt
```

---

## ⚙️ ML Pipeline

### 1. Preprocessing (`preprocess.py`)
- Cleans raw accident CSV — drops nulls, encodes categoricals
- Geocodes accident locations to lat/lng coordinates

### 2. DBSCAN Clustering (`clustering.py`)
- Uses **Haversine distance** with `eps=40km`, `min_samples=8`
- Each cluster becomes a **black spot** with:
  - Risk score = weighted combo of severity + casualties + accident count
  - Risk level: HIGH (≥6), MEDIUM (≥3.5), LOW (<3.5)
  - Metadata: top weather condition, road type, cause, junction type

### 3. Random Forest Classifier (`risk_model.py`)
- **Target**: Accident severity (1=Slight, 2=Serious, 3=Fatal)
- **Features**: hour, day, weather, road type, road condition, lighting, vehicles, casualties, junction, cause
- **Config**: 200 estimators, max depth 12, balanced class weights
- Saved via `joblib` for inference

### 4. Route Risk Checker (`route_checker.py`)
- Fetches driving route from OpenRouteService API
- Uses **Shapely LineString** to check if any black spot falls within 25km buffer of route
- Returns sorted alerts + overall risk summary

---

## 🚀 How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your ORS API key
In `ml/route_checker.py`, replace:
```python
ORS_API_KEY = "YOUR_FREE_API_KEY_HERE"
```
Get a free key at [openrouteservice.org](https://openrouteservice.org)

### 3. (Optional) Retrain the model
```bash
python ml/preprocess.py
python ml/clustering.py
python ml/risk_model.py
```

### 4. Run the Flask app
```bash
python app.py
```

Visit `http://localhost:5000`

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Map UI |
| `POST` | `/api/check-route` | Check route for danger zones |
| `GET` | `/api/black-spots` | Get all accident clusters |
| `POST` | `/api/geocode` | Convert place name to lat/lng |

### Example — Check Route
```json
POST /api/check-route
{
  "start_lat": 28.6139,
  "start_lng": 77.2090,
  "end_lat": 19.0550,
  "end_lng": 72.8692
}
```

```json
Response:
{
  "total_danger_zones": 3,
  "summary": {
    "overall_risk": "HIGH",
    "message": "🚨 2 HIGH risk zone(s) on your route. Drive with caution!",
    "color": "red"
  },
  "alerts": [...],
  "route": [...]
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask, Python 3.12 |
| ML | Scikit-learn (DBSCAN, Random Forest), Pandas, NumPy |
| Geospatial | Shapely, GeoPandas, Geopy |
| Routing API | OpenRouteService |
| Frontend | Leaflet.js, HTML/CSS/JS |
| Model Storage | Joblib |

---

## 👤 Author

**Vedant** — B.Tech CSE (2027), NMIET Pune  
Intel Unnati Industrial Training Alumnus  
[GitHub](https://github.com/your-username) • [LinkedIn](https://linkedin.com/in/your-profile)
