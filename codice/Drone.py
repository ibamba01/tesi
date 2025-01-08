#-------------------------------------- import ----------------------------------------------------------------------
import math
import random

# -----------------------------------------inizializzazione --------------------------------------------------------
class Drone:
    def __init__(self, grid, x=0, y=0, los=2, rand=False):
        self.grid = grid  # mappa.MapGrid
        self.matrix_counter = 0
        self.my_cells = []  # celle nella zona del drone, sono aggiornate da grid.calc_zones()
        self.my_events = [] # celle che deve visitare per attivare gli eventi
        self.busy = False
        self.random_position = rand
        self.target = (0,0)  # cella target verso cui si muove il drone
        self.lineofsight = los  # imposta il campo visivo del drone
        self.balance = 0.7  # bilancia il valore della cella con la distanza dal drone
        self.path_to_target = []  # contiene il percorso verso il target
        if rand:  # posizione randomica
            lx, ly = self.grid.get_bound()
            x = random.randint(0, lx - 1)
            y = random.randint(0, ly - 1)
            if self.grid.is_wall(x, y):
                x, y = self.grid.get_neerest_free(x, y)
            self.x = x
            self.y = y
        else:  # posizione assegnata dall'utente
            if self.grid.is_wall(x, y) or not self.grid.is_within_bounds(x, y):  # se la posizione non è valida
                print(f"Posizione: {x},{y} non valida, trovo un nuova posizione vicina.", end=" ")
                x, y = self.grid.get_neerest_free(x, y)
                print(f"La nuova posizione è: {x},{y}")
            self.x = x
            self.y = y
        self.grid.add_drone(self) # aggiunge il drone alla lista dei droni sulla mappa
        self.paths = {}  # Percorsi ottimali verso le celle della zona
        self.distance_matrix = []  # Distanze minime verso le celle della zona
        self.name = "Drone"

    def __del__(self):
        if self in self.grid.dronelist:
            self.grid.remove_drone(self)

# -------------------------------------------------direction-----------------------------------------------------------
    def to_target(self):
        # Coordinate attuali
        current_x, current_y = self.get_position()
        # Coordinate del target
        target_x, target_y = self.target
        # direzione
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

    def to_target_dijkstra(self):
        # ottieni il percorso verso il target
        percorso = self.reconstruct_paths()
        # se il percorso non è vuoto
        if len(percorso) > 0:
            # prende il primo passo
            x, y = percorso[0]
            # esegue il movimento (la differenza serve perchè il drone si muove di un passo alla volta, sennò si teletrasporta)
            self.move(x - self.x, y - self.y)
        else:
            self.move(0,0)

# -------------------------------------------------------vista--------------------------------------------------------
    def drone_sight(self):
        posx, posy = self.get_position()
        if self.grid.has_event(posx, posy):
            print("vista drone chiama")
            e = self.grid.get_event(posx, posy)
            e.trigger() # l'evento drecrementa di durata, e se è finito allora
            if e.is_terminated():
                self.grid.clear_event(posx,posy,self)
                self.busy = False
            return

        for i in range(-self.lineofsight, self.lineofsight + 1):
            for j in range(-self.lineofsight, self.lineofsight + 1):
                # Controlla i limiti della griglia
                if not self.grid.is_within_bounds(posx + i, posy + j) or self.grid.has_event(posx + i, posy + j):
                    continue # ignora tutte le celle che hanno un evento (eliminerebbe l'evento)
                if i == 0 and j == 0: # evita di dover dividere per 0
                    self.grid.set_cell(posx + i, posy + j, 1.0, agente=self)
                    continue
                # Calcola la distanza euclidea
                distance = math.sqrt(i ** 2 + j ** 2)
                # Controlla se la cella è fuori dal raggio di visione
                if distance > self.lineofsight:
                    continue
                # Controlla se la linea di vista è bloccata
                blocked = self.bresenham_line_check(i, j, posx, posy)

                # Se la linea è bloccata, la cella non è visibile
                if blocked:
                    continue
                self.grid.set_cell(posx + i, posy + j, 1.0, agente=self)


    def bresenham_line_check(self, i, j, posx, posy):
        x0, y0 = posx, posy # posizione drone
        x1, y1 = posx + i, posy + j # posizione cella
        # Calcolo delle differenze
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        # Determinazione del passo in base alla direzione
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        # Inizializzazione dell'errore
        err = dx - dy
        while True:
            # Controlla se la cella è fuori dai limiti
            if not self.grid.is_within_bounds(x0, y0):
                break
            # Controlla se la cella è un muro
            if self.grid.is_wall(x0, y0):
                return True
            # Se raggiunge il punto finale, termina
            if x0 == x1 and y0 == y1:
                break
            # Aggiornamento della posizione
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        # Se non ci sono ostacoli lungo la linea, la vista è libera
        return False


