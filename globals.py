import melee

#Create these objects here and then never again
def init(dolphin, smashbot_port, opponent_port):
    global gamestate
    gamestate = melee.gamestate.GameState(dolphin)
    global controller
    controller = melee.controller.Controller(port=smashbot_port, dolphin=dolphin)
    global opponent_controller
    opponent_controller = melee.controller.Controller(port=opponent_port, dolphin=dolphin)
    global controller2
    controller2 = opponent_controller
    global smashbot_state
    smashbot_state = gamestate.player[smashbot_port]
    global opponent_state2
    opponent_state2 = smashbot_state
    global opponent_state
    opponent_state = gamestate.player[opponent_port]
    global smashbot_state2
    smashbot_state2 = opponent_state
    global framedata
    framedata = melee.framedata.FrameData()
    global logger
    logger = dolphin.logger
    global difficulty
    difficulty = 4
