import re

page = open("out/index.html", encoding="utf-8").read()
assert "<script" not in page.lower(), "page must be pure HTML (no JavaScript)"
assert "Hamar" in page, "location missing"
assert "MET Norway" in page, "MET attribution missing (CC BY 4.0)"
rows = page.count('class="day-row"')
assert 5 <= rows <= 10, f"expected 5-10 day rows, got {rows}"
temps = [int(t) for t in re.findall(r"(-?\d+)°", page)]
assert temps, "no temperatures"
assert all(-50 <= t <= 45 for t in temps), f"implausible temperature in {temps}"
print("PASS")
