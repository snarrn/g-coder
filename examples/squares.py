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
