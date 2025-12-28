from PIL import Image, ImageDraw

class Node:
    def __init__(self, state, parent, action, goal, start):
        self.state = state
        self.parent = parent
        self.action = action
        self.goal = goal
        self.start = start

class DepthFirstSearch:
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("Empty Frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class BreadthFirstSearch(DepthFirstSearch):
    def remove(self):
        if self.empty():
            raise Exception("Empty Frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

class GreedyBestFirstSearch(DepthFirstSearch):
    @staticmethod
    def manhattan_distance(node):
        goal_r, goal_c = node.goal
        state_r, state_c = node.state
        dis_r = (goal_r - state_r) if goal_r > state_r else (state_r - goal_r)
        dis_c = (goal_c - state_c) if goal_c > state_c else (state_c - goal_c)
        man_distance = dis_r + dis_c
        return man_distance

    def remove(self):
        if self.empty():
            raise Exception("Empty Frontier")
        else:
            man_distance = [self.manhattan_distance(node) for node in self.frontier]
            node = self.frontier[man_distance.index(min(man_distance))]
            self.frontier.remove(node)
            return node

class AStarSearch(GreedyBestFirstSearch):
    @staticmethod
    def path(node):
        start_path = 0
        while node.state != node.start:
            start_path += 1
            node = node.parent
        return start_path

    def remove(self):
        if self.empty():
            raise Exception("Empty Frontier")
        else:
            astar = []
            for node in self.frontier:
                man_distance = self.manhattan_distance(node)
                start_path = self.path(node)
                astar.append(man_distance + start_path)
            node = self.frontier[astar.index(min(astar))]
            self.frontier.remove(node)
            return node

class Maze:
    def __init__(self, filename):
        self.filename = filename
        self.start = None
        self.goal = None
        self.walls = []
        self.height = None
        self.width = None
        self.maze = []
        self.solution = False
        self.num_explored = 0
        self.explored_set = set()

    def maze_checker(self):
        file = open(self.filename)

        maze_layout = file.read()

        if maze_layout.count("A") == 0:
            raise Exception("No start given in the Maze")
        elif maze_layout.count("A") != 1:
            raise Exception("Multiple start positions given")
        elif maze_layout.count("B") == 0:
            raise Exception("No goal given in the Maze")
        elif maze_layout.count("B") != 1:
            raise Exception("Multiple goals given")

    def maze_read(self):
        file = open(self.filename)

        maze_len = []
        file_list = file.readlines()

        self.maze_checker()

        for line in file_list:
            sub_maze = []
            for i in line:
                if i.isspace() or i == "A" or i == "B":
                    sub_maze.append(i)
                else:
                    sub_maze.append("█")
            if "\n" in sub_maze:
                sub_maze.remove("\n")
            maze_len.append(len(sub_maze))
            self.maze.append(sub_maze)

        for sub_maze in self.maze:
            dif = max(maze_len) - len(sub_maze)
            if dif == 0:
                continue
            else:
                for i in range(dif):
                    sub_maze.append(" ")

        self.height = len(self.maze)
        self.width = len(self.maze[0])

        return self.maze

    def set_coordinates(self):
        maze = self.maze_read()
        for i in range(len(maze)):
            for j in range(len(maze[i])):
                if maze[i][j] == "A":
                    self.start = (i, j)
                elif maze[i][j] == "B":
                    self.goal = (i, j)
                elif maze[i][j] == "█":
                    self.walls.append((i, j))

    def neighbours(self, coordinates):
        row, col = coordinates
        set_neighbours = [
            ("right", (row, col + 1)),
            ("left", (row, col - 1)),
            ("up", (row - 1, col)),
            ("down", (row + 1, col))
        ]

        set_neighbours = [
            neighbour for neighbour in set_neighbours
            if 0 <= neighbour[1][0] < self.height and
               0 <= neighbour[1][1] < self.width and
               neighbour[1] not in self.walls
        ]

        return set_neighbours

    def res_display(self):
        for sub_maze in self.maze:
            sub_maze.append(" ")

        for sub_maze in self.maze:
            for ele in range(len(sub_maze)):
                if ele == len(sub_maze):
                    continue
                elif sub_maze[ele] == "█" and sub_maze[ele+1] == "█":
                    print(sub_maze[ele], end = "█")
                else:
                    print(sub_maze[ele], end = " ")
            print()
        print("States Explored: ", self.num_explored)

        for i in range(len(self.maze)):
            self.maze[i] = self.maze[i][:-1]
        return

    def res_img(self):
        img = Image.new("RGB", (len(self.maze[1])*100, len(self.maze)*100), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        for i in range(len(self.maze)):
            for j in range(len(self.maze[i])):
                l, t = j*100, i*100
                r, b = l+100, t+100
                if self.maze[i][j] == "█":
                    draw.rectangle((l, t, r, b), fill = (0, 0, 0), outline = (255, 255, 255), width = 2)
                elif self.maze[i][j] == "A":
                    draw.rectangle((l, t, r, b), fill=(255, 0, 0), outline=(255, 255, 255), width=2)
                elif self.maze[i][j] == "B":
                    draw.rectangle((l, t, r, b), fill=(0, 0, 255), outline=(255, 255, 255), width=2)
                elif self.maze[i][j] == " ":
                    draw.rectangle((l, t, r, b), fill=(230, 230, 230), outline=(255, 255, 255), width=2)
                else:
                    draw.rectangle((l, t, r, b), fill=(0, 255, 0), outline=(255, 255, 255), width=2)

        return img

    def solve(self):
        self.set_coordinates()

        frontier = AStarSearch()
        node = Node(state = self.start, parent = None, action = None, goal = self.goal, start = self.start)

        frontier.add(node)

        while True:
            if frontier.empty():
                self.solution = False
                return self.solution

            node = frontier.remove()
            #if node.state == self.start or node.state == self.goal:
            #    pass
            #else:
            #    self.maze[node.state[0]][node.state[1]] = "-"
            self.num_explored += 1

            if node.state == self.goal:
                self.solution = True

                child = node
                while True:
                    row, col = child.state

                    if child.state == self.start:
                        return self.solution
                    elif child.state == self.goal:
                        pass
                    else:
                        if child.action == "up":
                            self.maze[row][col] = "↑"
                        elif child.action == "down":
                            self.maze[row][col] = "↓"
                        elif child.action == "right":
                            self.maze[row][col] = "→"
                        elif child.action == "left":
                            self.maze[row][col] = "←"

                    child = child.parent

            self.explored_set.add(node.state)

            for coord in self.neighbours(node.state):
                if (coord[1] not in [node.state for node in frontier.frontier] and
                    coord[1] not in self.explored_set):
                    frontier.add(Node(coord[1], node, coord[0], self.goal, self.start))