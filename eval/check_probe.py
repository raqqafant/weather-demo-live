import json
from datetime import datetime

data = json.load(open("out/probe.json", encoding="utf-8"))
assert data["source_url"].startswith("https://")
assert len(data["items"]) >= 1, "no items"

for it in data["items"]:
    assert it["title"].strip(), "empty title"
    d = it["date"].replace("Z", "+00:00")
    datetime.fromisoformat(d)
    # Domain assertion: a plausible air temperature for Hamar (deg C)
    assert -50 <= it["air_temperature"] <= 45, f"implausible temp {it['air_temperature']}"

# Domain assertion: data comes from MET Norway
assert "api.met.no" in data["source_url"], "source is not MET Norway"
print("PASS")
