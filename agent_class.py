import ast
import random
import json
from constants import ACTIONS


class Agent:
    def __init__(self, alpha=0.1,
                 gamma=0.97, epsilon=1.0, epsilon_min=0.15, epsilon_decay=0.8):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table = {}

    # ---------------------------------------------------------------- Q-table

    def _get_q(self, state, action):
        return self.q_table.get(state, {}).get(action, 0.0)

    def _set_q(self, state, action, value):
        if state not in self.q_table:
            self.q_table[state] = {}
        self.q_table[state][action] = value

    # -------------------------------------------------------------- inference

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)
        q_values = {a: self._get_q(state, a) for a in ACTIONS}
        return max(q_values, key=q_values.get)

    # --------------------------------------------------------------- learning

    def update(self, state, action, reward, next_state, done):
        current_q = self._get_q(state, action)
        if done:
            target = reward
        else:
            best_next = max(self._get_q(next_state, a) for a in ACTIONS)
            target = reward + self.gamma * best_next
        new_q = current_q + self.alpha * (target - current_q)
        self._set_q(state, action, new_q)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # ------------------------------------------------------------ save / load

    def save(self, path):
        data = {
            "q_table": {str(k): v for k, v in self.q_table.items()},
            "epsilon": self.epsilon,
            "alpha": self.alpha,
            "gamma": self.gamma,
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    def load(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        self.q_table = {ast.literal_eval(k): v for k,
                        v in data["q_table"].items()}
        self.epsilon = data.get("epsilon", self.epsilon_min)
        self.alpha = data.get("alpha", self.alpha)
        self.gamma = data.get("gamma", self.gamma)
