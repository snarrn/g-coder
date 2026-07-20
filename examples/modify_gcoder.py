# Modify GCoder
"""
Showcases how to make a PlotterProfile so the GCoder class work with your pen plotter.
These particular edits were made to work with an EleksMaker EleksDraw.
"""
from gcoder import GCoder, require_unlocked
from gcoder.plotter_profile import PlotterProfile

def eleks_header(g: GCoder):
    """Writes a g-code file header for the EleksMaker EleksDraw."""
    g.add_comment(g.drawing_name, as_header=True, prefix="; ")
    g.add_command("A1   ; Enable EleksDraw RC Servo Mode")
    g.add_command("G21  ; Set units to millimeters")
    g.add_command("G90  ; Use absolute positioning")
    g.set_speed(g.speed)
    g.add_space()

    g.add_comment("To Home Position", as_header=True)
    g.penup()
    g.move(g.profile.pos_home, quick_move=True)
    g.add_space()

    g.add_comment("Start Drawing!", as_header=True)

def eleks_footer(g: GCoder):
    """Writes a g-code file footer for the EleksMaker EleksDraw."""
    g.add_space()
    g.add_comment("Ending the Drawing", as_header=True)
    g.penup()
    g.move(g.profile.pos_home)
    g.add_space()

eleks_profile = PlotterProfile(command_pen_up="M03 S0  ; Penup",
                               command_pen_down="M03 S35 ; Pendown",
                               wait_time_pen_move=0.175,
                               default_speed=200,
                               pos_home=(0, 0),
                               round_pos_to=4,
                               round_time_to=4,
                               header_hook=eleks_header,
                               footer_hook=eleks_footer)

with GCoder(profile=eleks_profile, drawing_name="ModifyGCoder") as g:
    g.add_comment("Test Comment")
