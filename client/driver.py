from include import Ply, RPly, CHARIZARD, TEAMS, Battle
from poke_env import ServerConfiguration
from poke_env.data import GenData
import asyncio 
import argparse
import os
from ai import *
import random

key_to_class = {"random": RPly, "ai1": AIPly1, "ai2": AIPly2, "ai3": AIPly3, "ai4": AIPly4}
AIS = list(key_to_class.keys())

# parser = argparse.ArgumentParser()

# parser.add_argument('ai1', type=str, choices=['random', 'ai1', 'ai2', 'ai3', 'ai4'], help="First player class")
# parser.add_argument('ai2', nargs='?', type=str, default="random", choices=['random', 'ai1', 'ai2', 'ai3', 'ai4'], help="Second player class")
# parser.add_argument('--mode', '--m', type=str, default="battle", choices=['battle', 'ladder', 'accept', 'challenge'], help="Type of battles to commence")
# parser.add_argument('--id', type=str, default="", help="ID for account name")
# parser.add_argument('--replay', '--replays', '--r', action="store_true", help="Save replays in replays folder")
# parser.add_argument('--n', '--num_battles', '--num', type=int, default=1, help="Number of battles to conduct")
# args = parser.parse_args()

parser = argparse.ArgumentParser(description="Driver script for executing battles with your custom AI")

common = argparse.ArgumentParser(add_help=False)
common.add_argument("ai1", choices=AIS, help="First player class")
common.add_argument("--id", type=str, default="", help="ID for account name")
common.add_argument("--replay", "--replays", "-r", action="store_true", help="Save replays in replays folder")
common.add_argument("--n", "--num_battles", "--num", type=int, default=1, help="Number of battles / challenges")
subparsers = parser.add_subparsers(dest="mode", required=True)

battle = subparsers.add_parser("battle", parents=[common])
battle.add_argument("ai2", nargs="?", default="random", choices=AIS, help="Second player class to battle against")

ladder = subparsers.add_parser("ladder", parents=[common])
ladder.add_argument("ai2", nargs="?", type=str, default="random", help="Placeholder")

challenge = subparsers.add_parser("challenge", parents=[common])
challenge.add_argument("ai2", type=str, help="Player name to send challenges to")

accept = subparsers.add_parser("accept", parents=[common])
accept.add_argument("ai2", nargs="?", type=str, default=None, help="Player name to accept challenges from, or None to accept from all")

args = parser.parse_args()

ai1 = args.ai1
ai2 = args.ai2

suff = args.id
num_battles = args.n
mode = args.mode
save_replay = 'replay' if args.replay else False

server_url = ""

try:
    with open("env.txt") as F:
        data = [x.strip() for x in F.readlines()]
        server_url = data[0]
        codes = data[1:]
except:
    Exception("Env file error!")

codes = [code + suff for code in codes]

LocalServerConfig = ServerConfiguration( 
    server_url, 
    "https://play.pokemonshowdown.com/action.php?"
)

def get_kwargs(ply, sr=False, ind=0):
    D = {
        "server_configuration": LocalServerConfig,
        "code": codes[ind],
        "start_timer_on_battle_start": True,
        "battle_format": 'gen9nationaldex',
        "log_level": 0,
        "save_replays": sr
    }

    if ply == "random":
        filename = random.choice(TEAMS)
    else:
        filename = key_to_class[ply].TEAM
    
    if not os.path.exists(filename):
        filename = CHARIZARD

    with open(filename, 'r') as file:
        D["team"] = file.read().strip()

    return D

player1 = key_to_class[ai1](**get_kwargs(ai1, sr=save_replay))
if mode == "battle":
    player2 = key_to_class[ai2](**get_kwargs(ai2))
else:
    player2 = None

async def main(log=False):

    if mode =='battle':
        await player1.battle_against(player2, n_battles=num_battles)

    if mode == 'ladder':
        await player1.ladder(num_battles)

    if mode == 'accept':
        await player1.accept_challenges(None, n_challenges=num_battles)

    if mode == 'challenge':
        await player1.send_challenges(ai2, n_challenges=num_battles)

    if log:
        # for battle_tag, battle in player1.battles.items():
        #     print(battle_tag, battle.won)

        print(sum([x.won for x in player1.battles.values() if x is not None]) / len(player1.battles))


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main(True))