# G-Coder
A lightweight Python package for generating g-code for pen plotters.

## Features
* Drawing paths
* Pen up/down control
* Movement commands
* Context-manager support
* Customizable plotter commands

## Quick Example
__Code:__
```python
from gcoder import GCoder

with GCoder(drawing_name="Squares") as g:
    g.add_comment("Drawing the Inside Square", prefix="; ", as_header=True)
    g.penup()
    g.set_speed(150)

    g.move((-5, -5))
    g.pendown()
    g.move((5, -5))
    g.move((5, 5))
    g.move((-5, 5))
    g.move((-5, -5))
    g.penup()

    g.wait(seconds=5)
    g.add_space()

    g.add_comment("Drawing the Outside Square", as_header=True)
    square_pnts = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    g.draw_path(path=square_pnts, scale=10, offset=(0, 0), loop_to_start=True)

    g.move((0, 0))
```

__Output:__
```none
; --- Drawing the Inside Square ---
; Penup
G4 P0.2500 ; Wait for 0.2500 seconds
G1 F150 ; Set movement speed
G01 X-5.0000 Y-5.0000
; Pendown
G4 P0.2500 ; Wait for 0.2500 seconds
G01 X5.0000 Y-5.0000
G01 X5.0000 Y5.0000
G01 X-5.0000 Y5.0000
G01 X-5.0000 Y-5.0000
; Penup
G4 P0.2500 ; Wait for 0.2500 seconds
G4 P5.0000 ; Wait for 5.0000 seconds

; --- Drawing the Outside Square ---
G01 X-10.0000 Y-10.0000
; Pendown
G4 P0.2500 ; Wait for 0.2500 seconds
G01 X10.0000 Y-10.0000
G01 X10.0000 Y10.0000
G01 X-10.0000 Y10.0000
G01 X-10.0000 Y-10.0000
; Penup
G4 P0.2500 ; Wait for 0.2500 seconds
G01 X0.0000 Y0.0000
```

The output `.gcode` file is placed in the current working directory. The output shown above includes placeholder commands for moving the pen up or down, because that command varies among different pen plotters. See [Getting Started](#getting-started) to find out how to change these.

## Requirements
* Python 3.10+
* No external dependencies

## Installing the Project
To install the project as a Python package, enter the command `pip install git+https://github.com/snarrn/g-coder.git` in a terminal. You can then import the package in Python using `from gcoder import GCoder` or just `import gcoder`.

If you would like to modify the project, you may clone it using `git clone https://github.com/snarrn/g-coder.git`. Look at the [License](#license) section and [LICENSE](LICENSE.md) for more information on how you can use this project.

## Getting Started
The `GCoder` class can be used to write g-code for a variety of pen plotters. Different pen plotters require different commands to perform tasks, such as moving the pen up and down. Because of this, a `PlotterProfile` is used to configure some of these commands, as well as allow for a header and footer to be attached to each g-code file for setup and shutdown.

I used the `GCoder` class to generate g-code for an EleksMaker EleksDraw plotter. The following code shows how I achieved this with `PlotterProfile`. This code is available in the [examples](examples/) folder.

```python
# examples/modify_gcoder.py
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
```

## Updating the Project
If you installed the project using `pip install git+https://github.com/snarrn/g-coder.git`, then you may use `pip install --upgrade git+https://github.com/snarrn/g-coder.git` to install the latest version in its place. If you installed the project with `git clone https://github.com/snarrn/g-coder.git`, then use `git pull` to get the latest version.

## Next Steps
In the future, I may add these features:
* Estimated drawing time
* A drawing visualizer, which shows the pen moving and drawing
* Automatic comment indentation

## Contributions
This project was developed by Nathan Snarr. Generative AI was used for review of code and suggestions.

Feel free to fork the repository and make your own additions. Active collaboration may be limited on my part.

## License
The project is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0). The project's code and assets are free to use and modify with attribution given to the authors. See [LICENSE](LICENSE.md) for more details.