"""Gateshead Local Plan retail centres — fetch, geometry, assignment.

Centres come from Gateshead Council's own public ArcGIS server (Local Plan
policies map, MSGP Policy 6 designations — keyless):

  * layer 21  Primary Shopping Areas   -> "Gateshead town centre"   (tier: town)
  * layer 29  District Shopping Centre -> 8 district centres        (tier: district)
  * layer 30  Local Shopping Centre    -> 15 local centres          (tier: local)
  * layer 32  Metrocentre Regional Shopping Centre                  (tier: destination)
  * layer 31  RW - Retail World (Team Valley)                       (tier: destination)

Assignment: a point belongs to a centre if it falls inside the designated
polygon or within BUFFER_M metres of its boundary (side streets and edges of
the designated frontage — an analytical judgement, logged in the assurance
note). Pure-python geometry: ray-casting point-in-polygon + point-to-segment
distance on a local-metres approximation; no extra dependencies.

Run standalone to probe the live service:  python centres.py
"""
from __future__ import annotations
import json
import math

import config as C

GIS_BASE = "https://gis.gateshead.gov.uk/server/rest/services/LDP21_MIL1/MapServer"
CENTRE_LAYERS = [
    (21, "town", None),                # Primary Shopping Areas (urban core)
    (29, "district", None),            # SITE attribute carries the name
    (30, "local", None),
    (32, "destination", "MetroCentre"),
    (31, "destination", "Retail World (Team Valley)"),
]
# Layers 31/32 are point (label) layers; approximate extents with a circle.
# Radii are an analytical judgement (assurance note): large regional shopping
# centre vs retail park. Destinations are context only — excluded from
# "high street" aggregates by tier.
DEST_RADIUS_M = {"MetroCentre": 500.0, "Retail World (Team Valley)": 350.0}
BUFFER_M = 150.0        # walkable fringe around the designated boundary
TIER_LABEL = {"town": "Town centre", "district": "District centre",
              "local": "Local centre", "destination": "Retail destination"}


def _fetch_layer(session, layer_id):
    url = f"{GIS_BASE}/{layer_id}/query"
    r = session.get(url, params={
        "where": "1=1", "outFields": "SITE,LAYER_NAME", "outSR": "4326",
        "returnGeometry": "true", "f": "json"}, timeout=C.HTTP_TIMEOUT)
    r.raise_for_status()
    js = r.json()
    if "error" in js:
        raise RuntimeError(f"layer {layer_id}: {js['error']}")
    return js.get("features", [])


def load_centres(session):
    """-> list of centres: {id, name, tier, rings, lat, lon} (rings in [lon,lat])."""
    centres = {}
    for layer_id, tier, forced_name in CENTRE_LAYERS:
        try:
            feats = _fetch_layer(session, layer_id)
        except Exception as e:
            raise RuntimeError(f"Gateshead GIS centres layer {layer_id} failed: {e}")
        for f in feats:
            name = forced_name or (f.get("attributes", {}).get("SITE") or "").strip()
            if tier == "town":
                name = "Gateshead town centre"
            if not name:
                continue
            geom = f.get("geometry") or {}
            rings = geom.get("rings") or []
            if not rings and "x" in geom and "y" in geom:   # point layer -> circle
                r = DEST_RADIUS_M.get(name, 300.0)
                cx, cy = geom["x"], geom["y"]
                rings = [[[cx + (r / _MPD_LON) * math.cos(a), cy + (r / _MPD_LAT) * math.sin(a)]
                          for a in [2 * math.pi * k / 32 for k in range(33)]]]
            key = name.lower()
            if key not in centres:
                centres[key] = {"name": name, "tier": tier, "rings": []}
            centres[key]["rings"].extend(rings)
    out = []
    for i, c in enumerate(sorted(centres.values(),
                                 key=lambda c: ({"town": 0, "district": 1, "local": 2, "destination": 3}[c["tier"]], c["name"]))):
        pts = [p for ring in c["rings"] for p in ring]
        if not pts:
            print(f"    ! centre '{c['name']}' ({c['tier']}) has no geometry — skipped")
            continue
        lon = sum(p[0] for p in pts) / len(pts)
        lat = sum(p[1] for p in pts) / len(pts)
        out.append({"id": f"c{i}", "name": c["name"], "tier": c["tier"],
                    "rings": c["rings"], "lat": round(lat, 5), "lon": round(lon, 5)})
    return out


# ---------------------------------------------------------------------------
# geometry (local-metres approximation around Gateshead, fine at borough scale)
# ---------------------------------------------------------------------------
_LAT0 = 54.95
_MPD_LAT = 111_320.0
_MPD_LON = 111_320.0 * math.cos(math.radians(_LAT0))

def _xy(lon, lat):
    return lon * _MPD_LON, lat * _MPD_LAT

def _pip(x, y, ring_xy):
    inside = False
    n = len(ring_xy)
    for i in range(n):
        x1, y1 = ring_xy[i]
        x2, y2 = ring_xy[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside

def _seg_dist(x, y, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


class CentreIndex:
    """Preprojected centres with a cheap bounding-box prefilter."""
    def __init__(self, centres, buffer_m=BUFFER_M):
        self.buffer = buffer_m
        self.centres = centres
        self._prep = []
        for c in centres:
            rings_xy = [[_xy(lon, lat) for lon, lat in ring] for ring in c["rings"]]
            xs = [p[0] for r in rings_xy for p in r]
            ys = [p[1] for r in rings_xy for p in r]
            bbox = (min(xs) - buffer_m, min(ys) - buffer_m, max(xs) + buffer_m, max(ys) + buffer_m)
            self._prep.append((c["id"], rings_xy, bbox))

    def assign(self, lat, lon):
        """-> centre id or None. Inside any ring, or within buffer of an edge."""
        x, y = _xy(lon, lat)
        best, best_d = None, self.buffer + 1
        for cid, rings_xy, (x0, y0, x1, y1) in self._prep:
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                continue
            for ring in rings_xy:
                if _pip(x, y, ring):
                    return cid
                for i in range(len(ring)):
                    d = _seg_dist(x, y, *ring[i], *ring[(i + 1) % len(ring)])
                    if d < best_d:
                        best_d, best = d, cid
        return best if best_d <= self.buffer else None


def centres_geojson(centres):
    """Map-ready FeatureCollection (polygons, WGS84)."""
    feats = []
    for c in centres:
        feats.append({"type": "Feature",
                      "properties": {"id": c["id"], "name": c["name"], "tier": c["tier"]},
                      "geometry": {"type": "MultiPolygon",
                                   "coordinates": [[ring] for ring in c["rings"]]}})
    return {"type": "FeatureCollection", "features": feats}


if __name__ == "__main__":
    import requests
    s = requests.Session()
    s.headers.update(C.HTTP_HEADERS)
    cs = load_centres(s)
    print(f"{len(cs)} centres")
    for c in cs:
        print(f"  {c['id']:>4} {TIER_LABEL[c['tier']]:<18} {c['name']:34} rings={len(c['rings'])} @ {c['lat']},{c['lon']}")
    idx = CentreIndex(cs)
    # probe: Gateshead High Street (town centre) and a Team Valley point
    print("High St test ->", idx.assign(54.9628, -1.6034))
    print("Team Valley test ->", idx.assign(54.9330, -1.6210))
