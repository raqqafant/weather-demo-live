# Weather Demo – Hamar

A single-page 10-day weather forecast for Hamar, Norway, built with vanilla HTML/CSS/JS.

## Features

- **Tomorrow in detail** — large headline temperature, condition label, high/low pill, wind, precipitation, humidity, and an hourly strip (every 3 hours)
- **10-day outlook** — each day shows a proportional high/low temperature bar, weather icon, and daily precipitation highlighted in teal when it rains
- Weather icons and data served directly from MET Norway — no API key required

## Design

- Glassmorphism card with backdrop blur and slide-up entrance animation
- Inter font, coloured stat-card accents, gradient temperature bar (cool → warm → hot)
- Fully responsive, works on mobile and desktop

## Data source

[MET Norway Locationforecast 2.0](https://api.met.no/weatherapi/locationforecast/2.0/documentation)

## Live site

https://raqqafant.github.io/weather-demo-live/

## Run locally

Open `index.html` in a browser — no build step or server needed.
