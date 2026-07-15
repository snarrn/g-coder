# Modify GCoder
"""
Showcases how to make a child class of the GCoder class that will work with your pen plotter.
These particular edits were made to work with an EleksMaker EleksDraw.
"""
from gcoder import GCoder, require_unlocked

class GCoderEleksDraw(GCoder):

    DEFAULT_DRAWING_NAME = "MyEleksDrawDrawing"
    DEFAULT_MOVEMENT_SPEED = 200

    POS_HOME = (0, 0)
    ROUND_POS_TO = 4
    ROUND_TIME_TO = 4

    COMMAND_PEN_UP = "M03 S0  ; Penup"
    COMMAND_PEN_DOWN = "M03 S35 ; Pendown"

    WAIT_TIME_PEN_MOVE = 0.175
    
    @require_unlocked
    def initialize_file(self):
        """Writes the header and first few commands to the g-code file."""
        self.add_comment(self.drawing_name, as_header=True)
        self.add_command("A1   ; Enable EleksDraw RC Servo Mode")
        self.add_command("G21  ; Set units to millimeters")
        self.add_command("G90  ; Use absolute positioning")
        self.set_movement_speed(self.movement_speed)
        self.add_space()

        self.add_comment("Homing", as_header=True)
        self.penup()
        self.move_to(self.POS_HOME, quick_move=True)
        self.add_space()

        self.add_comment("Start Drawing!", as_header=True)
    
    @require_unlocked
    def save_drawing(self):
        """Saves the g-code file. This GCoderEleksDraw instance should no longer be used."""
        self.add_space()
        self.add_comment("Ending the Drawing", as_header=True)
        self.penup()
        self.move_to(self.POS_HOME)
        self.add_space()

        self.close_file() # Important to have at the end of this method
