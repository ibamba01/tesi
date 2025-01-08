import random


class Generator:
    def __init__(self, grid, rn=300,
                 min_room_size=4, max_room_size=12):
        self.grid = grid
        self.width = self.grid.shape[0]
        self.height = self.grid.shape[1]
        self.room_number = rn
        self.min_room_size = min_room_size
        self.max_room_size = max_room_size
        self.check_room_size()
        self.level = [['stone' for _ in range(self.width)] for _ in range(self.height)]
        self.rooms = []
        # Lista dei muri disponibili per nuove stanze
        self.wall_positions = []
        self.generate_structure()
        self.generate_rooms()
        self.add_doors()

    def check_room_size(self):
        if self.min_room_size < 4:
            raise ValueError('La dimensione minima della stanza deve essere almeno 4.')
        if self.min_room_size > self.max_room_size:
            raise ValueError('La dimensione minima della stanza deve essere minore della dimensione massima.')

    def generate_structure(self):
        for i in range(self.height):
            for j in range(self.width):
                if i == 0 or i == self.height - 1 or j == 0 or j == self.width - 1:
                    self.level[i][j] = 'wall'
                else:
                    self.level[i][j] = 'floor'

        # Aggiungi i muri iniziali alla lista
        for i in range(self.height):
            for j in range(self.width):
                if self.level[i][j] == 'wall':
                    self.wall_positions.append((i, j))

    def add_room(self, x, y, width, height):
        """Aggiunge una stanza adiacente a un muro esistente."""
        if (x + width >= self.width or y + height >= self.height or
            x <= 0 or y <= 0):
            raise ValueError('La stanza non può superare i confini della struttura.')
        for i in range(y, y + height):
            for j in range(x, x + width):
                if (i == y or i == y + height - 1 or
                    j == x or j == x + width - 1):
                    self.level[i][j] = 'wall'
                    if (i, j) not in self.wall_positions:
                        self.wall_positions.append((i, j))
                else:
                    self.level[i][j] = 'floor'
        # Rimuovi i muri interni alla stanza dalla lista
        self.wall_positions = [
            pos for pos in self.wall_positions
            if self.level[pos[0]][pos[1]] == 'wall']
        self.rooms.append({'x': x, 'y': y, 'width': width, 'height': height})

    def generate_rooms(self):
        for _ in range(self.room_number):
            if not self.wall_positions:
                break  # Nessun muro disponibile per attaccare altre stanze

            # Seleziona un muro casuale
            wall_x, wall_y = random.choice(self.wall_positions)

            # Calcola dimensioni casuali della stanza
            room_width = random.randint(self.min_room_size, self.max_room_size)
            room_height = random.randint(self.min_room_size, self.max_room_size)

            # Determina la posizione della stanza rispetto al muro
            direction = random.choice(['up', 'down', 'left', 'right'])
            if direction == 'up':
                x = wall_y - room_width // 2
                y = wall_x - room_height
            elif direction == 'down':
                x = wall_y - room_width // 2
                y = wall_x + 1
            elif direction == 'left':
                x = wall_y - room_width
                y = wall_x - room_height // 2
            elif direction == 'right':
                x = wall_y + 1
                y = wall_x - room_height // 2

            # Tenta di aggiungere la stanza
            try:
                self.add_room(x, y, room_width, room_height)
            except ValueError:
                continue  # Prova con un altro muro

    def check_doors(self,x,y):
        for i in range(-1, 1):
            for j in range(-1, 1):
                if self.level[x + i][y + j] == 'door':
                    return True
        return False

    def add_doors(self):
        """Aggiunge porte tra muri condivisi di stanze adiacenti."""
        for i in range(1, self.height - 1):
            for j in range(1, self.width - 1):
                if self.level[i][j] == 'wall':
                    #if self.check_doors(i,j):
                     #   continue
                    wall_dir = {}
                    adjacent_walls = 0
                    if self.level[i - 1][j] == 'wall':
                        adjacent_walls += 1
                        wall_dir.update({'a': (i - 1, j)})
                    if self.level[i + 1][j] == 'wall':
                        adjacent_walls += 1
                        wall_dir.update({'b': (i + 1, j)})
                    if self.level[i][j - 1] == 'wall':
                        adjacent_walls += 1
                        wall_dir.update({'c': (i, j - 1)})
                    if self.level[i][j + 1] == 'wall':
                        adjacent_walls += 1
                        wall_dir.update({'d': (i, j + 1)})
                    if adjacent_walls >= 3:
                        self.level[i][j] = 'door'
                        #a,b = wall_dir[ random.choice( list( wall_dir.keys() ) ) ]
                        #self.level[a][b] = 'door'

    def update_matrix(self):
        wallsssssss= 0
        for i, row in enumerate(self.level):  # i è l'indice della riga
            for j, tile in enumerate(row):  # j è l'indice della colonna
                # Logica per determinare cosa impostare in other_matrix
                if tile == 'stone':
                    self.grid[i][j] = ('WALL', None)
                    wallsssssss += 1
                elif tile == 'wall':
                    self.grid[i][j] = ('WALL', None)
                    wallsssssss += 1
                elif tile == 'door':
                    self.grid[i][j] = (0, None)
                elif tile == 'floor':
                    self.grid[i][j] = (0, None)
        return self.grid, wallsssssss