from ple import PLE
import frogger_new
import numpy as np
from pygame.constants import K_w,K_a,K_F15, K_s, K_d

class NaiveAgent():
    def __init__(self, actions):
        self.actions = actions
        self.step = 0
        self.NOOP = K_F15

    def pickAction(self, reward, obs):
        return self.NOOP
        #Uncomment the following line to get random actions
        #return self.actions[np.random.randint(0,len(self.actions))]

game = frogger_new.Frogger()
fps = 30
p = PLE(game, fps=fps,force_fps=False)
agent = NaiveAgent(p.getActionSet())
print "Up: " + str(K_w)
print "Left: " + str(K_a)
print "Down: " + str(K_s)
print "Right: " + str(K_d)

print(p.getActionSet())
# exit()
reward = 0.0

#p.init()

while True:
    if p.game_over():
        p.reset_game()

    obs = game.getGameState()
    print obs
    action = agent.pickAction(reward, obs)
    reward = p.act(action)
    #print game.score
