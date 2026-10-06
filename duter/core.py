"""duter.core — the sprite animation engine.

Zero third-party dependencies: pure ``tkinter`` + standard library.

Animation Outline
-----------------
1. A tiny sprite materializes from stardust at the bottom of a starry night sky.
2. It begins to dance, leaving trails of sparkling light.
3. Bursts of joy explode around the sprite with colorful particles.
4. A particle system simulates the bloom: gravity, air drag, colour cooling
   (white-hot -> theme colour -> dying ember) and flickering sparks.
5. Optional finale: the sparks fade into a sky full of sparkles and the
   words "DUTER" appear one rainbow-coloured letter at a time, glow,
   and gently vanish.

Click anywhere to summon extra sparks. Press Esc to close early.
"""

from __future__ import annotations

import colorsys
import math
import random
import time
import tkinter as tk

__all__ = ["summon", "MOODS"]

# ----------------------------------------------------------------- palette

_BG = (6, 10, 30)                # deep night sky
_GOLD = (255, 200, 60)

_WIDTH, _HEIGHT = 920, 620
_MS = 16                         # frame interval (~60 fps)

#: Built-in colour themes. ``"rainbow"`` picks a fresh random hue per burst.
MOODS = {
    "rainbow": None,
    "gold": [(255, 200, 60), (255, 160, 50), (255, 235, 160)],
    "silver": [(210, 225, 255), (160, 185, 235), (240, 246, 255)],
    "sunrise": [(255, 140, 66), (255, 200, 120), (255, 100, 80)],
    "ocean": [(70, 130, 180), (100, 200, 230), (173, 216, 230)],
}


def _hex(c):
    return "#%02x%02x%02x" % (int(c[0]), int(c[1]), int(c[2]))


def _mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def _scale(c, f):
    return (min(255, c[0] * f), min(255, c[1] * f), min(255, c[2] * f))


def _random_hue():
    h = random.random()
    return tuple(int(v * 255) for v in colorsys.hsv_to_rgb(h, 0.75, 1.0))


# ----------------------------------------------------------------- objects

class _Spark:
    """One firework particle with gravity, drag, colour cooling, flicker."""

    __slots__ = ("x", "y", "vx", "vy", "age", "life", "c0", "c1", "r",
                 "item", "flicker", "grav", "drag")

    def __init__(self, cv, x, y, vx, vy, life, color, r=2.0,
                 flicker=False, grav=0.045, drag=0.986):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.age, self.life = 0, life
        self.c0 = _mix(color, (255, 255, 255), 0.65)   # white-hot core
        self.c1 = color
        self.r = r
        self.flicker = flicker
        self.grav, self.drag = grav, drag
        self.item = cv.create_oval(x - r, y - r, x + r, y + r,
                                   fill=_hex(self.c0), outline="")

    def step(self, cv, frame):
        """Advance one frame; return False when the spark is dead."""
        self.age += 1
        if self.age >= self.life:
            cv.delete(self.item)
            return False
        self.vx *= self.drag
        self.vy = self.vy * self.drag + self.grav
        self.x += self.vx
        self.y += self.vy
        t = self.age / self.life
        if t < 0.22:                                   # hot white -> theme
            c = _mix(self.c0, self.c1, t / 0.22)
        else:                                          # theme -> dark ember
            c = _mix(self.c1, _scale(self.c1, 0.10), (t - 0.22) / 0.78)
        if self.flicker and (frame + id(self)) % 3 == 0:
            c = _BG
        r = self.r * (1.0 - 0.55 * t)
        cv.coords(self.item, self.x - r, self.y - r, self.x + r, self.y + r)
        cv.itemconfigure(self.item, fill=_hex(c))
        return True


class _Shell:
    """A rocket fired from the wand tip; explodes near its apex."""

    GRAV = 0.085

    def __init__(self, cv, x0, y0, tx, ty, colors):
        h = y0 - ty
        self.x, self.y = x0, y0
        self.vy = -math.sqrt(2 * self.GRAV * h)
        tf = math.sqrt(2 * h / self.GRAV)
        self.vx = (tx - x0) / tf
        self.colors = colors
        self.item = cv.create_oval(x0 - 3, y0 - 3, x0 + 3, y0 + 3,
                                   fill="#fff2c8", outline="")

    def step(self, cv, sparks):
        self.x += self.vx
        self.vy += self.GRAV
        self.y += self.vy
        cv.coords(self.item, self.x - 3, self.y - 3, self.x + 3, self.y + 3)
        for _ in range(2):                             # golden trail
            sparks.append(_Spark(
                cv,
                self.x + random.uniform(-2, 2),
                self.y + random.uniform(-2, 2),
                random.uniform(-0.4, 0.4),
                random.uniform(0.2, 0.9),
                random.randint(18, 30),
                (255, 190, 90), r=1.4, grav=0.01, drag=0.95,
            ))
        return self.vy > -0.35                         # near apex -> boom


