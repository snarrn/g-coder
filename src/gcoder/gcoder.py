# G-Coder Class
from typing import Tuple, Sequence
from functools import wraps
from .plotter_profile import PlotterProfile
Point2D = Tuple[float, float]

def require_unlocked(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.is_locked:
            raise RuntimeError("Cannot use a GCoder instance whose g-code file is complete (you already ran 'GCoder.save_drawing()' or 'GCoder.__exit__()').")
        return method(self, *args, **kwargs)
    return wrapper

class GCoder:
    """
    Generates g-code for pen plotters.
    """

    @property
    def drawing_name(self):
        return self._drawing_name

    @property
    def movement_speed(self):
        return self._movement_speed
    
    @property
    def pen_pos(self):
        return self._pen_pos
    
    @property
    def pen_is_up(self):
        return self._pen_is_up
    
    @property
    def pen_is_down(self):
        return not self._pen_is_up

    def __init__(self, profile: PlotterProfile | None = None, drawing_name: str = "MyDrawing", pen_starts_up: bool = False):
        self.profile = profile or PlotterProfile()
        self._drawing_name = drawing_name

        self._movement_speed = self.profile.default_movement_speed
        self._pen_pos = self.profile.pos_home

        self._pen_is_up = pen_starts_up
        self.is_locked = False

        self.__file = open(self._drawing_name + ".gcode", "w")
        self.initialize_file()

    @require_unlocked
    def __enter__(self):
        """Enters a context via the 'with' statement."""
        return self
    
    @require_unlocked
    def __exit__(self, exc_type, exc_value, traceback):
        """Exits the context of a 'with' statement, which closes the gcode file. This GCoder instance should no longer be used."""
        self.save_drawing()

        return False
    
    @require_unlocked
    def initialize_file(self):
        """Writes the g-code file header.
        
        The header is based on profile.header_hook or, if profile.header_hook is None, then each string from profile.header_commands is written on a new line."""
        if self.profile.header_hook is not None:
            self.profile.header_hook(self)
        
        else:
            for command in self.profile.header_commands:
                self.add_command(command)

    @require_unlocked
    def add_space(self, num_blank_lines: int = 1):
        """Add blank lines to the g-code file. Defaults to a single blank line."""
        for _ in range(num_blank_lines):
            self.__file.write("\n")
    
    @require_unlocked
    def add_command(self, command: str, prefix: str = "\n"):
        """Adds a command to the g-code file."""
        self.__file.write(prefix + command)
    
    @require_unlocked
    def add_comment(self, comment: str, prefix: str = "\n; ", as_header: bool = False):
        """Adds a comment to the g-code file. Set 'as_header' to True to place '---' before and after the comment."""
        self.__file.write((prefix + "--- " + comment + " ---") if as_header else (prefix + comment))
    
    @require_unlocked
    def set_movement_speed(self, movement_speed: float):
        """Sets a new movement speed."""
        self._movement_speed = movement_speed
        self.add_command(f"G1 F{self._movement_speed} ; Set movement speed")
    
    @require_unlocked
    def draw_path(self, path: Sequence[Point2D], scale: float | tuple[float, float] = 1.0, offset: tuple[float, float] = (0.0, 0.0), quick_move_to_start: bool = False, drag_to_start: bool = False, loop_to_start: bool = False):
        """Draws along a path of points, which may be scaled and given an offset. Set 'drag_to_start' to True to keep the pen down when moving to the start of the path. Set 'loop_to_start' to True to draw from the last point to the first."""
        if len(path) == 0:
            return
        
        pen_was_up = self.pen_is_up

        if drag_to_start:
            self.pendown()
        
        else:
            self.penup()
        
        if isinstance(scale, (float, int)):
            modified_path = tuple((pos[0] * scale + offset[0], pos[1] * scale + offset[1]) for pos in path)
        
        else:
            modified_path = tuple((pos[0] * scale[0] + offset[0], pos[1] * scale[1] + offset[1]) for pos in path)
        
        self.move_to(modified_path[0], quick_move=quick_move_to_start)
        self.pendown()

        for pos in modified_path[1:]:
            self.move_to(pos)
        
        if loop_to_start:
            self.move_to(modified_path[0])
        
        if pen_was_up:
            self.penup()
    
    @require_unlocked
    def move_to(self, pos: Point2D, quick_move: bool = False):
        """Moves to a new position. Set 'quick_move' to True for g-code 'G00' (instead of 'G01')."""
        self.add_command(("G00" if quick_move else "G01") + f" X{pos[0]:.{self.profile.round_pos_to}f} Y{pos[1]:.{self.profile.round_pos_to}f}")
        self._pen_pos = (round(pos[0], self.profile.round_pos_to), round(pos[1], self.profile.round_pos_to))
    
    @require_unlocked
    def penup(self):
        """Moves the pen up, if it isn't already."""
        if self.pen_is_down:
            self.add_command(self.profile.command_pen_up)
            self.wait(self.profile.wait_time_pen_move)

            self._pen_is_up = True
    
    @require_unlocked
    def pendown(self):
        """Moves the pen down, if it isn't already."""
        if self.pen_is_up:
            self.add_command(self.profile.command_pen_down)
            self.wait(self.profile.wait_time_pen_move)

            self._pen_is_up = False
    
    @require_unlocked
    def wait(self, seconds: float):
        """Waits the given amount of seconds. Ignores non-positive values."""
        if seconds > 0:
            self.add_command(f"G4 P{seconds:.{self.profile.round_time_to}f} ; Wait for {seconds:.{self.profile.round_time_to}f} seconds")
    
    @require_unlocked
    def save_drawing(self):
        """Writes the g-code file footer and closes the file. This GCoder instance should no longer be used.
        
        The footer is based on profile.footer_hook or, if profile.footer_hook is None, then each string from profile.footer_commands is written on a new line."""
        if self.profile.footer_hook is not None:
            self.profile.footer_hook(self)
        
        else:
            for command in self.profile.footer_commands:
                self.add_command(command)
        
        self.close_file()
    
    def close_file(self):
        """Closes the g-code file and locks the GCoder instance."""
        self.__file.flush()
        self.__file.close()
        self.is_locked = True
