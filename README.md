# G-Coder
A lightweight Python class useful for generating g-code for pen plotters.

## Features
* Drawing paths
* Pen up/down control
* Movement commands
* Context-manager support
* Customizable plotter commands

## Quick Example Code and Output
```python
from gcoder import GCoder

with GCoder("MyDrawing", movement_speed=10) as g:
    g.add_comment("Hello, World!")
    g.move_to((4, 2))
    g.pendown()
    g.move_to((2, 4))
    g.penup()

    pnts = ((0, 1), (1, -1), (2, 1), (3, -1))

    g.add_space()
    g.add_comment("Drawing Zig-Zag", as_header=True)
    g.wait(seconds=5)
    g.draw_path(path=pnts, scale=5, offset=(0, 0))
```

__Output:__
```none
; --- MyDrawing ---
G1 F10 ; Set movement speed
; <g-code for moving the pen up>
G00 X0.0000 Y0.0000
; ^ Here is where the initial commands go for setup...

; --- Start Drawing ---
; Hello, World!
G01 X4.0000 Y2.0000
; <g-code for moving the pen down>
G01 X2.0000 Y4.0000
; <g-code for moving the pen up>

; --- Drawing Zig-Zag ---
G4 P5.0000 ; Wait for 5.0000 seconds
G01 X0.0000 Y5.0000
; <g-code for moving the pen down>
G01 X5.0000 Y-5.0000
G01 X10.0000 Y5.0000
G01 X15.0000 Y-5.0000
; <g-code for moving the pen up>

; --- Ending the Drawing ---
G01 X0.0000 Y0.0000
```

The output `.gcode` file is placed in the current working directory. The output shown above includes a default header and footer as well as some placeholder commands. See __Getting Started__ to find out how to change these.

## Requirements
* Python 3.10+
* No external dependencies

## Installing the Project
To install the project as a Python package, enter the command `pip install git+https://github.com/snarrn/g-coder.git` in a terminal. You can then import the package in Python using `from gcoder import GCoder` or just `import gcoder`.

If you would like to modify the project, you may clone it using `git clone https://github.com/snarrn/g-coder.git`. Look at the _License_ section and _LICENSE.md_ file for more information on how you can use this project.

## Getting Started
The `GCoder` class is a base class for writing g-code files for pen plotters. Different pen plotters require different commands to perform different tasks, such as moving the pen up and down. Because of this, you will need to modify a few class variables and a couple of functions to make it work best for your plotter.

I recommend creating a subclass of `GCoder`, which inherits all of its methods. I used the `GCoder` class to generate g-code for an EleksMaker EleksDraw plotter. The following code shows the class variables and functions that you should change to fit your plotter. This code is available in the _examples_ folder.

```python
# examples/modify_gcoder.py
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
```

It will likely take some searching and testing to determine how you need or want to modify the class. I have found https://marlinfw.org/meta/gcode/ to be very helpful in explaining g-code commands. The following code shows how the GCoder class may be used to write g-code. This code is also available in the _examples_ folder.

```python
# examples/draw_shapes.py
from gcoder import GCoder
import math

# Using the 'with' context
with GCoder("square_and_circle_1", movement_speed=25) as g:
    g.add_comment("Drawing the Square", as_header=True)
    square_pnts = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    g.draw_path(path=square_pnts, scale=10, quick_move_to_start=True, loop_to_start=True)

    g.add_space()
    g.add_comment("Drawing the Circle", as_header=True)
    circle_pnts = tuple((math.cos(i / 50 * 2 * math.pi) * 10,
                         math.sin(i / 50 * 2 * math.pi) * 10) for i in range(51))
    g.draw_path(circle_pnts, quick_move_to_start=True)
# The 'g' GCoder instance should not be used outside of this context ^

# Without the 'with' context
h = GCoder(drawing_name="square_and_circle_2")

h.add_comment("Drawing the Square", as_header=True)
h.move_to((-10, -10), quick_move=True)
h.pendown()
h.move_to((10, -10))
h.move_to((10, 10))
h.move_to((-10, 10))
h.move_to((-10, -10))
h.penup()

h.add_space()
h.add_comment("Drawing the Circle", as_header=True)
h.move_to((10, 0), quick_move=True)
h.pendown()
for i in range(51):
    ang = i / 50 * 2 * math.pi
    x, y = math.cos(ang) * 10, math.sin(ang) * 10
    h.move_to((x, y))

h.save_drawing() # The 'h' GCoder instance should not be used after this method is called
```

## Updating the Project
If you installed the project using `pip install git+https://github.com/snarrn/g-coder.git`, then you may use `pip install --upgrade git+https://github.com/snarrn/g-coder.git` to install the latest version in its place. If you installed the project with `git clone https://github.com/snarrn/g-coder.git`, then use `git pull` to get the latest version.

## Next Steps
In the future, I may add these features:
* Estimated drawing time
* A drawing visualizer, which shows the pen moving and drawing

## Contributions
This project was developed by Nathan Snarr. Generative AI was used for review of code and suggestions.

Feel free to fork the repository and make your own additions. Active collaboration may be limited on my part.

## License
The project is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0). The project's code and assets are free to use and modify with attribution given to the authors. See LICENSE.md for more details.