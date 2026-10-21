"""Stage 2: turn the MET forecast into a static page, out/index.html.

Pure Python, no JavaScript in the output. Same design as the original page.

Usage:
  python3 harness/render.py   # reads fixtures/met_hamar.json
"""
import json
import shutil
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "fixtures" / "met_hamar.json"
OUT = ROOT / "out" / "index.html"
ICONS = Path(__file__).resolve().parent / "icons"   # metno/weathericons, MIT
CSS = (Path(__file__).resolve().parent / "style.css").read_text(encoding="utf-8")

TZ = ZoneInfo("Europe/Oslo")
LOCATION = "Hamar, Norway"
DAYS = 10

SYMBOL_EMOJI = {
    "clearsky": "☀️", "fair": "🌤️", "partlycloudy": "⛅", "cloudy": "☁️", "fog": "🌫️",
    "lightrain": "🌦️", "rain": "🌧️", "heavyrain": "🌧️", "rainshowers": "🌦️",
    "heavyrainshowers": "🌧️", "sleet": "🌨️", "lightsleet": "🌨️", "snow": "❄️",
    "lightsnow": "🌨️", "heavysnow": "❄️", "snowshowers": "🌨️", "thunder": "⛈️",
    "lightsnowandthunder": "⛈️",
}


# ── data ──────────────────────────────────────────────────────────────────

def _base(code):
    for suffix in ("_day", "_night", "_polartwilight"):
        if code and code.endswith(suffix):
            return code[: -len(suffix)]
    return code


def symbol_label(code):
    return _base(code).replace("_", " ") if code else "—"


def symbol_emoji(code):
    base = (_base(code) or "").lower()
    for key, emoji in SYMBOL_EMOJI.items():
        if key in base:
            return emoji
    return "🌡️"


def _local(step):
    return datetime.fromisoformat(step["time"].replace("Z", "+00:00")).astimezone(TZ)


