import melee
import globals
import Tactics2
import random
from melee.enums import Action, Button
from Strategies2.strategy import Strategy
from Tactics2.punish import Punish
from Tactics2.pressure import Pressure
from Tactics2.defend import Defend
from Tactics2.recover import Recover
from Tactics2.mitigate import Mitigate
from Tactics2.edgeguard import Edgeguard
from Tactics2.infinite import Infinite
from Tactics2.celebrate import Celebrate
from Tactics2.wait import Wait
from Tactics2.retreat import Retreat

class Bait(Strategy):
    def __init__(self):
        self.approach = False

    def __str__(self):
        string = "Bait"

        if not self.tactic:
            return string
        string += str(type(self.tactic))

        if not self.tactic.chain:
            return string
        string += str(type(self.tactic.chain))
        return string

    def step(self):
        opponent_state = globals.opponent_state2
        smashbot_state = globals.smashbot_state2

        # If we have stopped approaching, reset the state
        if type(self.tactic) != Tactics2.Approach:
            self.approach = False

        if Mitigate.needsmitigation():
            self.picktactic(Tactics2.Mitigate)
            return

        if self.tactic and not self.tactic.isinteruptible():
            self.tactic.step()
            return

        # If we're stuck in a lag state, just do nothing. Trying an action might just
        #   buffer an input we don't want
        if Wait.shouldwait():
            self.picktactic(Tactics2.Wait)
            return

        if Recover.needsrecovery():
            self.picktactic(Tactics2.Recover)
            return

        if Celebrate.deservescelebration():
            self.picktactic(Tactics2.Celebrate)
            return

        # Difficulty 5 is a debug / training mode
        #   Don't do any attacks, and don't do any shielding
        #   Take attacks, DI, and recover
        if globals.difficulty2 == 5:
            self.picktactic(Tactics2.KeepDistance)
            return

        if Defend.needsprojectiledefense():
            self.picktactic(Tactics2.Defend)
            return

        # If we can infinite our opponent, do that!
        if Infinite.caninfinite():
            self.picktactic(Tactics2.Infinite)
            return

        # If we can punish our opponent for a laggy move, let's do that
        if Punish.canpunish():
            self.picktactic(Tactics2.Punish)
            return

        # Do we need to defend an attack?
        if Defend.needsdefense():
            self.picktactic(Tactics2.Defend)
            return

        # Can we edge guard them?
        if Edgeguard.canedgeguard():
            self.picktactic(Tactics2.Edgeguard)
            return

        # Can we shield pressure them?
        if Pressure.canpressure():
            self.picktactic(Tactics2.Pressure)
            return

        if Retreat.shouldretreat():
            self.picktactic(Tactics2.Retreat)
            return

        # Is opponent starting a jump?
        jumping = opponent_state.action == Action.KNEE_BEND
        if opponent_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD] and \
                opponent_state.speed_y_self > 0:
            jumping = True

        # Randomly approach some times rather than keeping distance
        if smashbot_state.action == Action.TURNING and random.randint(0, 40) == 0:
            self.approach = True

        if (jumping and opponent_state.invulnerability_left <= 0) or self.approach:
            self.picktactic(Tactics2.Approach)
            return

        self.picktactic(Tactics2.KeepDistance)
