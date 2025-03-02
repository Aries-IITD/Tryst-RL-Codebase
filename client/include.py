from poke_env.player.player import Player
from dataclasses import dataclass
from logging import Logger
from typing import Any, Dict, List, Union, Optional
from poke_env.environment import AbstractBattle, Battle
from poke_env.environment.move import Move
from poke_env.environment.pokemon_type import PokemonType
from poke_env import AccountConfiguration
from poke_env.ps_client.account_configuration import CONFIGURATION_FROM_PLAYER_COUNTER
from poke_env.data import GenData
from poke_env.environment.double_battle import DoubleBattle
from poke_env.environment.pokemon import Pokemon
from poke_env.exceptions import ShowdownException
from poke_env.teambuilder.constant_teambuilder import ConstantTeambuilder
import hashlib
import random

CHARIZARD = "teams/charizard.txt"
BLASTOISE = "teams/blastoise.txt"
VENUSAUR = "teams/venusaur.txt"
PIKACHU = "teams/pikachu.txt"

TEAMS = [CHARIZARD, BLASTOISE, VENUSAUR, PIKACHU]

class Battle(Battle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Turn choice attributes
        self._can_mega_evolve_x: bool = False
        self._can_mega_evolve_y: bool = False
    
    @property
    def can_mega_evolve_x(self) -> bool:
        """
        :return: Whether or not the current active pokemon can mega evolve X.
        :rtype: bool
        """
        return self._can_mega_evolve_x
    
    @property
    def can_mega_evolve_y(self) -> bool:
        """
        :return: Whether or not the current active pokemon can mega evolve Y.
        :rtype: bool
        """
        return self._can_mega_evolve_y
    
    def parse_request(self, request: Dict[str, Any]) -> None:
        """
        Update the object from a request.
        The player's pokemon are all updated, as well as available moves, switches and
        other related information (z move, mega evolution, forced switch...).

        :param request: Parsed JSON request object.
        :type request: dict
        """
        if "wait" in request and request["wait"]:
            self._wait = True
        else:
            self._wait = False

        side = request["side"]

        self._available_moves = []
        self._available_switches = []
        self._can_mega_evolve = False
        self._can_mega_evolve_x = False
        self._can_mega_evolve_y = False
        self._can_z_move = False
        self._can_dynamax = False
        self._can_tera = None
        self._maybe_trapped = False
        self._reviving = any(
            [m["reviving"] for m in side.get("pokemon", []) if "reviving" in m]
        )
        self._trapped = False
        self._force_switch = request.get("forceSwitch", [False])[0]

        if self._force_switch:
            self._move_on_next_request = True

        self._last_request = request

        if request.get("teamPreview", False):
            self._teampreview = True
            number_of_mons = len(request["side"]["pokemon"])
            self._max_team_size = request.get("maxTeamSize", number_of_mons)
        else:
            self._teampreview = False
        self._update_team_from_request(request["side"])

        if "active" in request:
            active_request = request["active"][0]

            if active_request.get("trapped"):
                self._trapped = True

            if self.active_pokemon is not None:
                self._available_moves.extend(
                    self.active_pokemon.available_moves_from_request(active_request)
                )

            if active_request.get("canMegaEvo", False):
                self._can_mega_evolve = True
            if active_request.get("canMegaEvoX", False):
                self._can_mega_evolve_x = True
            if active_request.get("canMegaEvoY", False):
                self._can_mega_evolve_y = True
            if active_request.get("canZMove", False):
                self._can_z_move = True
            if active_request.get("canDynamax", False):
                self._can_dynamax = True
            if active_request.get("maybeTrapped", False):
                self._maybe_trapped = True
            if active_request.get("canTerastallize", False):
                self._can_tera = PokemonType.from_name(
                    active_request["canTerastallize"]
                )

        if side["pokemon"]:
            self._player_role = side["pokemon"][0]["ident"][:2]

        if not self.trapped and not self.reviving:
            for pokemon in side["pokemon"]:
                if pokemon:
                    pokemon = self._team[pokemon["ident"]]
                    if not pokemon.active and not pokemon.fainted:
                        self._available_switches.append(pokemon)

        if not self.trapped and self.reviving:
            for pokemon in side["pokemon"]:
                if pokemon and pokemon.get("reviving", False):
                    pokemon = self._team[pokemon["ident"]]
                    if not pokemon.active:
                        self._available_switches.append(pokemon)

@dataclass
class BattleOrder:
    order: Optional[Union[Move, Pokemon]]
    mega: bool = False
    megax: bool = False
    megay: bool = False
    z_move: bool = False
    dynamax: bool = False
    terastallize: bool = False
    move_target: int = DoubleBattle.EMPTY_TARGET_POSITION

    DEFAULT_ORDER = "/choose default"

    def __str__(self) -> str:
        return self.message

    @property
    def message(self) -> str:
        if isinstance(self.order, Move):
            if self.order.id == "recharge":
                return "/choose move 1"
            
            message = f"/choose move {self.order.id}"
            if self.mega:
                message += " mega"
            if self.megax:
                message += " megax"
            if self.megay:
                message += " megay"
            elif self.z_move:
                message += " zmove"
            elif self.dynamax:
                message += " dynamax"
            elif self.terastallize:
                message += " terastallize"

            if self.move_target != DoubleBattle.EMPTY_TARGET_POSITION:
                message += f" {self.move_target}"
            return message
        elif isinstance(self.order, Pokemon):
            return f"/choose switch {self.order.species}"
        else:
            return ""

class DefaultBattleOrder(BattleOrder):
    def __init__(self, *args: Any, **kwargs: Any):
        pass

    @property
    def message(self) -> str:
        return self.DEFAULT_ORDER

class Ply(Player):
    async def _create_battle(self, split_message: List[str]) -> AbstractBattle:
        """Returns battle object corresponding to received message.

        :param split_message: The battle initialisation message.
        :type split_message: List[str]
        :return: The corresponding battle object.
        :rtype: AbstractBattle
        """
        # We check that the battle has the correct format
        if split_message[1] == self._format and len(split_message) >= 2:
            # Battle initialisation
            battle_tag = "-".join(split_message)[1:]

            if battle_tag in self._battles:
                return self._battles[battle_tag]
            else:
                gen = GenData.from_format(self._format).gen
                if self.format_is_doubles:
                    battle: AbstractBattle = DoubleBattle(
                        battle_tag=battle_tag,
                        username=self.username,
                        logger=self.logger,
                        save_replays=self._save_replays,
                        gen=gen,
                    )
                else:
                    battle = Battle(
                        battle_tag=battle_tag,
                        username=self.username,
                        logger=self.logger,
                        gen=gen,
                        save_replays=self._save_replays,
                    )

                # Add our team as teampreview_team, as part of battle initialisation
                if isinstance(self._team, ConstantTeambuilder):
                    battle.teampreview_team = set(
                        [
                            Pokemon(gen=gen, teambuilder=tb_mon)
                            for tb_mon in self._team.team
                        ]
                    )

                await self._battle_count_queue.put(None)
                if battle_tag in self._battles:
                    await self._battle_count_queue.get()
                    return self._battles[battle_tag]
                async with self._battle_start_condition:
                    self._battle_semaphore.release()
                    self._battle_start_condition.notify_all()
                    self._battles[battle_tag] = battle

                if self._start_timer_on_battle_start:
                    await self.ps_client.send_message("/timer on", battle.battle_tag)

                return battle
        else:
            self.logger.critical(
                "Unmanaged battle initialisation message received: %s", split_message
            )
            raise ShowdownException()
        
    @staticmethod
    def possible_moves(battle: Battle) -> List[BattleOrder]:
        available_orders = [BattleOrder(move) for move in battle.available_moves]
        available_orders.extend(
            [BattleOrder(switch) for switch in battle.available_switches]
        )

        if battle.can_mega_evolve and (battle.active_pokemon.species in ["blastoise", "venusaur"]):
            available_orders.extend(
                [BattleOrder(move, mega=True) for move in battle.available_moves]
            )

        # if battle.can_mega_evolve_x:
        #     available_orders.extend(
        #         [BattleOrder(move, megax=True) for move in battle.available_moves]
        #     )
        
        if battle.can_mega_evolve_y  and (battle.active_pokemon.species in "charizard"):
            available_orders.extend(
                [BattleOrder(move, megay=True) for move in battle.available_moves]
            )

    @staticmethod
    def choose_default_move() -> DefaultBattleOrder:
        """Returns showdown's default move order.

        This order will result in the first legal order - according to showdown's
        ordering - being chosen.
        """
        return DefaultBattleOrder()

    @staticmethod
    def choose_random_singles_move(battle: Battle) -> BattleOrder:
        available_orders = Ply.possible_moves(battle)

        if available_orders:
            return available_orders[int(random.random() * len(available_orders))]
        else:
            return Ply.choose_default_move()
        
    @staticmethod
    def choose_random_move(battle: AbstractBattle) -> BattleOrder:
        """Returns a random legal move from battle.

        :param battle: The battle in which to move.
        :type battle: AbstractBattle
        :return: Move order
        :rtype: str
        """
        if isinstance(battle, DoubleBattle):
            return Player.choose_random_doubles_move(battle)
        elif isinstance(battle, Battle):
            return Ply.choose_random_singles_move(battle)
        else:
            raise ValueError(
                f"battle should be Battle or DoubleBattle. Received {type(battle)}"
            )

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
    
    @staticmethod
    def create_order(
        order: Union[Move, Pokemon],
        mega: bool = False,
        megax: bool = False,
        megay: bool = False,
        z_move: bool = False,
        dynamax: bool = False,
        terastallize: bool = False,
        move_target: int = DoubleBattle.EMPTY_TARGET_POSITION,
    ) -> BattleOrder:
        """Formats an move order corresponding to the provided pokemon or move.

        :param order: Move to make or Pokemon to switch to.
        :type order: Move or Pokemon
        :param mega: Whether to mega evolve the pokemon, if a move is chosen.
        :type mega: bool
        :param z_move: Whether to make a zmove, if a move is chosen.
        :type z_move: bool
        :param dynamax: Whether to dynamax, if a move is chosen.
        :type dynamax: bool
        :param terastallize: Whether to terastallize, if a move is chosen.
        :type terastallize: bool
        :param move_target: Target Pokemon slot of a given move
        :type move_target: int
        :return: Formatted move order
        :rtype: str
        """
        return BattleOrder(
            order,
            mega=mega,
            megax=megax,
            megay=megay,
            move_target=move_target,
            z_move=z_move,
            dynamax=dynamax,
            terastallize=terastallize,
        )
    
    def __init__(self, *args, code='default', **kwargs):
        super().__init__(*args, account_configuration=self._create_account_configuration(code), **kwargs)

def valid_move(battle: AbstractBattle, move: BattleOrder) -> BattleOrder:
    valid = True
    nm = move
    if move.megax:
        valid = False
        nm.megax = False
    if move.mega and (battle.active_pokemon.species not in ["blastoise", "venusaur"]):
        valid = False
        nm.mega = False
    if move.megay and (battle.active_pokemon.species != "charizard"):
        valid = False
        nm.megay = False
    if move.dynamax:
        valid = False
        move.dynamax = False
    if move.terastallize:
        valid = False
        move.terastallize = False
    if move.z_move:
        valid = False
        move.z_move = False

    return valid, move

class RPly(Ply):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pr_move = False

    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        move = self.choose_random_move(battle)
        while not valid_move(battle, move):
            move = self.choose_random_move(battle)

        return move