# ---------------------------------------------------calcolo target-----------------------------------------------------
    # calcola quale cella massimizza il valore delle celle viste
    def calc_target(self):
        # il valore massimo che posso ottenere chiamando la funzione cell_circle_value su quella cella
        max_possibile = 0
        # tupla della cella che massimizza il valore
        mtup = (0, 0)
        # per ogni cella appartenente al drone
        for tup in self.my_cells:
            px, py = tup
            # calcola la distanza euclidea tra la cella e il drone
            dist = math.dist((self.x, self.y), (px, py))
            # calcola il valore della cella
            temp = self.grid.cell_circle_value(px, py, self)
            # calcola il valore della cella bilanciato dalla distanza
            cel_val = temp - (dist * self.balance)
            # se il valore è maggiore del massimo valore possibile
            if cel_val > max_possibile:
                max_possibile = cel_val
                mtup = tup
        # imposta come target la cella che massimizza il valore
        self.set_target(mtup[0], mtup[1])

    # calcola quale cella massimizza il valore delle celle viste in un raggio circolare che si espande progressivamente
    def calc_target_circ(self, max_radius=6):
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

    # calcola il target attraverso l'algoritmo di Dijkstra
    def calc_target_dijkstra(self):

        if not self.my_events: #lista eventi vuota
            max_possible = 0
            mtup = (0, 0)
            for tup in self.my_cells:  # per ogni cella appartenente al drone, (non sono wall o fuori dalla griglia)
                if self.grid.is_wall(tup[0], tup[1]) or not self.grid.is_within_bounds(tup[0], tup[1]):
                    continue
                px, py = tup
                temp = self.grid.cell_circle_value(px, py, self)
                cel_val = temp - (self.distance_matrix[tup] * self.balance)
                if cel_val > max_possible:
                    max_possible = cel_val
                    mtup = tup
            self.set_target(mtup[0], mtup[1])
        else:
            temp = float('inf')
            for ev in self.my_events:
                if temp > self.distance_matrix[ev]:
                    temp = self.distance_matrix[ev]
                    tup = ev
            self.set_target(tup[0],tup[1])

# -----------------------------------------------dijkstra ausiliario---------------------------------------------------
    def reconstruct_paths(self):
        predecessor = self.paths
        current_target = self.target
        path = []
        while current_target != (self.x, self.y):
            path.append(current_target)
            if current_target not in predecessor:
                raise ValueError(f"Cella {current_target} non trovata nei predecessori. Percorso non valido.")
            current_target = predecessor.get(current_target, None)
        self.path_to_target = path[::-1] # Inverti il percorso
        return path[::-1]

#---------------------------------------------set fun-----------------------------------------------------------------
    def add_cell(self, cell):
        self.my_cells.append(cell)

    def add_event(self, cell):
        self.my_events.append(cell)

    def remove_event(self):
        self.my_events.clear()

    def set_percorsi(self, percorsi):
        self.paths = percorsi

    def set_target(self, x, y):
        if self.grid.is_within_bounds(x, y):
            self.target = (x, y)
        else:
            print("Target non valido: fuori dai limiti della griglia.")

#-------------------------------------------clear memory--------------------------------------------------------------
    def clear_cell(self):
        self.my_cells.clear()

    def clear_paths(self):
        self.paths.clear()

    def clear_distance_matrix(self):
        self.distance_matrix = {}

    def clear_path_to_target(self):
        self.path_to_target.clear()

#----------------------------------------------check fun---------------------------------------------------------------
    def is_my_cell(self, x, y):
        return (x, y) in self.my_cells

    def is_busy(self):
        return self.busy
#----------------------------------------------get fun----------------------------------------------------------------
    def get_position(self):
        # Restituisce la posizione attuale del drone
        return self.x, self.y

#----------------------------------------------movement---------------------------------------------------------------
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

    def move(self, x=0, y=0):
        if self.grid.is_within_bounds(self.x + x, self.y + y) and not self.grid.is_wall(self.x + x, self.y + y):
            self.y += y
            self.x += x
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")
        if self.grid.has_event(self.x, self.y):
            e = self.grid.get_event(self.x, self.y)
            e.activate()
            self.busy = True