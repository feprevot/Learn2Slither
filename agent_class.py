import ast
import json
import random
from constants import ACTIONS


class Agent:
    def __init__(self, alpha=0.1, gamma=0.98,
                 epsilon=1.0, epsilon_min=0.15, epsilon_decay=0.998):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table = {}

    def get_q(self, state, action):
        """Return Q(state, action). Defaults to 0 if never visited."""
        if state not in self.q_table:
            return 0.0
        return self.q_table[state].get(action, 0.0)

    def set_q(self, state, action, value):
        """Write Q(state, action) into the table."""
        if state not in self.q_table:
            self.q_table[state] = {}
        self.q_table[state][action] = value

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)
        return max(ACTIONS, key=lambda a: self.get_q(state, a))

    def update(self, state, action, reward, next_state, done):
        current_q = self.get_q(state, action)

        if done:
            target = reward
        else:
            future_q = max(self.get_q(next_state, a) for a in ACTIONS)
            target = reward + self.gamma * future_q

        new_q = current_q + self.alpha * (target - current_q)
        self.set_q(state, action, new_q)

        self.decay_epsilon()

    def decay_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, path):
        data = {
            "q_table": {str(s): v for s, v in self.q_table.items()},
            "epsilon": self.epsilon,
            "epsilon_min": self.epsilon_min,
            "epsilon_decay": self.epsilon_decay,
            "alpha": self.alpha,
            "gamma": self.gamma,
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    def load(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        self.q_table = {
            ast.literal_eval(s): v for s, v in data["q_table"].items()
        }
        self.epsilon = data.get("epsilon", self.epsilon_min)
        self.epsilon_min = data.get("epsilon_min", self.epsilon_min)
        self.epsilon_decay = data.get("epsilon_decay", self.epsilon_decay)
        self.alpha = data.get("alpha", self.alpha)
        self.gamma = data.get("gamma", self.gamma)
