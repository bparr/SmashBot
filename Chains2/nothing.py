import melee
import globals
from Chains.chain import Chain

class Nothing(Chain):
    def step(self):
        globals.controller2.empty_input()
        self.interruptible = True
