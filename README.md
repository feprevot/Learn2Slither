# Learn2Slither

A Snake game where the snake learns to play **on its own** through
**Q-learning**, a classic reinforcement-learning algorithm. No strategy is
hand-coded: the agent only receives rewards and, over thousands of games,
discovers that eating green apples is good and that walls, its own body and red
apples are bad.

> 42 school project.

---

## Table of contents

- [How it works](#how-it-works)
  - [The environment](#the-environment)
  - [What the snake sees (the state)](#what-the-snake-sees-the-state)
  - [Rewards](#rewards)
  - [The agent](#the-agent)
- [Project structure](#project-structure)
- [Setup](#setup)
- [Usage](#usage)
- [Command-line arguments](#command-line-arguments)
- [Controls (graphical window)](#controls-graphical-window)
- [Pre-trained models](#pre-trained-models)
- [Benchmark](#benchmark)
- [Glossary](#glossary)

---

## How it works

### The environment

The game is played on a square grid (`10x10` by default). At all times the
board contains:

- the **snake**, starting with a length of 3,
- **2 green apples** — eating one grows the snake by 1 and spawns a new green
  apple,
- **1 red apple** — eating it shrinks the snake by 1 and spawns a new red apple.

A game ends when the snake hits a **wall**, runs into **its own body**, or
shrinks to a **length of 0** (after eating a red apple). Implemented in
[`board_class.py`](board_class.py).

### What the snake sees (the state)

The snake does **not** see the whole board. Like a real snake, it only looks
straight along the four directions from its head (up, down, left, right). For
each direction it reports the **first object it encounters** and **how far away
it is**:

- object: `danger` (its body **or** a wall), `green` (green apple) or `red`
  (red apple);
- distance bucket: `near` (1 cell), `medium` (2–3 cells) or `far` (4+ cells).

The state is therefore a tuple of four `(object, distance)` pairs in the order
`(UP, DOWN, LEFT, RIGHT)`, for example:

```python
(('green', 'far'), ('danger', 'near'), ('red', 'medium'), ('danger', 'far'))
```

This compact, hashable tuple is used directly as the key of the Q-table. The
vision logic lives in `Board.scan_direction` and `Board.get_state`
([`board_class.py`](board_class.py)).

### Rewards

After each move the agent receives a numeric reward
([`constants.py`](constants.py)):

| Event                 | Reward |
|-----------------------|-------:|
| Eat a green apple     |   +25  |
| Eat a red apple       |   −25  |
| Die (wall/body/empty) |  −100  |
| Any other step        |   −2.5 |

The small per-step penalty discourages the snake from wandering aimlessly and
pushes it to reach apples quickly.

### The agent

The agent ([`agent_class.py`](agent_class.py)) is a tabular Q-learner:

- It keeps a **Q-table** `{state: {action: q_value}}`.
- It selects actions with an **epsilon-greedy** policy: with probability `ε` it
  explores (random action), otherwise it exploits (best known action).
- It learns by updating Q-values with the **Bellman equation**:

  ```
  Q(s,a) ← Q(s,a) + α · [ r + γ · max_a' Q(s',a') − Q(s,a) ]
  ```

Default hyperparameters:

| Parameter | Value | Meaning |
|---|---|---|
| `alpha` (α) | `0.1` | learning rate |
| `gamma` (γ) | `0.98` | discount factor (importance of future rewards) |
| `epsilon` (ε) | `1.0 → 0.15` | exploration rate, decayed over time |
| `epsilon_decay` | `0.998` | multiplied to ε on every update |

Models are saved/loaded as JSON (the Q-table plus the hyperparameters).

---

## Project structure

```
learn2slither/
├── snake.py          # Entry point: CLI parsing + training/eval loop
├── agent_class.py    # Q-learning agent (Q-table, epsilon-greedy, Bellman update)
├── board_class.py    # Environment: board, apples, movement, vision/state
├── snake_class.py    # Snake body: move, grow, shrink, self-collision
├── render_class.py   # Pygame graphical display
├── benchmark.py      # Train & compare models at several session counts
├── constants.py      # Board size, rewards, symbols, hyperparameter constants
├── models/           # Pre-trained Q-tables (1 → 10000 sessions)
└── requirements.txt
```

---

## Setup

Requires **Python 3.12**.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies: `pygame` (graphical display) and `flake8` (linting).

---

## Usage

The entry point is `snake.py`.

```bash
# Run one game with the graphical window (untrained)
python3 snake.py

# Train for 100 sessions without graphics, then save the model
python3 snake.py -sessions 100 -visual off -save models/100sess.txt

# Load a trained model and watch it play step by step (no further learning)
python3 snake.py -load models/100sess.txt -visual on -dontlearn -step-by-step

# Load a model and watch 10 games at a slower pace
python3 snake.py -load models/100sess.txt -sessions 10 -visual on -dontlearn -speed 0.05
```

When the graphical window is on, the snake's **vision** and the chosen action
are also printed to the terminal at every step.

---

## Command-line arguments

| Argument | Default | Description |
|---|---|---|
| `-sessions N` | `1` | Number of games (sessions) to play |
| `-visual on/off` | `on` | Enable/disable the graphical window |
| `-save PATH` | — | Save the model to a file after running |
| `-load PATH` | — | Load an existing model before running |
| `-dontlearn` | off | Disable Q-table updates **and** exploration (ε = 0, pure exploitation) |
| `-step-by-step` | off | Wait for a keypress between each step |
| `-speed N` | `0.2` | Seconds between steps in visual mode |
| `-reset-epsilon` | off | Reset ε to 1.0 after loading (re-explore from a saved model) |
| `-max-steps N` | `1000` | Hard cap on steps per session (prevents infinite loops) |
| `-board_size N` | `10` | Board dimensions (N×N); minimum 10 |

---

## Controls (graphical window)

- `ESC` or closing the window — quit
- Any key — advance to the next step (in `-step-by-step` mode)

---

## Pre-trained models

The `models/` folder ships with Q-tables trained for increasing numbers of
sessions, so you can watch the agent improve without training anything
yourself:

| File | Sessions trained |
|---|---|
| `models/1sess.txt` | 1 |
| `models/10sess.txt` | 10 |
| `models/100sess.txt` | 100 |
| `models/1000sess.txt` | 1000 |
| `models/10000sess.txt` | 10000 |

Try loading a few of them with `-dontlearn` to compare how a barely-trained
snake behaves versus a well-trained one.

---

## Benchmark

[`benchmark.py`](benchmark.py) trains models at several session counts
(100, 200, …, 1000, then 2000, …, 5000), evaluates each over 20 games with
exploration disabled (ε = 0), and prints a comparison table of best length,
best duration and number of states learned:

```bash
python3 benchmark.py          # reuses already-trained models if present
python3 benchmark.py -force   # retrains everything from scratch
```

Trained benchmark models are written to a `benchmark_models/` folder.

---

## Glossary

**Reinforcement Learning** — A paradigm where an *agent* learns by interacting
with an *environment*: at each step it observes a state, picks an action, and
receives a reward, trying to maximize cumulative reward. Here the snake learns
on its own to eat green apples and avoid walls, its body and red apples, with no
hand-coded strategy.

**State** — The environment as seen by the agent at a given step. In this
project it is the snake's *vision*: one `(object, distance)` pair per direction
(see [What the snake sees](#what-the-snake-sees-the-state)). This tuple is the
Q-table key.

**Q-value** — `Q(s, a)`, the estimated quality of taking action `a` in state
`s`: the expected cumulative future reward if we take that action and then
follow the learned policy.

**Q-function** — The function `Q : (state, action) → q_value` that the agent
tries to learn. It can be a table or a neural network — here it is a table.

**Q-table** — The table storing all learned Q-values, implemented as a nested
dict `{state: {action: q_value}}` ([`agent_class.py`](agent_class.py)).

**Bellman equation** — The rule used to update a Q-value from the immediate
reward and the best Q-value of the next state. It is the core of the learning
process.

**Alpha (α) — learning rate** — Controls how much a new observation overrides
the old value. `α = 1` ⇒ forget the past, `α = 0` ⇒ learn nothing. Here
`α = 0.1` for stable training.

**Gamma (γ) — discount factor** — Importance of future rewards relative to
immediate ones. Close to 0 ⇒ short-sighted, close to 1 ⇒ long-term planner.
Here `γ = 0.98`, so the snake aims at apples even when they are far.

**Epsilon (ε)** — Probability, at each step, of choosing a *random* action
instead of the best known one, forcing exploration. It starts at `1.0` (fully
random) and decays toward `0.15` to gradually favor exploitation.

**Epsilon-greedy strategy** — Action selection: with probability `ε` pick a
random action (exploration), otherwise pick `argmax_a Q(s, a)` (exploitation).
This prevents the agent from locking into a suboptimal policy learned too early.
