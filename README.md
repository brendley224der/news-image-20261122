# The World Today — Sunday 22 November 2026

A one-page newspaper front page summing up the world's news of
Sunday 22 November 2026, drawn by a pure-stdlib Python program.

## The day in six stories

1. **Gulf war widens** — Iran struck a US air base in Kuwait and targeted
   Bahrain; tankers were hit off Oman and oil prices fell.
2. **COP31 talks deadlock** — a fight over fossil fuels and climate finance
   left the summit stalled.
3. **Quake shakes Peru** — a magnitude 6.9 earthquake struck the Andes.
4. **Cartel boss captured** — Mexican forces arrested El Chapo Isidro;
   violence in Sinaloa left 11 dead.
5. **Russia's big barrage** — 400 drones and 110 missiles in one of the
   war's largest attacks; a strike on Zelenskyy's hometown killed two.
6. **Estonia to close its border with Russia** — Moscow decried a new
   Iron Curtain.

Also noted: Trump touts a summit with Xi and Putin, Bolsonaro in intensive
care, and an Air Niugini jet landing safely after an engine fire.

## Run

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## How it works

`main.py` draws the front page with a hand-built 5x7 bitmap font onto a
1024x1024 RGB framebuffer and encodes it as a PNG using only the Python
standard library (`zlib`, `struct`, `binascii`). No network, no randomness,
no clock: every run writes byte-identical output (16,749 bytes, well under
the 1 MiB limit).

## License

MIT — see `LICENSE`.
