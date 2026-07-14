# G-Coder Class
from typing import Sequence
from functools import wraps
Point2D = tuple[float, float]

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

    DEFAULT_DRAWING_NAME = "MyDrawing"
    DEFAULT_MOVEMENT_SPEED = 10

    POS_HOME = (0, 0)
    ROUND_POS_TO = 4
    ROUND_TIME_TO = 4

    COMMAND_PEN_UP = "; <g-code for moving the pen up>"
    COMMAND_PEN_DOWN = "; <g-code for moving the pen down>"

    WAIT_TIME_PEN_MOVE = 0

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

    def __init__(self, drawing_name: str | None = None, movement_speed: float | None = None):
        self._drawing_name = drawing_name or GCoder.DEFAULT_DRAWING_NAME
        self._movement_speed = movement_speed or GCoder.DEFAULT_MOVEMENT_SPEED

        self._pen_is_up = False
        self._pen_pos = GCoder.POS_HOME

        self.is_locked = False

        self.__file = open(self._drawing_name + ".gcode", "w")
        self.initialize_file()
    
    @require_unlocked
    def __enter__(self):
        """Enters a context via the 'with' statement."""
        return self
    
    @require_unlocked
    def __exit__(self, exc_type, exc_value, traceback):
        """Exits the context of a 'with' statement, which closes the gcode file. This GCoder instance should not be used anymore."""
        self.save_drawing()

        return False
    
    @require_unlocked
    def initialize_file(self):
        """Writes the header and initial commands to the gcode file."""
        self.add_comment(f"{self._drawing_name}", prefix="; ", as_header=True)
        self.set_movement_speed(self._movement_speed)
        self.penup()
        self.move_to(GCoder.POS_HOME, quick_move=True)
        self.add_comment("^ Here is where the initial commands go for setup...")
        self.add_space()
        
        self.add_comment("Start Drawing", as_header=True)

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
    def draw_path(self, path: Sequence[Point2D], scale: float | tuple[float, float] = 1.0, offset: tuple[float, float] = (0.0, 0.0), drag_to_start: bool = False, loop_to_start: bool = False):
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
        
        self.move_to(modified_path[0])
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
        self.add_command(("G00" if quick_move else "G01") + f" X{pos[0]:.{GCoder.ROUND_POS_TO}f} Y{pos[1]:.{GCoder.ROUND_POS_TO}f}")
        self._pen_pos = (round(pos[0], GCoder.ROUND_POS_TO), round(pos[1], GCoder.ROUND_POS_TO))
    
    @require_unlocked
    def penup(self):
        """Moves the pen up, if it isn't already."""
        if self.pen_is_down:
            self.add_command(GCoder.COMMAND_PEN_UP)
            self.wait(GCoder.WAIT_TIME_PEN_MOVE)

            self._pen_is_up = True
    
    @require_unlocked
    def pendown(self):
        """Moves the pen down, if it isn't already."""
        if self.pen_is_up:
            self.add_command(GCoder.COMMAND_PEN_DOWN)
            self.wait(GCoder.WAIT_TIME_PEN_MOVE)

            self._pen_is_up = False
    
    @require_unlocked
    def wait(self, time: float):
        """Waits the given amount of time. Ignores non-positive values."""
        if time > 0:
            self.add_command(f"G4 P{time:.{GCoder.ROUND_TIME_TO}f} ; Wait for {time:.{GCoder.ROUND_TIME_TO}f} seconds")
    
    @require_unlocked
    def save_drawing(self):
        """Saves the g-code file. This GCoder instance should no longer be used."""
        self.add_space()
        self.add_comment("Ending the Drawing", as_header=True)
        self.penup()
        self.move_to(GCoder.POS_HOME)
        self.add_space()

        self.__close_file()
    
    def __close_file(self):
        """Closes the g-code file and locks the GCoder instance."""
        self.__file.flush()
        self.__file.close()
        self.is_locked = True
