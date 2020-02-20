import sys
from PIL import Image
import math

X_LENGTH = 10.29
Y_LENGTH = 7.55
# for scaling the difficulty function
DIFFICULTY_SCALE = 1

# from (0,0)
# x right
# y down

terrain_image = None
elevation_file = None
points = []
season = ''
output_image_path = None
seasons = ['summer', 'spring', 'fall', 'winter']

open_land = (248, 148, 18, 255)
rough_meadow = (255, 192, 0, 255)
run_forest = (255, 255, 255, 255)
slow_run_forest = (2, 208, 60, 255)
walk_forest = (2, 136, 40, 255)
impass = (5, 73, 24, 255)
water = (0, 0, 255, 255)
road = (71, 51, 3, 255)
foot_path = (0, 0, 0, 255)
out_of_bounds = (205, 0, 101, 255)

map_image = []

terrain_difficulty_dict = {
    open_land: 3,
    rough_meadow: 6,
    run_forest: 4,
    slow_run_forest: 5,
    walk_forest: 6,
    impass: 80,  # ripping through
    water: 900,  # swimming
    road: 1,
    foot_path: 2,
    out_of_bounds: -1
}


# generates a 2d array of tuples (difficulty, elevation_value) from terrain_diff_dict and elevation txt
def generate_map(terrain_image_object, elevation_file_object):
    global map_image
    raw_image = terrain_image.load()
    for y in range(0, 500):
        row = []
        elevation_row = elevation_file.readline().split()
        for x in range(0, 395):
            row.append((terrain_difficulty_dict.get(raw_image[x, y]), elevation_row[x]))
        map_image.append(row)


# helper function so i dont have to transpose
def get_pixel_difficulty(x, y):
    return map_image[y][x]


def get_heuristic_for_move(next_move, destination):
    # calculate distance of move destination from final destination
    # simple distance formula with x and y scaling
    return math.sqrt(
        (((next_move[0] - destination[0]) * X_LENGTH) ** 2) + (((next_move[1] - destination[1]) * Y_LENGTH) ** 2))


# terrain difficulty of destination + change in elevation
def get_move_difficulty(xy1, xy2):
    x1 = xy1[0]
    y1 = xy1[1]
    x2 = xy2[0]
    y2 = xy2[1]

    # bounds checking
    if x1 < 0 or x2 < 0 or y1 < 0 or y2 < 0:
        return -1
    if x1 > 394 or x2 > 394:
        return -1
    if y1 > 499 or y2 > 499:
        return -1

    diff_1 = get_pixel_difficulty(x1, y1)
    diff_2 = get_pixel_difficulty(x2, y2)
    if diff_2[0] < 0:  # out of bounds
        return -1
    else:
        elevation_1 = diff_1[1]
        elevation_2 = diff_2[1]
        # uphill hard downhill easy
        # uphill -> larger (elevation_2 - elevation_1) value = more difficult move
        return ((float(elevation_2) - float(elevation_1)) + diff_2[0]) * DIFFICULTY_SCALE


def get_cardinal_difficulty(x, y, cardinal_direction):
    if cardinal_direction == "north":
        return (x, y - 1), get_move_difficulty((x, y), (x, y - 1))
    elif cardinal_direction == "south":
        return (x, y + 1), get_move_difficulty((x, y), (x, y + 1))
    elif cardinal_direction == "east":
        return (x + 1, y), get_move_difficulty((x, y), (x + 1, y))
    elif cardinal_direction == "west":
        return (x - 1, y), get_move_difficulty((x, y), (x - 1, y))
    elif cardinal_direction == "nwest":
        return (x - 1, y - 1), get_move_difficulty((x, y), (x - 1, y - 1))
    elif cardinal_direction == "swest":
        return (x - 1, y + 1), get_move_difficulty((x, y), (x - 1, y + 1))
    elif cardinal_direction == "neast":
        return (x + 1, y - 1), get_move_difficulty((x, y), (x + 1, y - 1))
    elif cardinal_direction == "seast":
        return (x + 1, y + 1), get_move_difficulty((x, y), (x + 1, y + 1))


class Node():
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def find_optimal_path(source, destination):
    # A*
    start_node = Node(None, source)
    start_node.f = 0
    end_node = Node(None, destination)
    end_node.f = 0

    open_list = [start_node]
    closed_list = []

    while len(open_list) > 0:
        # find lowest f
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index
        open_list.pop(current_index)
        closed_list.append(current_node)

        # goal found
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        children = []
        for direction in ["north", "south", "east", "west", "nwest", "neast", "swest", "seast"]:
            coord, fval = get_cardinal_difficulty(current_node.position[0], current_node.position[1], direction)
            if fval > 0:
                new_child = Node(current_node, coord)
                new_child.f = fval + get_heuristic_for_move(coord, destination)
                children.append(new_child)

        for child in children:
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            for open_node in open_list:
                if child == open_node:
                    continue

            open_list.append(child)


def draw_path(path):
    pixels = terrain_image.load()
    for pair in path:
        pixels[pair] = (255,0,0,255)
    terrain_image.save(output_image_path)
    terrain_image.show()


def main():
    global terrain_image, elevation_file, points, season, output_image_path
    if len(sys.argv) != 6:
        print("Not enough arguments. Exiting.")
        return
    try:
        terrain_image = Image.open(sys.argv[1])
    except:
        print("Error occurred opening image file.")
    try:
        elevation_file = open(sys.argv[2])
        path_file = open(sys.argv[3])
        for line in path_file:
            points.append((int(line.split(" ")[0]), int(line.split(" ")[1].strip("\n"))))
    except:
        print("Couldnt open elevation and/or path file")
    if sys.argv[4] in seasons:
        season = sys.argv[4]
    else:
        print("Season invalid.")
    try:
        output_image_path = sys.argv[5]
    except:
        print("Failed to create output file.")

    if season == "summer":
        # get a 2d array of tuples with difficulty and elevation
        generate_map(terrain_image, elevation_file)

        for p in range(0, len(points)-1):
            draw_path(find_optimal_path(points[p], points[p+1]))

main()
