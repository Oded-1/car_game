# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A top-down 2D car racing game built with `pygame-ce` (Pygame Community Edition). Currently a minimal single-track prototype: a player-controlled car with acceleration/friction physics driving around a track image. Collision detection against the track border is not yet wired up (see "Known gaps" below).

## Running the game

The repo includes a `.venv` directory, but it was created on a different machine (Linux, `/home/odedtz/car_game_py/.venv` per `.venv/pyvenv.cfg`) and its interpreter symlinks will not resolve here. Create a fresh venv instead of relying on the committed one:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pygame-ce
```

Then run the game from the repo root (it loads images via relative paths like `public/track1.png`, so the working directory matters):

```bash
python main.py
```

There is no `requirements.txt`, build step, lint config, or test suite in this repo.

## Architecture

Two files make up the whole game:

- **`main.py`** — entry point. Loads images from `public/`, defines the car classes, and runs the main game loop.
  - `AbstractCar` — base class holding movement physics: `rotate`, `move_forward`, `move_backward`, `move`, `collide` (mask-based overlap check, currently unused by the loop), `reset`. Subclasses must set class attributes `IMG` and `START_POS`.
  - `PlayerCar(AbstractCar)` — the only car type currently; adds `reduce_speed` (friction when no input).
  - `draw(scrn, imgs, player_car)` — blits background/border images then the car, and flips the display.
  - `move_player(player_car, d_t)` — reads `pygame.key.get_pressed()` (arrows or WASD) and calls the appropriate car methods.
  - The `while running` loop computes `delta_time` from `clock.tick(FPS)` (clamped to `[0.001, 0.1]`) so movement speed is frame-rate independent, then handles the `QUIT` event, applies input, clears the screen, and draws. Several pipeline steps are stubbed out as empty comments (hitbox setup, collision checks/response, text rendering) — see "Known gaps".
- **`methods.py`** — small Pygame helper functions used by `main.py`: `scale_image` (scales a surface by a factor), `blit_rotate_center` (rotates an image around its own center rather than the top-left corner), `blit_text_center` (centers rendered text on the window).

Assets live in `public/`: `track1.png` / `track1_border.png` (the track and its collision mask source), `car_red.png` (player sprite), `finish.png` and `ariel.jpeg` (not currently loaded by `main.py`).

## Known gaps

`main.py`'s main loop has placeholder comments for functionality that isn't implemented yet: building the border mask, checking `player_car.collide(...)` against it, responding to collisions (e.g. calling `reset()` or reducing velocity), and rendering on-screen text via `blit_text_center`/`font`. When extending collision or UI behavior, this is the intended integration point.

## Roadmap: AI player

Once the game itself is finished and polished (full collision handling, win/lose state, etc.), the plan is to train an AI to play it via a neural network + reinforcement learning, rather than scripting it by hand. Implications for earlier work:

- Keep the simulation step (`move`, `collide`, physics) decoupled from Pygame rendering/input where practical, so an RL training loop can step the car/track logic headlessly (no window, no `clock.tick`-bound real time) at high speed across many episodes.
- Collision detection (currently a gap) will double as the episode-termination / reward signal (off-track = penalty or episode end), so get it working correctly before building the RL environment on top of it.
- Expect to eventually wrap the game as a Gym-style environment (`reset()`/`step(action)`/observation+reward) feeding the car's state (position, angle, velocity, sensor/raycast distances to the border, etc.) to the policy network.
