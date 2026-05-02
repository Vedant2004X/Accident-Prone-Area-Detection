import json, requests
from shapely.geometry import Point, LineString

ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjFkYmI4YmM3ZGJmZDQ3NTM4ZDRiYzcxM2U3YjNjMjMxIiwiaCI6Im11cm11cjY0In0="

# Time-based risk multipliers (hour → multiplier)
TIME_RISK = {
    0:1.8, 1:2.0, 2:2.0, 3:1.9, 4:1.7, 5:1.4,
    6:1.2, 7:1.3, 8:1.4, 9:1.1, 10:1.0, 11:1.0,
    12:1.1, 13:1.0, 14:1.0, 15:1.1, 16:1.2, 17:1.4,
    18:1.5, 19:1.6, 20:1.7, 21:1.8, 22:1.8, 23:1.8
}

# Weather-based risk multipliers
WEATHER_RISK = {
    "Clear":  1.0,
    "Cloudy": 1.1,
    "Rainy":  1.5,
    "Foggy":  1.8,
    "Stormy": 2.0,
    "Hazy":   1.3,
    "Windy":  1.2,
    "Snow":   2.2
}

def get_route(start_lat, start_lng, end_lat, end_lng):
    url     = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body    = {"coordinates": [[start_lng, start_lat], [end_lng, end_lat]]}
    try:
        res    = requests.post(url, json=body, headers=headers, timeout=10)
        data   = res.json()
        coords = data["features"][0]["geometry"]["coordinates"]
        return [(lat, lng) for lng, lat in coords]
    except Exception as e:
        print("Route API error:", e)
        steps = 100
        lats  = [start_lat + (end_lat - start_lat) * i/steps for i in range(steps+1)]
        lngs  = [start_lng + (end_lng - start_lng) * i/steps for i in range(steps+1)]
        return list(zip(lats, lngs))


def check_route_for_accidents(route_coords, black_spots_path="data/black_spots.json",
                               buffer_km=25, hour=12, weather="Clear"):
    with open(black_spots_path) as f:
        black_spots = json.load(f)

    route_line    = LineString([(lng, lat) for lat, lng in route_coords])
    start         = route_coords[0]
    end           = route_coords[-1]
    exclusion_deg = 100 / 111.0
    buffer_deg    = buffer_km / 111.0

    # Get multipliers
    time_mult    = TIME_RISK.get(hour, 1.0)
    weather_mult = WEATHER_RISK.get(weather, 1.0)
    combined     = round(time_mult * weather_mult, 2)

    alerts = []
    for spot in black_spots:
        spot_point  = Point(spot["lng"], spot["lat"])
        dist_start  = ((spot["lat"] - start[0])**2 + (spot["lng"] - start[1])**2)**0.5
        dist_end    = ((spot["lat"] - end[0])**2   + (spot["lng"] - end[1])**2)**0.5

        if dist_start < exclusion_deg or dist_end < exclusion_deg:
            continue
        if route_line.distance(spot_point) >= buffer_deg:
            continue

        # Adjust risk score by time + weather
        adjusted = round(min(10, spot["risk_score"] * combined), 1)
        level    = "HIGH" if adjusted >= 6.5 else "MEDIUM" if adjusted >= 3.5 else "LOW"

        alerts.append({**spot,
            "risk_score":    adjusted,
            "risk_level":    level,
            "time_mult":     time_mult,
            "weather_mult":  weather_mult,
        })

    return sorted(alerts, key=lambda x: x["risk_score"], reverse=True)


def get_route_summary(alerts):
    if not alerts:
        return {"overall_risk":"LOW",
                "message":"✅ Route looks safe! No accident-prone zones detected.",
                "color":"green"}
    high = sum(1 for a in alerts if a["risk_level"] == "HIGH")
    med  = sum(1 for a in alerts if a["risk_level"] == "MEDIUM")
    if high > 0:
        return {"overall_risk":"HIGH",
                "message":f"🚨 {high} HIGH risk zone(s) on your route. Drive with extreme caution!",
                "color":"red"}
    elif med > 0:
        return {"overall_risk":"MEDIUM",
                "message":f"⚠️ {med} moderate risk zone(s) detected. Stay alert.",
                "color":"orange"}
    return {"overall_risk":"LOW",
            "message":"🟢 Route is relatively safe. Drive carefully.",
            "color":"green"}