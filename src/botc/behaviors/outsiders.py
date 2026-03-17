# src/botc/behaviors/outsiders.py
from botc.enums import RoleName
from .base import RoleBehavior
from . import register_role

@register_role(RoleName.BUTLER)
class ButlerBehavior(RoleBehavior):
    first_night_priority = 9
    other_night_priority = 10
    
    def act(self, player: 'Player', game: 'GameManager'):
        print(f"\nWake {player.believed_role} ({player.player_name}). Who is their Master? Put to sleep.")
