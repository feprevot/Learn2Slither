import ast
import json
import random
from constants import ACTIONS


class Agent:
    """
    Tabular Q-learning agent.

    Maintains a Q-table mapping (state, action) -> estimated total future
    reward. On each step the agent:
      1. picks an action: random with probability epsilon (exploration),
         otherwise the action with the highest Q-value (exploitation).
      2. receives a reward and the next state from the board.
      3. updates Q(state, action) with the Bellman equation.
      4. decays epsilon so it explores less over time.
    """

    def __init__(self, alpha=0.1, gamma=0.98,
                 epsilon=1.0, epsilon_min=0.15, epsilon_decay=0.9):
        # alpha   = learning rate: how much a new sample shifts the old Q-value
        # gamma   = discount factor: how much we value future rewards vs now
        # epsilon = exploration rate: probability of taking a random action
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
        """Pick a random action with probability epsilon,
        otherwise the action with the highest Q-value for this state."""
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)

        best_action = ACTIONS[0]
        best_q = self.get_q(state, best_action)
        for action in ACTIONS[1:]:
            q = self.get_q(state, action)
            if q > best_q:
                best_q = q
                best_action = action
        return best_action

    def update(self, state, action, reward, next_state, done):
        """
        Bellman equation:
            Q(s,a) <- Q(s,a) + alpha * (target - Q(s,a))
        where:
            target = reward                                (if episode done)
            target = reward + gamma * max_a' Q(next_s, a') (otherwise)
        """
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
        """Shrink epsilon by epsilon_decay, never going below epsilon_min."""
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self, path):
        """Serialize the Q-table and learning parameters to JSON."""
        # JSON keys must be strings, so we convert each tuple state to its
        # string repr; load() reverses this with ast.literal_eval.
        serialized_q_table = {
            str(state): action_values
            for state, action_values in self.q_table.items()
        }
        data = {
            "q_table": serialized_q_table,
            "epsilon": self.epsilon,
            "alpha": self.alpha,
            "gamma": self.gamma,
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    def load(self, path):
        """Restore a previously saved Q-table and learning parameters."""
        with open(path, 'r') as f:
            data = json.load(f)

        # Parse each string key back into the original tuple state.
        self.q_table = {
            ast.literal_eval(state_str): action_values
            for state_str, action_values in data["q_table"].items()
        }
        self.epsilon = data.get("epsilon", self.epsilon_min)
        self.alpha = data.get("alpha", self.alpha)
        self.gamma = data.get("gamma", self.gamma)
