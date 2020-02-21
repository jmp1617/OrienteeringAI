import sys
from PIL import Image
import math

X_LENGTH = 10.29
Y_LENGTH = 7.55
# for scaling the TERRAIN difficulty function
# higher the scale, harder the terrain features
DIFFICULTY_SCALE = 5

# from (0,0)
# x right
# y down

terrain_image = None
elevation_file = None
elevation_file_path = ''
points = []
season = ''
output_image_path = None
seasons = ['summer', 'spring', 'fall', 'winter']

open_land = (248, 148, 18, 255)
rough_meadow = (255, 192, 0, 255)
run_forest = (255, 255, 255, 255)
new_run_forest = (255, 255, 255, 100)
slow_run_forest = (2, 208, 60, 255)
walk_forest = (2, 136, 40, 255)
impass = (5, 73, 24, 255)
water = (0, 0, 255, 255)
swamp = (150, 75, 0, 255)
new_water = (0, 0, 255, 100)
road = (71, 51, 3, 255)
foot_path = (0, 0, 0, 255)
out_of_bounds = (205, 0, 101, 255)

map_image = []

terrain_difficulty_dict = {
    open_land: 3,
    rough_meadow: 6,
    run_forest: 4,
    new_run_forest: 4,
    slow_run_forest: 5,
    walk_forest: 6,
    impass: 80,  # ripping through
    new_water: 4,  # ice
    water: 900,  # swimming
    swamp: 8,
    road: 0.01,
    foot_path: 0.0001,
    out_of_bounds: -1
}


def winter_transform(raw_image):
    border_water = []
    for x in range(1, 394):
        for y in range(1, 499):
            # find the border of waters
            if raw_image[x, y] == water:
                if raw_image[x + 1, y] != water or \
                        raw_image[x - 1, y] != water or \
                        raw_image[x, y + 1] != water or \
                        raw_image[x, y - 1] != water:
                    border_water.append((x, y))
    ice = set()
    for pixel in border_water:
        depth = 0
        # get neighbors
        neighbors = [(pixel[0], pixel[1], depth)]
        local_ice = set()
        while len(neighbors) > 0:
            current = neighbors.pop()
            currentx = current[0]
            currenty = current[1]
            # Freeze
            ice.add((currentx, currenty))
            local_ice.add((currentx, currenty))
            if current[2] < 7:
                if currentx + 1 < 395:
                    if raw_image[currentx + 1, currenty] == water:
                        if (currentx + 1, currenty) not in local_ice:
                            neighbors.append((currentx + 1, currenty, current[2] + 1))
                if currentx - 1 > 0:
                    if raw_image[currentx - 1, currenty] == water:
                        if (currentx - 1, currenty) not in local_ice:
                            neighbors.append((currentx - 1, currenty, current[2] + 1))
                if currenty + 1 < 500:
                    if raw_image[currentx, currenty + 1] == water:
                        if (currentx, currenty + 1) not in local_ice:
                            neighbors.append((currentx, currenty + 1, current[2] + 1))
                if currenty - 1 > 0:
                    if raw_image[currentx, currenty - 1] == water:
                        if (currentx, currenty - 1) not in local_ice:
                            neighbors.append((currentx, currenty - 1, current[2] + 1))
                if currentx - 1 > 0 and currenty - 1 > 0:
                    if raw_image[currentx - 1, currenty - 1] == water:
                        if (currentx - 1, currenty - 1) not in local_ice:
                            neighbors.append((currentx - 1, currenty - 1, current[2] + 1))
                if currentx - 1 > 0 and currenty + 1 < 500:
                    if raw_image[currentx - 1, currenty + 1] == water:
                        if (currentx - 1, currenty + 1) not in local_ice:
                            neighbors.append((currentx - 1, currenty + 1, current[2] + 1))
                if currentx + 1 < 395 and currenty - 1 > 0:
                    if raw_image[currentx + 1, currenty - 1] == water:
                        if (currentx + 1, currenty - 1) not in local_ice:
                            neighbors.append((currentx + 1, currenty - 1, current[2] + 1))
                if currentx + 1 < 395 and currenty + 1 < 500:
                    if raw_image[currentx + 1, currenty + 1] == water:
                        if (currentx + 1, currenty + 1) not in local_ice:
                            neighbors.append((currentx + 1, currenty + 1, current[2] + 1))
    for coord in ice:
        raw_image[coord[0], coord[1]] = new_water
    print("Winter map generated.")


