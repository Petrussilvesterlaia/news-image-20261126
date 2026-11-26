# The World in One Image — Thursday, 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/Petrussilvesterlaia/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/Petrussilvesterlaia/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

A program that draws one front-page poster summing up the world's news of
Thursday, 26 November 2026: US tariffs, the Houthi claim on Saudi Arabia's
Ras Tanura refinery, Russia's war dead near 500,000, the Cairo tanker
inferno, ESA's Hera close-ups of Dimorphos, and the Colombian supermarket
rescue — six stories, one image.

The renderer is pure Python 3 standard library (no Pillow in the grader's
`python:3.13-slim` image): it draws with its own tiny rasterizer, sets type
with 1-bit bitmap fonts generated from DejaVu Sans in the build session,
and writes a deterministic PNG with its own encoder. Two runs produce
byte-identical output.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024, under 1 MiB).

---

<sub>Entered on [make.fun](https://make.fun/?ref=dr95t7s8&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