# ------------------------------------------------------------------- show

class _Show:
    """Owns the tkinter window and runs the whole animation state machine."""

    def __init__(self, mood, duration, finale):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:                     # no display available
            raise RuntimeError(
                "duter needs a graphical display (a desktop) to summon "
                "its sprite, but none was found: " + str(exc)
            ) from exc

        self.mood = mood
        self.duration = max(2.0, duration)
        self.finale = finale
        self._summons = min(8, max(2, round((self.duration - 0.8) / 2.4)))

        self.root.title("duter ✨ a sprite, sparks of joy & a little happiness")
        self.root.configure(bg=_hex(_BG))
        self.root.resizable(False, False)
        self.cv = tk.Canvas(self.root, width=_WIDTH, height=_HEIGHT,
                            bg=_hex(_BG), highlightthickness=0)
        self.cv.pack()

        self.root.update_idletasks()
        self.root.geometry("+%d+%d" % (
            (self.root.winfo_screenwidth() - _WIDTH) // 2,
            (self.root.winfo_screenheight() - _HEIGHT) // 2,
        ))

        self._frame = 0
        self._phase = "materialize"    # materialize -> dance -> burst -> settle
        self._pt = 0                   # frames spent in current phase
        self._summon_no = 0
        self._sparks = []
        self._shells = []
        self._flashes = []
        self._letters = []
        self._sub = None
        self._done = False
        self._t0 = time.time()

        self._build_sky()
        self._build_sprite()
        self._build_glow_items()

        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.bind("<Escape>", self._close)
        self.cv.bind("<Button-1>", self._on_click)

    # ------------------------------------------------------------- scenery

    def _build_sky(self):
        self._stars = []
        for _ in range(110):
            x = random.uniform(0, _WIDTH)
            y = random.uniform(0, _HEIGHT * 0.92)
            r = random.choice((0.7, 0.9, 1.2, 1.6))
            c = random.choice(((200, 215, 255), (255, 245, 225), (235, 240, 255)))
            item = self.cv.create_oval(x - r, y - r, x + r, y + r,
                                       fill=_hex(_scale(c, random.uniform(0.35, 1.0))),
                                       outline="")
            self._stars.append((item, c))

    def _build_sprite(self):
        """Build the tiny magical sprite that dances across the sky."""
        self._sprite_pos = (_WIDTH / 2, _HEIGHT * 0.85)
        self._sprite_dy = 0
        # Sprite body: a glowing orb with wings
        self._sprite_body = self.cv.create_oval(0, 0, 0, 0, fill="#ffe4b5", outline="")
        self._sprite_glow = self.cv.create_oval(0, 0, 0, 0, fill="#ffd700", stipple="gray50", outline="")
        self._sprite_wing_l = self.cv.create_oval(0, 0, 0, 0, fill="#fffacd", stipple="gray25", outline="")
        self._sprite_wing_r = self.cv.create_oval(0, 0, 0, 0, fill="#fffacd", stipple="gray25", outline="")
        self._sprite_eyes = []

    def _build_glow_items(self):
        """Build glow items for the sprite's aura."""
        sx, sy = self._sprite_pos
        self._aura_a = self.cv.create_oval(0, 0, 0, 0, fill="#ffd970",
                                           stipple="gray50", outline="")
        self._aura_b = self.cv.create_oval(0, 0, 0, 0, fill="#ffe9a8",
                                           stipple="gray75", outline="")

    def _sprite_position(self):
        """Get current sprite position with dance animation."""
        sx, sy = self._sprite_pos
        if self._phase == "materialize":
            t = min(1.0, self._pt / 42.0)
            e = 1.0 - (1.0 - t) ** 3
            dy = (1.0 - e) * 100
        elif self._phase == "dance":
            dy = 8 * math.sin(self._frame * 0.06)
        else:
            dy = 4 * math.sin(self._frame * 0.04)
        return (sx, sy - dy)

    # -------------------------------------------------------------- casting

    def _mood_colors(self):
        if self.mood == "rainbow":
            base = _random_hue()
            second = _random_hue() if random.random() < 0.35 else base
        else:
            pal = MOODS[self.mood]
            base = random.choice(pal)
            second = random.choice(pal)
        return base, second

    def _burst(self, colors=None):
        sx, sy = self._sprite_position()
        target = (random.uniform(_WIDTH * 0.15, _WIDTH * 0.85),
                  random.uniform(_HEIGHT * 0.14, _HEIGHT * 0.34))
        self._shells.append(
            _Shell(self.cv, sx, sy - 20, target[0], target[1], colors or self._mood_colors()))

    def _explode(self, x, y, colors):
        base, second = colors
        self._flashes.append({"x": x, "y": y, "t": 0})
        n = random.randint(85, 125)
        speed = random.uniform(2.8, 4.2)
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = speed * random.uniform(0.25, 1.0)
            col = base if random.random() < 0.75 else second
            self._sparks.append(_Spark(
                self.cv, x, y,
                math.cos(a) * v, math.sin(a) * v,
                random.randint(45, 85), col,
                r=random.uniform(1.6, 2.6),
                flicker=random.random() < 0.4,
            ))
        for _ in range(12):                             # slow falling embers
            a = random.uniform(0, math.tau)
            v = random.uniform(0.5, 1.4)
            self._sparks.append(_Spark(
                self.cv, x, y,
                math.cos(a) * v, math.sin(a) * v,
                random.randint(90, 130), second,
                r=2.2, drag=0.965, grav=0.05,
            ))

    def _on_click(self, _event):
        """Click anywhere: the sprite creates more sparks of joy."""
        if not self._done and self._phase != "materialize":
            self._burst()

    # --------------------------------------------------------------- frames

    def _update_sprite(self):
        """Update sprite position and animation."""
        sx, sy = self._sprite_position()
        # Body
        r = 12 + 2 * math.sin(self._frame * 0.1)
        self.cv.coords(self._sprite_body, sx - r, sy - r, sx + r, sy + r)
        # Glow aura
        ga, gb = r * 2.5, r * 1.8
        self.cv.coords(self._sprite_glow, sx - ga, sy - ga, sx + ga, sy + ga)
        # Wings that flutter
        wing_offset = 3 * math.sin(self._frame * 0.15)
        self.cv.coords(self._sprite_wing_l, sx - r - 10, sy - wing_offset - 5, sx - r + 5, sy + wing_offset + 8)
        self.cv.coords(self._sprite_wing_r, sx + r - 5, sy - wing_offset - 5, sx + r + 10, sy + wing_offset + 8)

    def _update_aura(self):
        """Update sprite's glowing aura."""
        sx, sy = self._sprite_position()
        if self._phase == "materialize":
            r = 4.0 + 2.5 * math.sin(self._pt * 0.45)
            ga, gb = r * 2.8, r * 1.6
        else:
            r = 3.0 + 0.6 * math.sin(self._frame * 0.1)
            ga, gb = r * 2.2, r * 1.4
        for item, rad in ((self._aura_a, ga), (self._aura_b, gb)):
            self.cv.coords(item, sx - rad, sy - rad, sx + rad, sy + rad)

    def _update_shells(self):
        alive = []
        for sh in self._shells:
            if sh.step(self.cv, self._sparks):
                self._explode(sh.x, sh.y, sh.colors)
                self.cv.delete(sh.item)
            else:
                alive.append(sh)
        self._shells = alive

    def _update_sparks(self):
        self._sparks = [s for s in self._sparks if s.step(self.cv, self._frame)]

    def _update_flashes(self):
        keep = []
        for f in self._flashes:
            f["t"] += 1
            t = f["t"] / 12.0
            if t >= 1.0:
                if "item" in f:
                    self.cv.delete(f["item"])
                continue
            r = 10 + 70 * t
            c = _mix((255, 250, 235), _BG, t)
            if "item" not in f:
                f["item"] = self.cv.create_oval(
                    f["x"] - r, f["y"] - r, f["x"] + r, f["y"] + r,
                    fill=_hex(c), stipple="gray50", outline="")
            else:
                self.cv.coords(f["item"], f["x"] - r, f["y"] - r,
                               f["x"] + r, f["y"] + r)
                self.cv.itemconfigure(f["item"], fill=_hex(c))
            keep.append(f)
        self._flashes = keep

    def _update_stars(self):
        for item, c in random.sample(self._stars, 6):
            self.cv.itemconfigure(item, fill=_hex(_scale(c, random.uniform(0.3, 1.0))))

    # ------------------------------------------------------- phase machine

    def _update_phase(self):
        self._pt += 1
        ph = self._phase

        if ph == "materialize" and self._pt >= 42:
            self._phase, self._pt = "dance", 0

        elif ph == "dance" and self._pt >= 26:
            self._summon_no += 1
            self._burst()
            self._phase, self._pt = "burst", 0

        elif ph == "burst" and not self._shells:
            self._phase, self._pt = "settle", 0

        elif ph == "settle" and self._pt >= 70:
            if self._summon_no < self._summons:
                self._phase, self._pt = "dance", 0
            else:
                self._phase, self._pt = "finale", 0
                if self.finale:
                    self._build_finale_text()

        elif ph == "finale":
            if self.finale:
                self._update_finale()
            elif self._pt >= 25:
                self._phase, self._pt = "over", 0

        elif ph == "over" and self._pt >= 10:
            self._close()

    def _build_finale_text(self):
        """Each letter of "DUTER" gets its own rainbow hue."""
        self._letters = []
        text = "DUTER"
        n = len(text)
        spacing = 56
        x0 = _WIDTH / 2 - spacing * (n - 1) / 2
        for i, ch in enumerate(text):
            if ch == " ":
                continue
            hue = (i / n) * 0.85                       # rainbow sweep
            col = tuple(int(v * 255)
                        for v in colorsys.hsv_to_rgb(hue, 0.9, 1.0))
            item = self.cv.create_text(
                x0 + i * spacing, _HEIGHT * 0.42, text=ch,
                font=("Georgia", 52, "bold"), fill=_hex(_BG))
            self._letters.append((item, col))
        self._sub = self.cv.create_text(
            _WIDTH / 2, _HEIGHT * 0.42 + 65,
            text="—  a magical sprite bringing you joy  —",
            font=("Georgia", 14, "italic"), fill=_hex(_BG))

    def _update_finale(self):
        pt = self._pt
        for _ in range(3):                              # sky glitter
            self._sparks.append(_Spark(
                self.cv,
                random.uniform(_WIDTH * 0.08, _WIDTH * 0.92),
                random.uniform(_HEIGHT * 0.08, _HEIGHT * 0.55),
                random.uniform(-0.3, 0.3), random.uniform(-0.2, 0.2),
                random.randint(30, 60),
                random.choice(((255, 240, 190), (255, 255, 255), _GOLD)),
                r=random.uniform(1.0, 2.0), grav=0.008, drag=0.99,
                flicker=True,
            ))
        if pt >= 160:                                   # all done
            for item, _col in self._letters:
                self.cv.delete(item)
            self.cv.delete(self._sub)
            self._phase, self._pt = "over", 0
            return
        # letters: staggered fade-in, hold, staggered fade-out
        for i, (item, col) in enumerate(self._letters):
            a_in = max(0.0, min(1.0, (pt - 3 * i) / 42.0))
            a_out = max(0.0, min(1.0, (pt - 120 - 2 * i) / 32.0))
            self.cv.itemconfigure(
                item, fill=_hex(_mix(_BG, col, a_in * (1.0 - a_out))))
        a_sub = max(0.0, min(1.0, pt / 45.0)) * (
            1.0 - max(0.0, min(1.0, (pt - 120) / 32.0)))
        self.cv.itemconfigure(
            self._sub, fill=_hex(_mix(_BG, (150, 150, 170), a_sub)))

    # -------------------------------------------------------------- control

    def _close(self, *_args):
        if self._done:
            return
        self._done = True
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def _tick(self):
        if self._done:
            return
        self._frame += 1
        self._update_sprite()
        self._update_aura()
        self._update_shells()
        self._update_sparks()
        self._update_flashes()
        self._update_stars()
        self._update_phase()
        if time.time() - self._t0 > self.duration + 15:   # safety net
            self._close()
            return
        self.root.after(_MS, self._tick)

    def run(self):
        self.root.after(_MS, self._tick)
        self.root.mainloop()


# ----------------------------------------------------------------- public

def summon(mood="rainbow", duration=8.0, finale="sparkle"):
    """Summon a sprite: a magical being appears and sparks of joy bloom in the night sky.

    Parameters
    ----------
    mood : str
        Colour theme: ``"rainbow"`` (default), ``"gold"``, ``"silver"``,
        ``"sunrise"`` or ``"ocean"``.
    duration : float
        Rough length of the show in seconds (>= 2). At least two sparks
        are created; more for longer durations.
    finale : str or None
        ``"sparkle"`` (default) ends with a sky of sparkles and the
        rainbow-coloured words "DUTER"; ``None`` ends right after the
        last burst.

    Notes
    -----
    Opens a tkinter window and blocks until it closes (automatically at the
    end of the show, or earlier via Esc / closing the window). While open,
    click anywhere to create extra sparks of joy.
    """
    if mood not in MOODS:
        raise ValueError("unknown mood %r; choose from %s"
                         % (mood, sorted(MOODS)))
    _Show(mood, float(duration), finale).run()