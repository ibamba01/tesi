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
            x = random.randint(0, lx - 1)
            y = random.randint(0, ly - 1)
            if self.grid.is_wall(x, y):
                x, y = self.grid.neerest_free(x, y)
            self.x = x
            self.y = y
        else: # posizione assegnata dall'utente
            if self.grid.is_wall(x, y) or not self.grid.is_within_bounds(x, y): # se la posizione non è valida
                print("Posizione non valida, trovo un nuova posizione vicina.")
                x, y = self.grid.neerest_free(x, y)
                print(f"La nuova posizione è: {x},{y}")
            self.x = x
            self.y = y
        # aggiunge il drone alla lista dei droni sulla mappa
        self.grid.add_drone(self)

    def __del__(self):
        if self in self.grid.dronelist:
            self.grid.remove_drone(self)

#----------------------------------------gestione zone------------------------------------------------------------------
    def add_cell(self, cell):
        self.my_cells.append(cell)

    def clear_cell(self):
        self.my_cells.clear()

    def is_my_cell(self, x, y):
        return (x, y) in self.my_cells
#----------------------------------------get fun------------------------------------------------------------------------
    def get_position(self):
        # Restituisce la posizione attuale del drone
        return self.x, self.y

#----------------------------------------set fun------------------------------------------------------------------------
    def set_target(self, x, y):
        if self.grid.is_within_bounds(x, y):
            self.target = (x, y)
        else:
            print("Target non valido: fuori dai limiti della griglia.")

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
        if self.grid.is_within_bounds(self.x, self.y + y) and not self.grid.is_wall(self.x, self.y + y):
            self.y += y
        if self.grid.is_within_bounds(self.x + x, self.y) and not self.grid.is_wall(self.x + x, self.y) :
            self.x += x
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")
        #print(f"La posizione attuale è:",self.get_position())

    def to_target(self):
        current_x, current_y = self.get_position()
        # Coordinate del target
        target_x, target_y = self.target

        move_x, move_y = 0, 0

        # determina il movimento lungo l'asse x
        if current_x < target_x:
            move_x = 1
        elif current_x > target_x:
            move_x = -1

        # determina il movimento lungo l'asse y
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
                if i == 0 and j == 0:
                    self.grid.set_cell(posx + i, posy + j, 1.0, agente=self)
                    continue
                # Controlla i limiti della griglia
                if not self.grid.is_within_bounds(posx + i, posy + j):
                    continue
                # Calcola la distanza euclidea
                distance = math.sqrt(i ** 2 + j ** 2)
                # Controlla se la cella è fuori dal raggio di visione
                if distance > self.lineofsight:
                    continue
                # Calcola il passo incrementale lungo la direzione
                step_x, step_y = i / distance, j / distance
                steps = int(distance)

                # Verifica ogni cella lungo la linea di vista
                x, y = posx, posy
                blocked = False
                for _ in range(steps):
                    x += step_x
                    y += step_y
                    cell_x, cell_y = round(x), round(y)

                    if not self.grid.is_within_bounds(cell_x, cell_y):
                        break
                    if self.grid.is_wall(cell_x, cell_y):
                        blocked = True
                        break

                # Se la linea non è bloccata, imposta la cella come visibile
                if not blocked:
                    self.grid.set_cell(posx + i, posy + j, 1.0, agente=self)

    # calcola quale cella massimizza il valore delle celle viste
    def calc_target(self):
        # il valore massimo che posso ottenere chiamando la funzione cell_circle_value su quella cella
        max_possibile = 0
        # tupla della cella che massimizza il valore
        mtup = (0,0)
        # per ogni cella appartenente al drone
        for tup in self.my_cells:
            px, py = tup
            temp = self.grid.cell_circle_value(px, py, self)
            if temp > max_possibile:
                max_possibile = temp
                mtup = tup
        # imposta come target la cella che massimizza il valore
        self.set_target(mtup[0], mtup[1])


    def calc_target_circ(self, max_radius=6):
        """
        Calcola il bersaglio del drone esplorando in modo progressivo anelli circolari concentrici
        intorno alla posizione attuale del drone.
        """
        posdx, posdy = self.get_position()
        max_possibile = 0
        mtup = (posdx, posdy)

        # Esplora progressivamente anelli concentrici
        for r in range(1, max_radius + 1):
            # itera su tutte le celle nell'anello
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    # controlla se la cella è sulla circonferenza dell'anello
                    if abs(dx) != r and abs(dy) != r:
                        continue
                    nx, ny = posdx + dx, posdy + dy

                    if self.is_my_cell(nx, ny) and self.grid.is_within_bounds(nx, ny) and not self.grid.is_wall(nx, ny):
                        temp = self.grid.cell_circle_value(nx, ny, self)

                        if temp > max_possibile:
                            max_possibile = temp
                            mtup = (nx, ny)

        self.set_target(mtup[0], mtup[1])