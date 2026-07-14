# Draw Shapes
"""
Showcases different ways to draw the same set of shapes with GCoder.
"""
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
