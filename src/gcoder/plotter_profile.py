# Plotter Profile
from typing import Tuple, Sequence, Callable
from dataclasses import dataclass
Point2D = Tuple[float, float]

@dataclass
class PlotterProfile:
    command_pen_up: str
    command_pen_down: str

    wait_time_pen_move: float = 0.25
    default_movement_speed: float = 10
    pos_home: Point2D = (0, 0)

    round_pos_to: int = 4
    round_time_to: int = 4

    header_commands: Sequence[str] = tuple()
    footer_commands: Sequence[str] = tuple()

    header_hook: Callable | None = None
    footer_hook: Callable | None = None
