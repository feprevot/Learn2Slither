import argparse
from board_class import Board
from agent_class import Agent
from render_class import Display


def parse_args():
    parser = argparse.ArgumentParser(
        description="Learn2Slither - Snake Q-learning")
    parser.add_argument(
        "-sessions", type=int, default=1, help="Number of training sessions")
    parser.add_argument(
        "-save", type=str, default=None, help="Save model to file")
    parser.add_argument(
        "-load", type=str, default=None, help="Load model from file")
    parser.add_argument(
        "-visual", type=str, default="on", choices=["on", "off"],
        help="Graphical display")
    parser.add_argument(
        "-dontlearn", action="store_true",
        help="Disable learning (exploitation only)")
    parser.add_argument(
        "-step-by-step", dest="step_by_step", action="store_true",
        help="Step-by-step mode")
    parser.add_argument(
        "-speed", type=float, default=0.2,
        help="Display speed in seconds between steps")
    parser.add_argument(
        "-reset-epsilon", dest="reset_epsilon", action="store_true",
        help="Reset epsilon to 1.0 after loading (re-explore)")
    parser.add_argument(
        "-max-steps", dest="max_steps", type=int, default=1000,
        help="Hard cap on steps per session to prevent infinite loops")
    return parser.parse_args()


def run(args):
    agent = Agent()

    if args.load:
        agent.load(args.load)
        print(f"Load trained model from {args.load}")

    if args.reset_epsilon:
        agent.epsilon = 1.0

    if args.dontlearn:
        agent.epsilon = 0.0

    visual = args.visual == "on"
    display = Display(visual=visual, speed=args.speed,
                      step_by_step=args.step_by_step)
    best_score = 0

    for session in range(args.sessions):
        board = Board()
        done = False
        steps = 0
        max_length = board.snake_length()

        while not done and steps < args.max_steps:
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
            length = board.snake_length()
            if length > max_length:
                max_length = length

            if visual:
                display.wait(done)

            if max_length > best_score:
                best_score = max_length

        print(f"Game over, max length = {max_length}, max duration = {steps}")

    display.close()
    print(f"Best score across all sessions: {best_score}")

    if args.save:
        agent.save(args.save)
        print(f"Save learning state in {args.save}")


if __name__ == "__main__":
    args = parse_args()
    run(args)
