import json
import sys
import time
from Queue import Queue
from ast import literal_eval

from ple import PLE
from frogger import frogger_new
import random
from pygame.constants import K_F15, K_w, K_a, K_s, K_d

from froggerState import FroggerState


class QAgent:
    def __init__(self, actions):
        self.second_prev_state = None
        self.actions = actions
        self.step = 0
        self.q_table = self.initialize_q_table()
        self.NOOP = K_F15
        self.prev_state = None
        self.future_state = None
        self.prev_action = None
        self.actions_map = {K_s: "DOWN", K_d: "RIGHT", K_w: "UP", K_a: "LEFT", None: "STAY"}
        self.been_to_intersection = False
        self.most_recent_states = Queue()

    def pick_action(self, reward, obs):
        # Create state and add to q table if it doesn't already exist
        state = FroggerState(reward, obs)
        # # Copy Q val if state has been seen before
        if state.get_id() in self.q_table:
            state.set_n(self.q_table[state.get_id()][1])
            state.set_q_values(self.q_table[state.get_id()][0])

        # print "Current state: " + state.get_id() + " (" + str(state.frog_x) + ", " + str(state.frog_y) + "): " + \
        #           str(state.get_q_value_strings())

        # Add state to q_table
        self.q_table[state.get_id()] = [state.get_q_values(), state.get_n()]

        # Update Q table
        if self.future_state is not None:
            reward = self.modify_reward(state, reward)
            print "Reward: " + str(reward)
            self.prev_state.update_q_value(reward, self.calculate_future_expected_reward(obs, state),
                                           self.prev_action)

        # Add to most recent states
        if self.most_recent_states.qsize() == 5:
            self.most_recent_states.get()
        self.most_recent_states.put(state)

        # Choose new action
        return self.arg_max_action(reward, obs, state)

    def arg_max_action(self, reward, obs, state):
        # rand = random.random()
        # r = False
        # if rand < self.exploration_cutoff and (state.get_frog_y() < 261 or iteration < num_iterations_per_seq/2):
        #     r = True
        #     action = self.actions[random.randint(0, 4)]
        # else:

        # Initialize max variables
        max_q_val = float('-inf')

        # Search for best action
        for action, q_val in state.get_q_values().iteritems():
            if q_val > max_q_val:
                max_q_val = q_val

        # Select action randomly if two actions have the same q-value
        matching = []
        for action, q_val in state.get_q_values().iteritems():
            if q_val == max_q_val:
                matching.append(action)
        action = matching[random.randint(0, len(matching) - 1)]

        self.future_state = state.check_action(action)

        # Save state for death purposes
        if self.future_state.get_id() in self.q_table:
            self.future_state.set_q_values(self.q_table[self.future_state.get_id()][0])
            self.future_state.set_n(self.q_table[self.future_state.get_id()][1])
        else:
            self.future_state.set_q_values({K_w: 0, K_a: 0, K_s: 0, K_d: 0, None: 0})
        self.q_table[self.future_state.get_id()] = [self.future_state.get_q_values(), self.future_state.get_n()]

        if self.prev_state is not None:
            print "\n---- Picking new action ----"
            print "Old state: " + state.get_id() + " (" + str(state.frog_x) + ", " + str(state.frog_y) + "): " + \
                  str(state.get_q_value_strings())
            print "Action: " + self.actions_map[action]
            print "New state: " + self.future_state.get_id() + " (" + str(self.future_state.frog_x) + ", " + \
                  str(self.future_state.frog_y) + "): " + str(self.future_state.get_q_value_strings())

        self.second_prev_state = self.prev_state
        self.prev_action = action
        self.prev_state = state

        return action

    def calculate_future_expected_reward(self, obs, state):
        max_q_val = float('-inf')

        # Search for best action
        for action, q_val in state.get_q_values().iteritems():
            # Calculate expected reward
            # print "Action: " + str(action)
            # print "Q-Val: " + str(q_val)
            if q_val > max_q_val:
                max_q_val = q_val

        print "Expected Future Reward: " + str(max_q_val)

        # Return optimal action
        return max_q_val

    def modify_reward(self, state, reward):
        if abs(reward) == 1.0:
            if reward == 1.0:
                reward = 3.0
            return reward
        else:
            reward = 0.0

        # 2nd to bottom row
        if state.get_frog_y() == 453 and self.prev_state is not None and self.prev_state.get_frog_y() != 485:
            return -0.3
        # Bottom row
        elif state.get_frog_y() == 485:
            return -0.3
        elif self.is_cycle(state):
            return -0.3
        # Infinite loop back and forth
        elif self.second_prev_state is not None and \
                state.get_frog_y() == self.second_prev_state.get_frog_y() and \
                state.get_frog_x() == self.second_prev_state.get_frog_x():
            return -0.3
        # Going back to intersection
        elif self.prev_state is not None and self.prev_state.get_frog_y() == 229 and state.get_frog_y() == 261:
            return -0.3
        # Going down from the intersection
        elif self.prev_state is not None and self.prev_state.get_frog_y == 261 and state.get_frog_y() > 261:
            return -0.5
        # Intersection
        elif state.get_frog_y() == 261 and not self.been_to_intersection:
            self.been_to_intersection = True
            return 0.5
        # Staying in lillypad
        # elif (state.get_frog_y() == 229 or state.get_frog_y() == 133) and self.prev_action is None:
        #     print 'STAYING IN LILLYPAD'
        #     return -0.2

        return reward

    def is_cycle(self, state):
        for index, s in enumerate(list(self.most_recent_states.queue)):
            if state.get_id() == s.get_id() and index != self.most_recent_states.qsize()-1:
                return True
        return False

    def save_q_values(self):
        f = open('q_values.json', 'w')
        f.write(json.dumps(self.q_table))
        f.close()

    @staticmethod
    def initialize_q_table():
        to_ret = {}
        if not use_file:
            print "Not using history file.\n"
            time.sleep(5)
            return {}
        try:
            f = open('q_values.json', 'r')
            data = json.load(f)
            for k, v in data.iteritems():
                to_ret[str(k)] = v
                for index, obj in enumerate(v):
                    to_ret[k][index] = {None if key == 'null' else int(key): value for key, value in data[k][index].iteritems()}
            return to_ret
        except Exception as e:
            print e
            print 'FUCK'
            exit(1)
            return {}


print '\n==== QAgent Frogger Launch ====\n'
if len(sys.argv) > 1:
    use_file = sys.argv[1] == '0'
else:
    use_file = False
game = frogger_new.Frogger()
fps = 40
p = PLE(game, fps=fps,force_fps=False)
agent = QAgent(p.getActionSet())
reward = 0.0
iteration = 0
num_iterations_per_seq = 20000
avg_reward = 0.0
num_games = 0.0
#p.init()

while True:
    iteration += 1
    if iteration % 100 == 0:
        print "Iteration: " + str(iteration)

    if p.game_over():
        print "\nFinal Score: " + str(game.score)
        avg_reward += game.score
        num_games += 1
        print "Average Score: " + str(round(avg_reward/num_games, 2)) + "\n"
        p.reset_game()
        agent.been_to_intersection = False

    obs = game.getGameState()
    # print obs
    action = agent.pick_action(reward, obs)
    reward = p.act(action)
    agent.save_q_values()
    # time.sleep(8)
