from include import Ply, RPly, CHARIZARD, BLASTOISE, VENUSAUR, PIKACHU

# use Ply.possible_moves(battle) to get a list of all possible actions that you can take
# use battle.active_pokemon to get the Pokemon object for your current active pokemon
# use battle.opponent_active_pokemon to get the Pokemon object for the opponent's current active pokemon
# use battle.team or battle.opponent_team to get a dict of <identifier, Pokemon object> for either side's team

class AIPly1(RPly):
    TEAM = CHARIZARD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pr_move = True

    def choose_move(self, battle):
        # Implement this
        return super().choose_move(battle)
    
class AIPly2(RPly):
    TEAM = BLASTOISE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def choose_move(self, battle):
        # Implement this
        return super().choose_move(battle)
    
class AIPly3(RPly):
    TEAM = VENUSAUR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def choose_move(self, battle):
        # Implement this
        return super().choose_move(battle)
    
class AIPly4(RPly):
    TEAM = PIKACHU

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def choose_move(self, battle):
        # Implement this
        return super().choose_move(battle)