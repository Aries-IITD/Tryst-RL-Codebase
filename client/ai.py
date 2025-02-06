from include import *

class AIPly1(RPly):
    TEAM = CHARIZARD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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