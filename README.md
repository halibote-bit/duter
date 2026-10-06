# goodluck ✦

Cast a spell with one line of Python: a wand rises, its tip glows,
fireworks bloom across a starry night sky — and at the end, **GOOD LUCK**
appears in rainbow colours, one letter at a time.

Run the window whenever you need it: it just might bring you a good mood
and a little good luck. 🍀

**Zero third-party dependencies** — pure standard-library `tkinter`.

```python
import goodluck
goodluck.cast()
```

While the window is open:

- **Click anywhere** — the wand fires one more firework
- **Esc** or close the window — end early

## API

```python
goodluck.cast(spell="rainbow", duration=8.0, finish="glitter")
```

| Parameter  | Default     | Meaning                                                      |
|------------|-------------|--------------------------------------------------------------|
| `spell`    | `"rainbow"` | Colour theme: `rainbow`, `gold`, `silver`, `gryffindor`, `slytherin` |
| `duration` | `8.0`       | Rough show length in seconds (≥ 2); more fireworks for longer shows |
| `finish`   | `"glitter"` | Finale: glitter sky + rainbow "GOOD LUCK"; `None` to skip |

## Command line

```console
python -m goodluck
python -m goodluck --spell gryffindor --duration 12
goodluck --spell gold --no-finish     # after `pip install goodluck`
```

## What happens on screen

1. A wooden wand rises from the bottom of a starry sky
2. Its tip charges a pulsing orb of light (*Lumos*)
3. A shell launches with a golden trail and explodes at its apex
4. ~100 particles bloom with gravity, drag, flicker, and colour cooling
   (white-hot → theme colour → dying ember)
5. Finale: glitter fills the sky, and **GOOD LUCK** glows in rainbow
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
