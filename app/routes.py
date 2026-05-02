from flask import Blueprint, request, jsonify, render_template
from ml.route_checker import get_route, check_route_for_accidents, get_route_summary
from geopy.geocoders import Nominatim
import json, datetime

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@bp.route("/api/geocode", methods=["POST"])
def geocode():
    data = request.json
    place = data.get("place", "")
    geolocator = Nominatim(user_agent="accident_detector_india")
    try:
        location = geolocator.geocode(place + ", India")
        if location:
            return jsonify({"lat": location.latitude, "lng": location.longitude, "found": True})
        return jsonify({"found": False})
    except:
        return jsonify({"found": False})

@bp.route("/api/check-route", methods=["POST"])
def check_route():
    data      = request.json
    start_lat = float(data["start_lat"])
    start_lng = float(data["start_lng"])
    end_lat   = float(data["end_lat"])
    end_lng   = float(data["end_lng"])
    hour      = int(data.get("hour",    datetime.datetime.now().hour))
    weather   = data.get("weather", "Clear")

    route_coords = get_route(start_lat, start_lng, end_lat, end_lng)
    alerts       = check_route_for_accidents(route_coords, hour=hour, weather=weather)
    summary      = get_route_summary(alerts)

    return jsonify({
        "route":              [[lat, lng] for lat, lng in route_coords],
        "alerts":             alerts,
        "total_danger_zones": len(alerts),
        "summary":            summary
    })

@bp.route("/api/black-spots", methods=["GET"])
def black_spots():
    with open("data/black_spots.json") as f:
        spots = json.load(f)
    return jsonify(spots)

@bp.route("/api/dashboard-stats", methods=["GET"])
def dashboard_stats():
    import pandas as pd
    df = pd.read_csv("data/geocoded_accidents.csv")
    with open("data/black_spots.json") as f:
        spots = json.load(f)

    # Top dangerous highways
    top_highways = (
        df.groupby("highway")
        .agg(accidents=("severity","count"), fatalities=("Number of Fatalities","sum"))
        .reset_index()
        .sort_values("fatalities", ascending=False)
        .head(10)
        .to_dict(orient="records")
    )

    # Accidents by hour
    by_hour = df.groupby("hour").size().reset_index(name="count")
    by_hour = by_hour.to_dict(orient="records")

    # Accidents by weather
    by_weather = df.groupby("Weather Conditions").size().reset_index(name="count")
    by_weather = by_weather.sort_values("count", ascending=False).to_dict(orient="records")

    # Accidents by severity
    by_severity = df.groupby("Accident Severity").size().reset_index(name="count")
    by_severity = by_severity.to_dict(orient="records")

    # Accidents by road type
    by_road = df.groupby("Road Type").size().reset_index(name="count")
    by_road = by_road.sort_values("count", ascending=False).to_dict(orient="records")

    # Summary numbers
    total_accidents  = len(df)
    total_fatalities = int(df["Number of Fatalities"].sum())
    high_risk_zones  = sum(1 for s in spots if s["risk_level"] == "HIGH")
    total_zones      = len(spots)

    return jsonify({
        "top_highways":     top_highways,
        "by_hour":          by_hour,
        "by_weather":       by_weather,
        "by_severity":      by_severity,
        "by_road":          by_road,
        "total_accidents":  total_accidents,
        "total_fatalities": total_fatalities,
        "high_risk_zones":  high_risk_zones,
        "total_zones":      total_zones
    })