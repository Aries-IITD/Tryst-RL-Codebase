from poke_env.player.player import Player
from poke_env.environment import AbstractBattle
from poke_env.player.battle_order import BattleOrder
from poke_env import AccountConfiguration
from poke_env.ps_client.account_configuration import CONFIGURATION_FROM_PLAYER_COUNTER
import hashlib

CHARIZARD = "teams/charizard.txt"
BLASTOISE = "teams/blastoise.txt"
VENUSAUR = "teams/venusaur.txt"
PIKACHU = "teams/pikachu.txt"

TEAMS = [CHARIZARD, BLASTOISE, VENUSAUR, PIKACHU]

class Ply(Player):
    def _create_account_configuration(self, code="default") -> AccountConfiguration:
        key = type(self).__name__
        hk = hashlib.md5(code.encode('utf-8')).hexdigest()[:6]
        CONFIGURATION_FROM_PLAYER_COUNTER.update([key])
        username = "%s%s%d" % (hk, key, CONFIGURATION_FROM_PLAYER_COUNTER[key])
        if len(username) > 18:
            username = "%s%s%d" % (
                hk,
                key[: 18 - len(username)],
                CONFIGURATION_FROM_PLAYER_COUNTER[key],
            )
        return AccountConfiguration(username, code)
    
    def __init__(self, *args, code='default', **kwargs):
        super().__init__(*args, account_configuration=self._create_account_configuration(code), **kwargs)
    
class RPly(Ply):
    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        return self.choose_random_move(battle)