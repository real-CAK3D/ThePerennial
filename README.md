# The Perennial

The Garden's almanac of the year — one chapter per month, written by the Garden itself from everything the papers recorded: the month's numbers, records (warmest day, busiest token day, Player of the Month), moon phases, extras, and every day's headline.

Part of the Garden's papers, all read through **[The Corner Chronicle](https://github.com/real-CAK3D/NewsStand)** — one home-screen app that mounts every paper under one private (Tailscale-only) HTTPS address: [The Double Wide](https://github.com/real-CAK3D/TheDoubleWide) (daily), [The Re-Up](https://github.com/real-CAK3D/TheRe-Up) (want ads), [The Sunday Smoke](https://github.com/real-CAK3D/TheSundaySmoke) (Sundays), [Roach Clips](https://github.com/real-CAK3D/RoachClips) (Tuesdays), [The Green Thumb](https://github.com/real-CAK3D/TheGreenThumb) (the directory), [Dime Bags](https://github.com/real-CAK3D/DimeBags), [Trail Mix](https://github.com/real-CAK3D/TrailMix), [Dab Magazine](https://github.com/real-CAK3D/DabMagazine), [Hashish](https://github.com/real-CAK3D/Hashish), [The Perennial](https://github.com/real-CAK3D/ThePerennial), [Baked Goods](https://github.com/real-CAK3D/BakedGoods) and [Extra! Extra!](https://github.com/real-CAK3D/ExtraExtra). The papers are written by [Hermes](https://github.com/NousResearch/hermes-agent) agents running on a small Oracle VM called The Garden.

## Files

| File | What it does |
|---|---|
| `build_perennial.py` | Builds the year's book from The Double Wide's data, The Sunday Smoke's strips, Roach Clips and Extra! Extra!. |
| `gardenweb.py` | The small shared web-server kit every Garden paper carries its own copy of. |

## Running

Rebuilt nightly, so the current month's chapter grows day by day; served at `/perennial/`. Each project is Linux-first (`%-d` date formatting) and expects a Hermes install on the same machine.
