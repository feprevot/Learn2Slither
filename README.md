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



## Glossary

**Reinforcement Learning**
A paradigm where an *agent* learns by interacting with an *environment*: at each step, it observes a state, picks an action, and receives a reward. The goal is to maximize cumulative reward. Here, the snake learns on its own to eat green apples and avoid walls / body / red apple, without any hand-coded strategy.

**State**
The environment representation seen by the agent at time `t`. In this project ([board_class.py:97](board_class.py#L97)), the state is the snake's *vision*: for each of the 4 directions, we encode `(first object seen, bucketed distance)` — for example `('G2', 'D1', 'R3', 'D2')`. This tuple is used as the key in the Q-table.

**Q-value**
The value `Q(s, a)` estimating the quality of action `a` in state `s`: it is the expected cumulative future reward if we take that action and then follow the learned policy. The higher the Q-value, the better the action is considered.

**Q-function**
The function `Q : (state, action) → q_value`. This is what the agent is trying to learn. It can be implemented as a table (Q-table) or a neural network — here we chose the table.

**Q-table**
Table storing all the learned Q-values. Implemented in [agent_class.py:15](agent_class.py#L15) as a nested dict `{state: {action: q_value}}`. At inference time we read it; during training we update it.

**Bellman equation**
The equation that defines how to update a Q-value from the immediate reward and the best Q-value of the next state:

```
Q(s,a) ← Q(s,a) + α · [ r + γ · max_a' Q(s',a') − Q(s,a) ]
```

Implemented in [agent_class.py:31-39](agent_class.py#L31-L39). It is the core of the learning process: without it the Q-table would never be updated.

**Alpha (α) — learning rate**
Learning speed: controls how much a new observation overrides the old value. `α = 1` ⇒ forget everything past, `α = 0` ⇒ learn nothing. Here `α = 0.1` ([agent_class.py:8](agent_class.py#L8)): new info is integrated slowly to keep training stable.

**Gamma (γ) — discount factor**
Importance of future rewards relative to immediate ones. `γ` close to 0 ⇒ short-sighted agent, `γ` close to 1 ⇒ long-term planner. Here `γ = 0.97`: the snake is encouraged to aim at apples even when they are far, not only the next cell.

**Epsilon (ε)**
Probability, at each step, of picking a *random* action instead of the best known one. Used to force exploration. Here we start at `ε = 1.0` (100% random at the beginning) and decay down to `ε = 0.15` ([agent_class.py:9](agent_class.py#L9)) to gradually shift toward exploitation.

**Epsilon-greedy strategy**
Action selection strategy: with probability `ε`, draw a random action (exploration); otherwise take `argmax_a Q(s,a)` (exploitation). Implemented in [choose_action](agent_class.py#L25-L29). This prevents the agent from getting stuck on a suboptimal policy learned too early.