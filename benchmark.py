import argparse
import os
import time
from board_class import Board
from agent_class import Agent

MAX_STEPS = 5000
EVAL_SESSIONS = 20
TRAIN_COUNTS = list(range(100, 1001, 100)) + list(range(2000, 5001, 1000))
MODELS_DIR = "benchmark_models"


def play_session(agent, learn):
    board = Board()
    done = False
    steps = 0
    max_length = board.snake_length()
    while not done and steps < MAX_STEPS:
        state = board.get_state()
        action = agent.choose_action(state)
        reward, done = board.step(action)
        if learn:
            next_state = board.get_state() if not done else state
            agent.update(state, action, reward, next_state, done)
        steps += 1
        length = board.snake_length()
        if length > max_length:
            max_length = length
    return max_length, steps


def train_model(sessions, path):
    agent = Agent()
    for _ in range(sessions):
        play_session(agent, learn=True)
    agent.save(path)
    return agent


def evaluate_model(path):
    agent = Agent()
    agent.load(path)
    agent.epsilon = 0.0
    best_length = 0
    best_duration = 0
    for _ in range(EVAL_SESSIONS):
        max_length, steps = play_session(agent, learn=False)
        if max_length > best_length:
            best_length = max_length
            best_duration = steps
    return best_length, best_duration, len(agent.q_table)


def print_table(rows):
    header = ("Sessions", "Best length", "Best duration", "States learned")
    widths = [max(len(str(r[i])) for r in [header] + rows)
              for i in range(len(header))]
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def fmt(row):
        return "| " + " | ".join(str(row[i]).rjust(widths[i])
                                 for i in range(len(row))) + " |"
    print(sep)
    print(fmt(header))
    print(sep)
    for row in rows:
        print(fmt(row))
    print(sep)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark Q-learning models trained for "
                    "100, 200, ... 1000, 2000, ... 5000 sessions.")
    parser.add_argument(
        "-force", action="store_true",
        help="Retrain even if the model file already exists")
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(MODELS_DIR, exist_ok=True)

    for count in TRAIN_COUNTS:
        path = os.path.join(MODELS_DIR, f"{count}sess.txt")
        if os.path.exists(path) and not args.force:
            print(f"[skip] {path} already exists")
            continue
        print(f"[train] {count} sessions -> {path}")
        t0 = time.time()
        train_model(count, path)
        print(f"        done in {time.time() - t0:.1f}s")

    rows = []
    for count in TRAIN_COUNTS:
        path = os.path.join(MODELS_DIR, f"{count}sess.txt")
        best_length, best_duration, states = evaluate_model(path)
        rows.append((count, best_length, best_duration, states))
        print(f"[eval]  {count:4d} sessions: "
              f"best length = {best_length}, "
              f"best duration = {best_duration}")

    print()
    print(f"Comparison over {EVAL_SESSIONS} evaluation sessions per model:")
    print_table(rows)


if __name__ == "__main__":
    main()
