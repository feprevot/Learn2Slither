import argparse
import sys
from board import Board
from agent import Agent
from display import Display


def parse_args():
    parser = argparse.ArgumentParser(description="Learn2Slither - Snake Q-learning")
    parser.add_argument("-sessions", type=int, default=1, help="Number of training sessions")
    parser.add_argument("-save", type=str, default=None, help="Save model to file")
    parser.add_argument("-load", type=str, default=None, help="Load model from file")
    parser.add_argument("-visual", type=str, default="on", choices=["on", "off"], help="Graphical display")
    parser.add_argument("-dontlearn", action="store_true", help="Disable learning (exploitation only)")
    parser.add_argument("-step-by-step", dest="step_by_step", action="store_true", help="Step-by-step mode")
    parser.add_argument("-speed", type=float, default=0.2, help="Display speed in seconds between steps")
    return parser.parse_args()


def run(args):
    agent = Agent()

    if args.load:
        agent.load(args.load)
        print(f"Load trained model from {args.load}")

    visual = args.visual == "on"
    display = Display(visual=visual, speed=args.speed, step_by_step=args.step_by_step)

    max_length_all = 0
    max_duration_all = 0

    for session in range(args.sessions):
        board = Board()
        done = False
        steps = 0

        while not done:
            state = board.get_state()

            if visual:
                display.render(board)
                display.print_vision(board)

            action = agent.choose_action(state)

            if visual:
                print(f"Action: {action}")

            reward, done = board.step(action)

            if not args.dontlearn:
                next_state = board.get_state() if not done else state
                agent.update(state, action, reward, next_state, done)

            steps += 1

            if visual:
                display.wait(done)

        length = board.snake_length()
        if length > max_length_all:
            max_length_all = length
        if steps > max_duration_all:
            max_duration_all = steps

    display.close()
    print(f"Game over, max length = {max_length_all}, max duration = {max_duration_all}")

    if args.save:
        agent.save(args.save)
        print(f"Save learning state in {args.save}")


if __name__ == "__main__":
    args = parse_args()
    run(args)
