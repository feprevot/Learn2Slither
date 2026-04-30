# Learn2Slither

Snake game with Q-learning reinforcement learning (42 project).

### setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 main.py

python3 main.py -sessions 100 -visual off -save models/100sess.txt

python3 main.py -load models/100sess.txt -visual on -dontlearn -step-by-step

python3 main.py -load models/100sess.txt -sessions 10 -visual on -dontlearn -speed 0.05
```

## Arguments

| Argument | Default | Description |
|---|---|---|
| `-sessions N` | 1 | Number of training sessions |
| `-visual on/off` | on | Enable/disable graphical window |
| `-save path` | — | Save model to file after training |
| `-load path` | — | Load existing model before running |
| `-dontlearn` | off | Disable Q-table updates (exploitation only) |
| `-step-by-step` | off | Wait for keypress between each step |
| `-speed N` | 0.2 | Seconds between steps (visual mode) |

## Controls (graphical window)

- `ESC` — quit
- Any key — next step (step-by-step mode)
