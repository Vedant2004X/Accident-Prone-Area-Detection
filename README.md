[README (1).md](https://github.com/user-attachments/files/27295569/README.1.md)
# 🚨 Accident Prone Area Detection System

An end-to-end ML web application that detects accident-prone zones on a route and predicts crash severity in real time. Built with Flask, DBSCAN clustering, and a Random Forest classifier trained on real accident data.

---
## 📌 Overview

Road accidents are often concentrated in specific high-risk zones due to factors like traffic density, road conditions, and environmental variables.

This project analyzes historical accident data to:
- Detect **accident hotspots (black spots)**
- Evaluate **route safety**
- Predict **severity of potential crashes**

👉 Goal: Assist users in making **safer travel decisions**

---

## ✨ Key Features

| Feature | Description |
|--------|------------|
| 1. Accident Hotspot Detection | Uses DBSCAN clustering to identify high-risk zones |
| 2. Route Risk Analysis | Checks if a route passes through dangerous areas |
| 3. Risk Alerts | Classifies routes as HIGH / MEDIUM / LOW risk |
| 4. Severity Prediction | Predicts crash severity (Slight / Serious / Fatal) |
| 5. Geocoding Support | Converts place names into coordinates |

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
## How it Works
## ML Pipeline

### 1. Data Preprocessing (`preprocess.py`)
- Cleans raw data set (removing missing values, encoding categoricals) 
- Geocoding accident sites to lat/lon coordinates

### 2. DBSCAN Clustering (`clustering.py`)
- Applies **Haversine Distance** algorithm with `eps=40km` and `min_samples=8` 
- Every cluster is a **black spot** having:
  - A **Risk Score** (weighted average of severity, casualties, and accidents)
  - **Risk Level** (HIGH ≥6, MEDIUM ≥3.5, LOW <3.5)
  - Meta-data includes top weather condition, road type, accident cause, and junction type

### 3. Random Forest Model (`risk_model.py`) 
- **Target Variable**: Severity (1=Slight, 2=Serious, 3=Fatal)
- **Features Used**: hour, day, weather, road type, road surface, lighting, number of vehicles involved, number of casualties, junction and cause of accident
- **Config**: 200 estimators, maximum tree depth of 12, balance classes
- Model serialized using `joblib`

### 4. Checking Risks On The Route (`route_checker.py`) 
- Gets driving route data from OpenRouteService API 
- Uses **Shapely LineString** to see if any of the black spots is within a 25 km buffer around the route
- Gives sorted alerts and total risk assessment

---

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
---

## 🚀 How to Run

## ⚙️ Installation & Setup
### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add OpenRouteService API key
In `ml/route_checker.py`, replace:
```python
ORS_API_KEY = "YOUR_FREE_API_KEY_HERE"
```
Get a free key from: [openrouteservice.org](https://openrouteservice.org)

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

| Method | Endpoint           | Purpose                         |
| ------ | ------------------ | ------------------------------- |
| GET    | `/`                | Load map interface              |
| POST   | `/api/check-route` | Check route risk                |
| GET    | `/api/black-spots` | Retrieve accident clusters      |
| POST   | `/api/geocode`     | Convert location to coordinates |


### Example — Check Route (API Response)
## Request
```json
POST /api/check-route
{
  "start_lat": 28.6139,
  "start_lng": 77.2090,
  "end_lat": 19.0550,
  "end_lng": 72.8692
}
```
## Response
```json
Response:
{
  "total_danger_zones": 3,
  "summary": {
    "overall_risk": "HIGH",
    "message": "2 HIGH risk zone(s) on your route. Drive with caution!",
    "color": "red"
  },
  "alerts": [...],
  "route": [...]
}
```
---
## 📸 Screenshots
🗺️ Map Interface

<img width="1920" height="905" alt="Screenshot 2026-05-15 113240" src="https://github.com/user-attachments/assets/b340685e-5482-458c-9ec1-5ed1556ced0c" />

🚦 Route Risk Detection

<img width="1920" height="917" alt="Screenshot 2026-05-15 121040" src="https://github.com/user-attachments/assets/5ab01b86-61f3-4b75-9086-21bdcaf1522f" />

📊 Prediction Output

<img width="1920" height="912" alt="Screenshot 2026-05-15 121150" src="https://github.com/user-attachments/assets/1053fb20-60e1-47a9-92f2-8da901750944" />

<img width="1920" height="908" alt="Screenshot 2026-05-15 113900" src="https://github.com/user-attachments/assets/a63ac702-7cd6-40fd-867c-a1a411e0beb1" />

---
---

## 🚧 Future Improvements
- Real-time traffic integration
- Live weather-based risk updates
- Mobile application version
- Voice-based alerts
- Deep learning models
- Cloud deployment (AWS / Render)

---

## 👥 Team & Contributions

This project was developed as part of a college project.

| Name | Role | Contribution |
|------|------|-------------|
| Vedant | Lead Developer | Designed and implemented the full system including ML models, clustering, backend APIs, and integration |
| Trushna | Research & Documentation | Contributed to research paper development, system analysis,added features and improved README |
| Piyush | Research & Analysis | Assisted in research work, data understanding, and preparation of academic documentation |

## 🎓 Academic Context

This project was developed as part of academic coursework, focusing on applying machine learning and geospatial analysis to real-world problems like accident detection and risk prediction.

📌 Note: While the core system development was led by the primary developer, supporting members contributed to research, analysis, and documentation.
