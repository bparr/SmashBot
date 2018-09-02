import melee
from Strategies.bait import Bait

"""
Expert system agent for SmashBot.
This is the "manually programmed" TAS-looking agent.
Only plays Fox on FD.
"""
class ESAgent():
    def __init__(self, controller, gamestate, smashbot_port, opponent_port):
        self.gamestate = gamestate
        self.controller = controller
        self.smashbot_state = self.gamestate.player[smashbot_port]
        self.opponent_state = self.gamestate.player[opponent_port]
        self.framedata = melee.framedata.FrameData()
        self.logger = gamestate.logger
        self.forced_difficulty = None
        self.reset()

    def force_difficulty(self, difficulty):
      self.forced_difficulty = difficulty

    def get_difficulty(self):
        difficulty = self.forced_difficulty
        if difficulty is None:
          difficulty = self.smashbot_state.stock
        return difficulty

    def act(self):
        self.strategy.difficulty = self.get_difficulty()
        self.strategy.step()

    def reset(self):
        self.strategy = Bait(
            self.gamestate, self.smashbot_state, self.opponent_state,
            self.logger, self.controller, self.framedata, self.get_difficulty())
