import random
import pygame
import numpy
import json
import os

class WaveFunctionCollapse:
    def __init__(self):
        with open("settings.json") as file:
            settings = json.load(file)
            self.SIZE = self.WIDTH, self.HEIGHT = settings["SIZE"]
            self.SOURCE = settings["SOURCE"]
            self.OUTPUT_RULES = settings["OUTPUT_RULES"]
            self.SPRITES_DIR = settings["SPRITES_DIR"]

        pygame.init()
        self.screen = pygame.display.set_mode(self.SIZE)
        pygame.display.set_caption("Wave Function Collapser")
    
    def load_rules(self):
        sample = numpy.loadtxt(open(self.SOURCE, "rb"), delimiter=",", skiprows=1)
        self.rules = {}

        for y, row in enumerate(sample):
            for x, element in enumerate(row):
                element = str(round(element))
                if element not in self.rules.keys():
                    self.rules[element] = [[],[],[],[]]

                # Append East block
                if (x != len(row) - 1) and (row[x+1] not in self.rules[element][0]):
                    if str(round(row[x+1])) not in self.rules[element][0]: self.rules[element][0].append(str(round(row[x+1])))

                # Append North block
                if (y != 0) and (row[y-1] not in self.rules[element][1]):
                    if str(round(sample[y-1][x])) not in self.rules[element][1]: self.rules[element][1].append(str(round(sample[y-1][x])))

                # Append West block
                if (x != 0) and (row[x-1] not in self.rules[element][2]):
                    if str(round(row[x-1])) not in self.rules[element][2]: self.rules[element][2].append(str(round(row[x-1])))

                # Append South block
                if (y != len(sample) - 1) and (row[y+1] not in self.rules[element][3]):
                    if str(round(sample[y+1][x])) not in self.rules[element][3]: self.rules[element][3].append(str(round(sample[y+1][x])))
           
    def dump_rules(self):
        with open(self.OUTPUT_RULES, "w") as file:
            json.dump(self.rules, file, indent=4)

    def generate_map(self, size):
        map_matrix = numpy.zeros((size[0], size[1], 2)).tolist()
        
        # Create entropy map
        for x, row in enumerate(map_matrix):
            for y, _ in enumerate(row):
                map_matrix[x][y][1] = [i for i in self.rules.keys()]
                map_matrix[x][y][1].sort(key=lambda x: int(x))
                random.shuffle(map_matrix[x][y][1])

        while max([max([len(x[1]) for x  in row]) for row in map_matrix]) > 1:

            min_entropy = len(self.rules)

            # get min entropy
            for y, row in enumerate(map_matrix):
                for x, (element, states) in enumerate(row):
                    if (element == 0) and (len(states) <= min_entropy) and (len(states) != 0):
                        min_entropy = len(states)
                        min_x = x
                        min_y = y

            zeros = []

            for new_state in map_matrix[min_y][min_x][1]:
                # Collapse min entropy cell
                map_matrix[min_y][min_x][0] = new_state

                # Update East block
                if (min_x < len(map_matrix[0]) - 1) and (map_matrix[min_y][min_x+1][0] == 0):
                    east_states = [state for state in map_matrix[min_y][min_x+1][1] if state in self.rules[new_state][0]]
                else:
                    east_states = [1]

                # Update North block
                if (min_y != 0) and (map_matrix[min_y-1][min_x][0] == 0):
                    north_states = [state for state in map_matrix[min_y-1][min_x][1] if state in self.rules[new_state][1]]
                else:
                    north_states = [1]

                # Update West block
                if (min_x != 0) and (map_matrix[min_y][min_x-1][0] == 0):
                    west_states = [state for state in map_matrix[min_y][min_x-1][1] if state in self.rules[new_state][2]]
                else:
                    west_states = [1]

                # Update South block
                if (min_y < len(map_matrix) - 1) and (map_matrix[min_y+1][min_x][0] == 0):
                    south_states = [state for state in map_matrix[min_y+1][min_x][1] if state in self.rules[new_state][3]]
                else:
                    south_states = [1]

                zeros.append([east_states, north_states, west_states, south_states].count(0))

            new_state = map_matrix[min_y][min_x][1][zeros.index(min(zeros))]
            map_matrix[min_y][min_x][0] = new_state
            map_matrix[min_y][min_x][1] = [new_state]

            # Update East block
            if (min_x < len(map_matrix[0]) - 1) and (map_matrix[min_y][min_x+1][0] == 0):
                map_matrix[min_y][min_x+1][1] = [state for state in map_matrix[min_y][min_x+1][1] if state in self.rules[new_state][0]]

            # Update North block
            if (min_y != 0) and (map_matrix[min_y-1][min_x][0] == 0):
                map_matrix[min_y-1][min_x][1] = [state for state in map_matrix[min_y-1][min_x][1] if state in self.rules[new_state][1]]

            # Update West block
            if (min_x != 0) and (map_matrix[min_y][min_x-1][0] == 0):
                map_matrix[min_y][min_x-1][1] = [state for state in map_matrix[min_y][min_x-1][1] if state in self.rules[new_state][2]]

            # Update South block
            if (min_y < len(map_matrix) - 1) and (map_matrix[min_y+1][min_x][0] == 0):
                map_matrix[min_y+1][min_x][1] = [state for state in map_matrix[min_y+1][min_x][1] if state in self.rules[new_state][3]]

            self.screen.fill([0, 0, 0])

            # Update canvas
            for y, row in enumerate(map_matrix):
                print([len(i[1]) for i in row])
                for x, element in enumerate(row):
                    if element[0] != 0:
                        self.screen.blit(self.sprites[element[0]], (x*100, y*100))
            
            pygame.display.flip()
            input()

        return [[element[0] for element in row] for row in map_matrix]

    def load_sprites(self):
        self.sprites = {}

        for name in ([name for name in os.listdir(self.SPRITES_DIR) if os.path.isfile(os.path.join(self.SPRITES_DIR, name))]):
            self.sprites[name.split('.')[0]] = pygame.image.load(os.path.join(self.SPRITES_DIR, name))

    def run(self):
        self.load_sprites()
        self.load_rules()
        self.dump_rules()
        self.map = self.generate_map((10, 10))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            pygame.display.flip()

if __name__ == "__main__":
    collapser = WaveFunctionCollapse()
    collapser.run()