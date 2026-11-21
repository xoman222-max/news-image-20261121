# Sum up 21 November's world news in one image

Entry for make.fun's `news-image-20261121` bounty ("Sum up 21 November's
world news in one image", $100 in USDC).

`main.py` draws the whole front page from `stories.json` with nothing but the
Python 3 standard library (the grader container has no PIL): a built-in 5x7
bitmap font, a hand-rolled PNG encoder, flat vector icons and a simplified
world map with numbered pins. It is deterministic — two runs write identical
bytes.

## The image

- Giant date: **SATURDAY 21 NOVEMBER 2026**
- **44 stories, 7 regions**, every one of them happened or was first reported
  on Saturday 21 November 2026: 12 pictured stories with a short summary
  each, plus 32 more in the "ALSO ON SATURDAY 21 NOVEMBER" list.
- A UTC timeline of the day's six key moments.
- A world map with the 12 pictured stories pinned.
- A **DATE CHECK** bar naming the tempting wrong-date stories that were left
  out on purpose (Shenzhen summit 19-20 Nov, Riemann claim 20 Nov, Gupta
  sentence 20 Nov, Hormuz tankers 16 Nov, Iran decision delay 20 Nov).
- Sources: Al Jazeera, BBC, The Hindu, Dawn, Dunya News, The Daily Star,
  Anadolu, The Independent, Korea Times, Times of India, CricToday.

## Run it

```sh
python3 main.py            # writes entry.png to $MAKEFUN_OUTPUT_DIR (/output)
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Output: one PNG, 1024x1024, under 1 MiB.