def spring_transform(raw_image):
    border_water = []
    for x in range(1, 394):
        for y in range(1, 499):
            # find the border of waters
            if raw_image[x, y] == water:
                if raw_image[x + 1, y] != water or \
                        raw_image[x - 1, y] != water or \
                        raw_image[x, y + 1] != water or \
                        raw_image[x, y - 1] != water:
                    border_water.append((x, y))

    elevation_map = [[]]
    for y in range(0, 500):
        elevation_map.append(elevation_file.readline().split())

    swamp_set = set()
    for pixel in border_water:
        depth = 0
        base_elevation = elevation_map[pixel[1]][pixel[0]]
        # get neighbors
        neighbors = [(pixel[0], pixel[1], base_elevation, depth)]
        local_swamp = set()
        while len(neighbors) > 0:
            current = neighbors.pop()
            currentx = current[0]
            currenty = current[1]
            # Freeze
            swamp_set.add((currentx, currenty))
            local_swamp.add((currentx, currenty))
            if float(current[2]) < 1 + float(base_elevation) and current[3] < 15:
                if currentx + 1 < 395:
                    if raw_image[currentx + 1, currenty] != water:
                        if (currentx + 1, currenty) not in local_swamp:
                            neighbors.append(
                                (currentx + 1, currenty, elevation_map[currenty][currentx + 1], current[3] + 1))
                if currentx - 1 > 0:
                    if raw_image[currentx - 1, currenty] != water:
                        if (currentx - 1, currenty) not in local_swamp:
                            neighbors.append(
                                (currentx - 1, currenty, elevation_map[currenty][currentx - 1], current[3] + 1))
                if currenty + 1 < 500:
                    if raw_image[currentx, currenty + 1] != water:
                        if (currentx, currenty + 1) not in local_swamp:
                            neighbors.append(
                                (currentx, currenty + 1, elevation_map[currenty + 1][currentx], current[3] + 1))
                if currenty - 1 > 0:
                    if raw_image[currentx, currenty - 1] != water:
                        if (currentx, currenty - 1) not in local_swamp:
                            neighbors.append(
                                (currentx, currenty - 1, elevation_map[currenty - 1][currentx], current[3] + 1))
                if currentx - 1 > 0 and currenty - 1 > 0:
                    if raw_image[currentx - 1, currenty - 1] != water:
                        if (currentx - 1, currenty - 1) not in local_swamp:
                            neighbors.append(
                                (currentx - 1, currenty - 1, elevation_map[currenty - 1][currentx - 1], current[3] + 1))
                if currentx - 1 > 0 and currenty + 1 < 500:
                    if raw_image[currentx - 1, currenty + 1] != water:
                        if (currentx - 1, currenty + 1) not in local_swamp:
                            neighbors.append(
                                (currentx - 1, currenty + 1, elevation_map[currenty + 1][currentx - 1], current[3] + 1))
                if currentx + 1 < 395 and currenty - 1 > 0:
                    if raw_image[currentx + 1, currenty - 1] != water:
                        if (currentx + 1, currenty - 1) not in local_swamp:
                            neighbors.append(
                                (currentx + 1, currenty - 1, elevation_map[currenty - 1][currentx + 1], current[3] + 1))
                if currentx + 1 < 395 and currenty + 1 < 500:
                    if raw_image[currentx + 1, currenty + 1] != water:
                        if (currentx + 1, currenty + 1) not in local_swamp:
                            neighbors.append(
                                (currentx + 1, currenty + 1, elevation_map[currenty + 1][currentx + 1], current[3] + 1))
    for coord in swamp_set:
        if raw_image[coord[0], coord[1]] != water:
            raw_image[coord[0], coord[1]] = swamp
    print("Spring map generated.")


def fall_transform(raw_image):
    for x in range(1, 394):
        for y in range(1, 499):
            if raw_image[x, y] == foot_path:
                if raw_image[x + 1, y] == run_forest or \
                        raw_image[x - 1, y] == run_forest or \
                        raw_image[x, y + 1] == run_forest or \
                        raw_image[x, y - 1] == run_forest:
                    raw_image[x, y] = new_run_forest
    print("Fall map generated.")


# generates a 2d array of tuples (difficulty, elevation_value) from terrain_diff_dict and elevation txt
def generate_map():
    global map_image, elevation_filef
    raw_image = terrain_image.load()
    if season == "fall":
        fall_transform(raw_image)
    if season == "winter":
        winter_transform(raw_image)
    if season == "spring":
        spring_transform(raw_image)
    elevation_file = open(elevation_file_path)
    for y in range(0, 500):
        row = []
        elevation_row = elevation_file.readline().split()
        for x in range(0, 395):
            row.append((terrain_difficulty_dict.get(raw_image[x, y]), elevation_row[x]))
        map_image.append(row)


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
        return None
    if x1 > 394 or x2 > 394:
        return None
    if y1 > 499 or y2 > 499:
        return None

    diff_1 = get_pixel_difficulty(x1, y1)
    diff_2 = get_pixel_difficulty(x2, y2)
    if diff_2[0] < 0:  # out of bounds
        return None
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
        self.g = 0

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
            coord, gval = get_cardinal_difficulty(current_node.position[0], current_node.position[1], direction)
            if gval is not None:
                new_child = Node(current_node, coord)
                new_child.g = gval
                new_child.f = gval + get_heuristic_for_move(coord, destination)
                children.append(new_child)

        for child in children:
            if child in closed_list:
                continue

            if child in open_list:
                for node in open_list:
                    if node.position == child.position:
                        if child.g > node.g:
                            continue

            open_list.append(child)


def draw_path(path):
    pixels = terrain_image.load()
    for pair in path:
        pixels[pair] = (255, 0, 0, 255)
    terrain_image.save(output_image_path)


def path_length(path):
    return len(path) * X_LENGTH + len(path) * Y_LENGTH


def main():
    global terrain_image, elevation_file, points, season, output_image_path, elevation_file_path
    if len(sys.argv) != 6:
        print("Not enough arguments. Exiting.")
        return
    try:
        terrain_image = Image.open(sys.argv[1])
    except:
        print("Error occurred opening image file.")
    try:
        elevation_file = open(sys.argv[2])
        elevation_file_path = sys.argv[2]
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

    # get a 2d array of tuples with difficulty and elevation
    generate_map()

    total = 0
    for p in range(0, len(points) - 1):
        path = find_optimal_path(points[p], points[p + 1])
        draw_path(path)
        length = path_length(path)
        print("Path found from " + str(points[p]) + " to " + str(points[p + 1]) + " lenght " + str(length))
        total += length
    print("Total path length: " + str(total) + "m \nNew Image file created.")


main()