def _midday(entries):
    return next((e for e in entries if _local(e).hour == 12), entries[len(entries) // 2])


def _symbol(step, *periods):
    for p in periods:
        code = step["data"].get(p, {}).get("summary", {}).get("symbol_code")
        if code:
            return code
    return None


def summarise_day(day, entries):
    mid = _midday(entries)
    inst = mid["data"]["instant"]["details"]
    temps = [e["data"]["instant"]["details"]["air_temperature"] for e in entries]
    precip = 0.0
    for e in entries:
        d = e["data"]
        amount = d.get("next_1_hours", {}).get("details", {}).get("precipitation_amount")
        if amount is None:
            amount = d.get("next_6_hours", {}).get("details", {}).get("precipitation_amount", 0)
        precip += amount
    return {
        "date": day,
        "symbol": _symbol(mid, "next_6_hours", "next_12_hours")
                  or _symbol(entries[0], "next_6_hours"),
        "temp_min": round(min(temps)),
        "temp_max": round(max(temps)),
        "midday_temp": round(inst["air_temperature"]),
        "precipitation": round(precip, 1),
        "wind_speed": round(inst["wind_speed"], 1),
        "humidity": round(inst["relative_humidity"]),
    }


def process(raw, today=None):
    """Group MET timesteps by local (Oslo) date: tomorrow + up to 10 days."""
    today = today or datetime.now(TZ).date()
    by_day = {}
    for step in raw["properties"]["timeseries"]:
        by_day.setdefault(_local(step).date(), []).append(step)

    days = []
    for i in range(1, DAYS + 1):
        d = today + timedelta(days=i)
        if by_day.get(d):
            days.append(summarise_day(d, by_day[d]))
    if not days:
        raise ValueError("No forecast data available.")

    tomorrow = by_day[days[0]["date"]]
    hourly = [{
        "time": _local(e).strftime("%H:%M"),
        "temp": round(e["data"]["instant"]["details"]["air_temperature"]),
        "symbol": _symbol(e, "next_1_hours", "next_6_hours"),
    } for e in tomorrow[::3][:8]]

    return {"tomorrow": days[0], "hourly": hourly, "ten_day": days}


# ── html ──────────────────────────────────────────────────────────────────

def icon(cls, code):
    """Local MET icon (copied to out/icons/), emoji if the code has no icon."""
    if not code or not (ICONS / f"{code}.svg").exists():
        return f'<span class="{cls}" style="font-size:1.8rem;line-height:1">{symbol_emoji(code)}</span>'
    return f'<img class="{cls}" src="icons/{escape(code)}.svg" alt="{escape(symbol_label(code))}">'


def copy_icons(f):
    used = {f["tomorrow"]["symbol"]}
    used |= {h["symbol"] for h in f["hourly"]} | {d["symbol"] for d in f["ten_day"]}
    dest = OUT.parent / "icons"
    dest.mkdir(parents=True, exist_ok=True)
    for code in filter(None, used):
        src = ICONS / f"{code}.svg"
        if src.exists():
            shutil.copy2(src, dest / src.name)


def long_date(d: date):
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B %Y')}"


def short_day(d: date, i):
    return "Tomorrow" if i == 0 else f"{d.strftime('%a')} {d.day} {d.strftime('%b')}"


def render(f, generated_at=None):
    t = f["tomorrow"]
    all_min = min(d["temp_min"] for d in f["ten_day"])
    all_max = max(d["temp_max"] for d in f["ten_day"])
    span = (all_max - all_min) or 1
    generated_at = generated_at or datetime.now(TZ)

    hourly_html = "".join(f"""
        <div class="hour-block">
          <div class="hour-time">{h['time']}</div>
          {icon("hour-icon", h['symbol'])}
          <div class="hour-temp">{h['temp']}°</div>
        </div>""" for h in f["hourly"])

    rows = []
    for i, d in enumerate(f["ten_day"]):
        left = (d["temp_min"] - all_min) / span * 100
        width = (d["temp_max"] - d["temp_min"]) / span * 100
        rain = d["precipitation"] > 0
        rows.append(f"""
          <div class="day-row">
            <div class="day-name">{short_day(d['date'], i)}</div>
            {icon("day-icon", d['symbol'])}
            <div class="day-bar-wrap">
              <div class="day-temp-lo">{d['temp_min']}°</div>
              <div class="bar-track"><div class="bar-fill" style="margin-left:{left:.1f}%;width:{width:.1f}%"></div></div>
              <div class="day-temp-hi">{d['temp_max']}°</div>
            </div>
            <div class="day-precip{' has-rain' if rain else ''}">{f"{d['precipitation']} mm" if rain else '—'}</div>
          </div>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>10-Day Weather Forecast – Hamar</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  <style>
{CSS}  </style>
</head>
<body>
  <div class="card" id="app">
    <div class="hero">
      <div class="location-row">
        <span class="location-pin">📍</span>
        <span class="location">{LOCATION}</span>
      </div>
      <div class="date">{long_date(t['date'])}</div>
      <div class="summary">
        <div class="summary-left">
          {icon("weather-icon", t['symbol'])}
          <div class="temp-block">
            <div class="temp-main">{t['temp_max']}<sup>°C</sup></div>
            <div class="condition">{escape(symbol_label(t['symbol']))}</div>
            <div class="temp-range-pill">
              <span class="hi">↑ {t['temp_max']}°</span>
              <span class="sep">/</span>
              <span class="lo">↓ {t['temp_min']}°</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="body">
      <div class="stats">
        <div class="stat"><span class="stat-icon">💨</span><div class="stat-label">Wind</div><div class="stat-value">{t['wind_speed']} m/s</div></div>
        <div class="stat"><span class="stat-icon">🌧️</span><div class="stat-label">Precipitation</div><div class="stat-value">{t['precipitation']} mm</div></div>
        <div class="stat"><span class="stat-icon">💧</span><div class="stat-label">Humidity</div><div class="stat-value">{t['humidity']}%</div></div>
        <div class="stat"><span class="stat-icon">🌡️</span><div class="stat-label">At midday</div><div class="stat-value">{t['midday_temp']}°C</div></div>
      </div>

      <div class="section-header">Hourly – every 3 h</div>
      <div class="hourly"><div class="hourly-row">{hourly_html}</div></div>

      <div class="divider"></div>

      <div class="section-header">10-day forecast</div>
      <div class="ten-day">{''.join(rows)}</div>
    </div>

    <div class="source">Data: MET Norway / Meteorologisk institutt (CC BY 4.0) · updated {generated_at:%d.%m.%Y %H:%M}</div>
  </div>
</body>
</html>
"""


def main():
    with open(FIXTURE, encoding="utf-8") as fh:
        raw = json.load(fh)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    forecast = process(raw)
    copy_icons(forecast)
    OUT.write_text(render(forecast), encoding="utf-8")
    print(f"render: wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
