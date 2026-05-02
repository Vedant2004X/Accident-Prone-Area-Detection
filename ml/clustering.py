import pandas as pd
import numpy as np
import json
from sklearn.cluster import DBSCAN

EARTH_RADIUS_KM = 6371.0

def get_black_spots(filepath="data/geocoded_accidents.csv", eps_km=8, min_samples=4):
    df = pd.read_csv(filepath)
    print(f"Clustering {len(df)} accident points...")

    coords = np.radians(df[["latitude","longitude"]].values)
    db = DBSCAN(
        eps=eps_km / EARTH_RADIUS_KM,
        min_samples=min_samples,
        algorithm="ball_tree",
        metric="haversine"
    )
    df["cluster"] = db.fit_predict(coords)

    total = df[df["cluster"] != -1]["cluster"].nunique()
    noise = (df["cluster"] == -1).sum()
    print(f"Clusters: {total} | Noise points: {noise}")

    black_spots = []
    clustered   = df[df["cluster"] != -1]

    for cid in sorted(clustered["cluster"].unique()):
        group = clustered[clustered["cluster"] == cid]

        avg_lat          = group["latitude"].mean()
        avg_lng          = group["longitude"].mean()
        avg_severity     = group["severity"].mean()
        total_fatalities = int(group["Number of Fatalities"].sum()) if "Number of Fatalities" in group.columns else 0
        total_casualties = int(group["num_casualties"].sum())
        count            = len(group)

        top_highway = group["highway"].mode()[0]      if "highway"      in group.columns else "NH"
        top_state   = group["state_region"].mode()[0] if "state_region" in group.columns else "India"
        top_weather = group["Weather Conditions"].mode()[0] if "Weather Conditions" in group.columns else "N/A"
        top_road    = group["Road Type"].mode()[0]          if "Road Type"          in group.columns else "N/A"

        display_name = top_highway.replace("_", " ").replace("NH", "NH-")
        radius_m     = int(min(3000 + count * 400, 15000))

        black_spots.append({
            "cluster_id":       int(cid),
            "lat":              round(avg_lat, 5),
            "lng":              round(avg_lng, 5),
            "count":            count,
            "avg_severity":     round(avg_severity, 2),
            "total_fatalities": total_fatalities,
            "total_casualties": total_casualties,
            "risk_score":       0,   # filled after normalization
            "risk_level":       "LOW",
            "top_weather":      top_weather,
            "top_road_type":    top_road,
            "state":            top_state,
            "highway":          display_name,
            "radius_m":         radius_m
        })

    # ── Normalize risk scores across all clusters ─────────────────────
    arr_sev  = np.array([s["avg_severity"]     for s in black_spots])
    arr_fat  = np.array([s["total_fatalities"] for s in black_spots])
    arr_cas  = np.array([s["total_casualties"] for s in black_spots])
    arr_cnt  = np.array([s["count"]            for s in black_spots])

    def norm(arr):
        mn, mx = arr.min(), arr.max()
        return np.zeros(len(arr)) if mx == mn else (arr - mn) / (mx - mn)

    n_sev = norm(arr_sev)
    n_fat = norm(arr_fat)
    n_cas = norm(arr_cas)
    n_cnt = norm(arr_cnt)

    for i, spot in enumerate(black_spots):
        raw   = (n_sev[i] * 3.5) + (n_fat[i] * 3.5) + (n_cas[i] * 2.0) + (n_cnt[i] * 1.0)
        score = round(raw, 1)
        spot["risk_score"] = score
        spot["risk_level"] = "HIGH" if score >= 6.5 else "MEDIUM" if score >= 3.5 else "LOW"

    black_spots = sorted(black_spots, key=lambda x: x["risk_score"], reverse=True)

    with open("data/black_spots.json","w") as f:
        json.dump(black_spots, f, indent=2)

    print(f"\n✅ Saved {len(black_spots)} black spots")
    print("\nTop 10 Danger Zones:")
    for s in black_spots[:10]:
        print(f"  [{s['risk_level']}] {s['highway']} | {s['state']} | Risk: {s['risk_score']}/10 | Accidents: {s['count']}")

    return black_spots


if __name__ == "__main__":
    get_black_spots()