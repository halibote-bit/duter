# duter ✨

Summon a sprite with one line of Python: a magical being appears, dances across a starry sky,
sparks of joy bloom around it — and at the end, **HAPPINESS**
appears in rainbow colours, one letter at a time.

Run the window whenever you need it: it just might bring you a good mood
and a little joy. 🌟

**Zero third-party dependencies** — pure standard-library `tkinter`.

```python
import duter
duter.summon()
```

While the window is open:

- **Click anywhere** — the sprite creates more sparks of joy
- **Esc** or close the window — end early

## API

```python
duter.summon(mood="rainbow", duration=8.0, finale="sparkle")
```

| Parameter  | Default     | Meaning                                                      |
|------------|-------------|--------------------------------------------------------------|
| `mood`    | `"rainbow"` | Colour theme: `rainbow`, `gold`, `silver`, `sunrise`, `ocean` |
| `duration` | `8.0`       | Rough show length in seconds (≥ 2); more sparks for longer shows |
| `finale`   | `"sparkle"` | Finale: sparkle sky + rainbow "HAPPINESS"; `None` to skip |

## Command line

```console
python -m duter
python -m duter --mood sunrise --duration 12
duter --mood gold --no-finale     # after `pip install duter`
```

## What happens on screen

1. A tiny sprite materializes from stardust at the bottom of a starry sky
2. It begins to dance, leaving trails of sparkling light
3. Bursts of joy explode around the sprite with colorful particles
4. ~100 particles bloom with gravity, drag, flicker, and colour cooling
   (white-hot → theme colour → dying ember)
5. Finale: sparkles fill the sky, and **HAPPINESS** glows in rainbow
   letters before gently fading away, then the window closes itself

## Requirements

- Python ≥ 3.8 with `tkinter` (included in the official installers on
  Windows and macOS; on Linux: `sudo apt install python3-tk` or equivalent)

## Development

```console
pip install build twine
python -m build
twine upload dist/*
```

## License

MIT