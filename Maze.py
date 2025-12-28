from MazeAlgorithm import *

maze = Maze("maze9.txt")

if maze.solve():
    maze.res_display()
    img = maze.res_img()
    img.save("maze_output.png")
else:
    print("No Solution")