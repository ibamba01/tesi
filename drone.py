import math
import random



class Drone:
# -------------------------------------------- class fun----------------------------------------------------------------
    def __init__(self, grid, x=0, y=0 ,los=2, rand=False):
        # imposta la mappa
        self.grid = grid # mappa.MapGrid
        self.my_cells = [] # celle nella zona del drone, sono aggiornate da grid.calc_zones()
        self.target = (0,0) # cella target verso cui si muove il drone
        self.lineofsight = los # imposta il campo visivo del drone
        # dove viene generato il drone
        if rand: # posizione randomica
            lx,ly = self.grid.get_bound()
            self.x = random.randint(0, lx - 1)
            self.y = random.randint(0, ly - 1)
        elif self.grid.is_within_bounds(x, y): # posizione assegnata dall'utente
            self.x = x
            self.y = y
        else: # posizione non valida
            if not self.grid.is_occupied(0, 0):
                self.x = 0
                self.y = 0
                raise ValueError("Posizione iniziale fuori dai limiti della griglia, inizializzato a 0,0")
            else:
                raise ValueError("Posizione iniziale fuori dai limiti della griglia, e origine occupata")
        # aggiunge il drone alla lista dei droni sulla mappa
        self.grid.add_drone(self)

    def __del__(self):
        if self in self.grid.dronelist:
            self.grid.remove_drone(self)

#----------------------------------------gestione zone------------------------------------------------------------------------
    def add_cell(self, cell):
        self.my_cells.append(cell)

    def clear_dronelist(self):
        self.my_cells.clear()

#----------------------------------------get fun------------------------------------------------------------------------
    def get_position(self):
        # Restituisce la posizione attuale del drone
        return self.x, self.y

#-------------------------------------- movement------------------------------------------------------------------------
    def move_up(self):
        if self.grid.is_within_bounds(self.x - 1, self.y):
            self.x -= 1
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")
    def move_down(self):
        if self.grid.is_within_bounds(self.x + 1, self.y):
            self.x += 1
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")

    def move_left(self):
        if self.grid.is_within_bounds(self.x, self.y - 1):
            self.y -= 1
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")

    def move_right(self):
        if self.grid.is_within_bounds(self.x, self.y + 1):
            self.y += 1
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")

    def teleport(self, x, y):
        if self.grid.is_within_bounds(x, y):
            self.y = y
            self.x = x
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")

    def move_random(self):
        x = random.randint(-1,1)
        y = random.randint(-1,1)
        if self.grid.is_within_bounds(self.x, self.y + y):
            self.y += y
        if self.grid.is_within_bounds(self.x + x, self.y):
            self.x += x
        #print(f"La posizione attuale è:",self.get_position())

    def move(self, x=0, y=0):
        if self.grid.is_within_bounds(self.x, self.y + y):
            self.y += y
        if self.grid.is_within_bounds(self.x + x, self.y):
            self.x += x
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")
        #print(f"La posizione attuale è:",self.get_position())

    def to_target(self):
        # Posizione attuale del drone
        current_x, current_y = self.get_position()
        # Coordinate del target
        target_x, target_y = self.target

        # Calcola la direzione del movimento
        move_x, move_y = 0, 0

        # Determina il movimento lungo l'asse x
        if current_x < target_x:
            move_x = 1
        elif current_x > target_x:
            move_x = -1
        # Determina il movimento lungo l'asse y
        if current_y < target_y:
            move_y = 1
        elif current_y > target_y:
            move_y = -1
        # Esegue il movimento
        self.move(move_x, move_y)

# --------------------------------------- logic ------------------------------------------------------------------------
    def vista_drone(self):
        posx, posy = self.get_position()
        for i in range(-self.lineofsight, self.lineofsight + 1):
            for j in range(-self.lineofsight, self.lineofsight + 1):
                # solo se la cella è dentro i limiti della griglia
                if  self.grid.is_within_bounds(posx + i, posy + j):
                    # calcola la distanza euclidea
                    distance = math.sqrt(i ** 2 + j ** 2)
                    if distance <= self.lineofsight: # se la cella è dentro il raggio di lineofsight
                        self.grid.set_cell(posx + i, posy + j, 1.0) # Imposta 1 per le celle visibili

    # calcola quale cella massimizza il valore delle celle viste
    def calc_target(self):
        max_possible = 0
        mtup = (0,0)
        #n = len(self.my_cells)
        #for i in range(30):
         #   px, py = self.my_cells[random.randint(0, n-1)]
          #  temp = self.grid.cell_circle_value(px, py, self)
           # if temp > max_possible:
            #    max_possible = temp
             #   mtup = (px, py)
        for tup in self.my_cells: # posso migliorarlo
            px, py = tup
            temp = self.grid.cell_circle_value(px, py, self)
            if temp > max_possible:
                max_possible = temp
                mtup = tup
        # aggiunge la cella che massimizza come target
        self.set_target(mtup[0], mtup[1])

    def set_target(self, x, y):
        if self.grid.is_within_bounds(x, y):
            self.target = (x, y)
        else:
            print("Target non valido: fuori dai limiti della griglia.")