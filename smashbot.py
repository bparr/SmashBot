#!/usr/bin/python3
import melee
import copy
import argparse
import signal
import sys

from Strategies.bait import Bait
from Strategies2.bait import Bait as Bait2

import globals

def check_port(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4:
         raise argparse.ArgumentTypeError("%s is an invalid controller port. \
         Must be 1, 2, 3, or 4." % value)
    return ivalue

chain = None

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--port', '-p', type=check_port,
                    help='The controller port your AI will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=check_port,
                    help='The controller port the opponent will play on',
                    default=1)
parser.add_argument('--live', '-l',
                    help='The opponent is playing live with a GCN Adapter',
                    default=True)
parser.add_argument('--debug', '-d', action='store_true',
                    help='Debug mode. Creates a CSV of all game state')
parser.add_argument('--difficulty', '-i', type=int,
                    help='Manually specify difficulty level of Smashbot')
parser.add_argument('--difficulty2', '-j', type=int,
                    help='Manually specify difficulty level of smashBot')
parser.add_argument('--nodolphin', '-n', action='store_true',
                    help='Don\'t run dolphin, (it is already running))')
parser.add_argument('--iso_path', required=True,
                    help='Path to SSBM v1.02 ISO.')

args = parser.parse_args()

log = None
if args.debug:
    log = melee.logger.Logger()

#Options here are:
#   "Standard" input is what dolphin calls the type of input that we use
#       for named pipe (bot) input
#   GCN_ADAPTER will use your WiiU adapter for live human-controlled play
#   UNPLUGGED is pretty obvious what it means
opponent_type = melee.enums.ControllerType.UNPLUGGED
if args.live:
    opponent_type = melee.enums.ControllerType.STANDARD

#Create our Dolphin object. This will be the primary object that we will interface with
is_20xx = ('20xx' in args.iso_path.lower())
print('is_20xx:', is_20xx)
dolphin = melee.dolphin.Dolphin(ai_port=args.port, opponent_port=args.opponent,
    opponent_type=opponent_type, logger=log, is_20xx=is_20xx)

#initialize our global objects
globals.init(dolphin, args.port, args.opponent)

gamestate = globals.gamestate
controller = globals.controller
opponent_controller = globals.opponent_controller

def signal_handler(signal, frame):
    dolphin.terminate()
    if args.debug:
        log.writelog()
        print("") #because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#Run dolphin and render the output
if not args.nodolphin:
    dolphin.run(render=True, iso_path=args.iso_path)

#Plug our controller in
#   Due to how named pipes work, this has to come AFTER running dolphin
#   NOTE: If you're loading a movie file, don't connect the controller,
#   dolphin will hang waiting for input and never receive it
controller.connect()
opponent_controller.connect()

strategy = Bait()
strategy2 = Bait2()

strategy_copy = None
strategy2_copy = None

supportedcharacters = [melee.enums.Character.PEACH, melee.enums.Character.CPTFALCON, melee.enums.Character.FALCO, \
    melee.enums.Character.FOX, melee.enums.Character.SAMUS, melee.enums.Character.ZELDA, melee.enums.Character.SHEIK, \
    melee.enums.Character.PIKACHU, melee.enums.Character.JIGGLYPUFF, melee.enums.Character.MARTH]

#Main loop
while True:
    #"step" to the next frame
    gamestate.step()

    #What menu are we in?
    if gamestate.menu_state == melee.enums.Menu.IN_GAME:
        #The strategy "step" will cascade all the way down the objective hierarchy
        if args.difficulty:
            globals.difficulty = int(args.difficulty)
        else:
            globals.difficulty = globals.smashbot_state.stock
        if args.difficulty2:
            globals.difficulty2 = int(args.difficulty2)
        else:
            globals.difficulty2 = globals.smashbot_state2.stock

        if gamestate.stage != melee.enums.Stage.FINAL_DESTINATION:
            melee.techskill.multishine(ai_state=globals.smashbot_state, controller=controller)
        elif globals.opponent_state.character not in supportedcharacters:
            melee.techskill.multishine(ai_state=globals.smashbot_state, controller=controller)
        elif gamestate.frame == 197:
            print('Creating saved state')
            strategy_copy = copy.deepcopy(strategy)
            strategy2_copy = copy.deepcopy(strategy2)
            controller.empty_input()
            opponent_controller.empty_input()
            print(gamestate.frame, gamestate.ai_state.x)
        elif gamestate.frame == 198:
            opponent_controller.press_button(melee.enums.Button.BUTTON_D_RIGHT)
            print(gamestate.frame, gamestate.ai_state.x)
        elif gamestate.frame == 199:
            opponent_controller.press_button(melee.enums.Button.BUTTON_D_RIGHT)
            print(gamestate.frame, gamestate.ai_state.x)
        elif gamestate.frame >= 200 and gamestate.frame % 200 == 0:
            print('Loading saved state')
            controller.empty_input()
            opponent_controller.empty_input()
            print(gamestate.frame, gamestate.ai_state.x)
        elif gamestate.frame >= 200 and gamestate.frame % 200 == 1:
            strategy = copy.deepcopy(strategy_copy)
            strategy2 = copy.deepcopy(strategy2_copy)
            opponent_controller.press_button(melee.enums.Button.BUTTON_D_LEFT)
            print(gamestate.frame, gamestate.ai_state.x)
        else:
            if gamestate.frame >= 200 and gamestate.frame % 200 == 2:
                opponent_controller.release_button(melee.enums.Button.BUTTON_D_LEFT)
                print(gamestate.frame, gamestate.ai_state.x)
            if gamestate.frame >= 200 and gamestate.frame % 200 == 3:
                print(gamestate.frame, gamestate.ai_state.x)
            try:
                strategy.step()
            except Exception as error:
                # Do nothing in case of error thrown!
                controller.empty_input()
                if log:
                    log.log("Notes", "Exception thrown: " + repr(error) + " ", concat=True)
                strategy = Bait()

            try:
                strategy2.step()
            except Exception as error:
                # Do nothing in case of error thrown!
                opponent_controller.empty_input()
                if log:
                    log.log("Notes", "Exception thrown: " + repr(error) + " ", concat=True)
                strategy2 = Bait2()

    #If we're at the character select screen, choose our character
    elif gamestate.menu_state == melee.enums.Menu.CHARACTER_SELECT:
        melee.menuhelper.choosecharacter(character=melee.enums.Character.FOX, opponent=True,
            gamestate=gamestate, controller=opponent_controller, start=False)
        melee.menuhelper.choosecharacter(character=melee.enums.Character.FOX, swag=True,
            gamestate=gamestate, controller=controller, start=True)
    #If we're at the postgame scores screen, spam START
    elif gamestate.menu_state == melee.enums.Menu.POSTGAME_SCORES:
        melee.menuhelper.skippostgame(controller=controller)
        melee.menuhelper.skippostgame(controller=opponent_controller)
    #If we're at the stage select screen, choose a stage
    elif gamestate.menu_state == melee.enums.Menu.STAGE_SELECT:
        melee.menuhelper.choosestage(stage=melee.enums.Stage.FINAL_DESTINATION,
            gamestate=gamestate, controller=controller)
    #Flush any button presses queued up
    controller.flush()
    opponent_controller.flush()

    if log:
        log.log("Notes", "Goals: " + str(strategy), concat=True)
        log.log("Notes", "Goals: " + str(strategy2), concat=True)
        log.logframe(gamestate)
        log.writeframe()
