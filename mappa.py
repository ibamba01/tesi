import numpy as np
import random
import math
import heapq

class MapGrid:
    def __init__(self, righe, colonne, valore_iniziale=0.0, agente_iniziale=None, rando=False, has_wall=False, rando_wall=False, perdita=0.98, wall_density=0.1):
        self.perdita = perdita
        self.has_wall = has_wall
        self.grid = np.empty((righe, colonne), dtype=object)
        # Crea una griglia di dimensioni (rows x cols) con valore iniziale specificato
        if rando:
            # itera su tutte le celle
            for i in range(righe):
                for j in range(colonne):
                    # assegna a ogni cella un valore casuale, e l'agente iniziale
                    valore_casuale = round(random.uniform(0, 1), 2)  # Valore casuale tra 0 e 1, arrotondato a 2 decimali
                    self.grid[i, j] = (valore_casuale, agente_iniziale)
        else:
            for i in range(righe):
                for j in range(colonne):
                    self.grid[i, j] = (valore_iniziale, agente_iniziale)
        self.dronelist = [] # mantengo una lista di tutte le istanze dei droni vivi
        self.num_walls = 0
        self.wall_density = 0
        if has_wall:
            if rando_wall:
                self.wall_density = wall_density
                # Posiziona pareti casuali
                self.num_walls = int(wall_density * righe * colonne)  # il 10% delle celle sono pareti
                for ii in range(self.num_walls):
                    x = random.randint(0, righe - 1)
                    y = random.randint(0, colonne - 1)
                    self.grid[x, y] = ('WALL', None)
            else:
                # Posiziona pareti predefinite (esempio: contorno della griglia)
                for i in range(righe):
                    self.grid[i, 0] = ('WALL', None)  # Bordo sinistro
                    self.grid[i, colonne - 1] = ('WALL', None)  # Bordo destro
                    self.num_walls += 2
                    self.grid[i, colonne // 2] = ('WALL', None)
                for j in range(colonne):
                    self.grid[0, j] = ('WALL', None)  # Bordo superiore
                    self.grid[righe - 1, j] = ('WALL', None)  # Bordo inferiore
                    self.num_walls += 2

    def start(self, choise):
        if choise == 0:
            self.start_with_voronoi()
        elif choise == 1:
            self.start_with_dijkstra()
        else:
            raise ValueError("utilizzare 0 per Voronoi o 1 per Dijkstra")

    # fa partire la logica dei droni
    def start_with_voronoi(self):
        # perdita di pacchetti per turno
        self.knloss()
        # partizione di Voronoi
        self.partizione()
        # per ogni drone calcola il target e si sposta
        for dd in self.dronelist:
            dd.calc_target()
            dd.to_target()
            dd.vista_drone()  # imposta a 1 le celle viste dal drone

    def start_with_dijkstra(self):
        self.knloss()
        # partizione delle celle attraverso la vicinaza secondo Dijkstra
        self.partizione_dijkstra()
        for drone in self.dronelist:
            # utilizza la distanza di Dijkstra per calcolare il percorso
            drone.calc_target_dijkstra()
            drone.to_target_dijkstra()
            drone.clear_distanze()
            drone.clear_percorsi()
            drone.vista_drone()

# ----------------------------------------gestione droni----------------------------------------------------------------
    def add_drone(self, drone):
        # Aggiunge un drone alla lista condivisa
        self.dronelist.append(drone)

    def remove_drone(self, drone):
        # rimuove un drone dalla lista
        self.dronelist.remove(drone)

    def display_dronelist(self):
        print("Lista dei droni sulla mappa:")
        for i, drone in enumerate(self.dronelist, start=1):
            x, y = drone.get_position()
            print(f"Drone {i}: posizione ({x}, {y}), line-of-sight {drone.lineofsight}")

    def clear_dronelist(self):
        self.dronelist.clear()
        print("Tutti i droni sono stati rimossi dalla mappa.")

    def dronelist_clear_cells(self):
        for dd in self.dronelist:
            dd.clear_cell()

    def dronelist_clear_percorsi(self):
        for dd in self.dronelist:
            dd.clear_percorsi()

    def dronelist_clear_path(self):
        for dd in self.dronelist:
            dd.clear_path()

    # rimuove tutte le distanze assegnate ai droni
    def dronelist_clear_distanze(self):
        for dd in self.dronelist:
            dd.clear_distanze()

    def dronelist_set(self):
        agentlist = list(set(dd for dd in self.dronelist))
        return agentlist

# ----------------------------------------set fun-----------------------------------------------------------------------
    def set_cell(self, row, col, value=None, agente=None):
        # controllo se la cella da modificare è valida
        if self.is_within_bounds(row, col):
            # se non è stato passato un valore
            if value is None:
                # imposto come valore da assegnare il valore corrente
                value = self.grid[row, col][0]
            if agente is None:
                agente = self.grid[row, col][1]
            # imposto il nuovo valore, possessore della cella
            self.grid[row, col] = (value, agente)
        else:
            print("Errore: le coordinate sono fuori dai limiti della griglia.")

# ----------------------------------------get fun-----------------------------------------------------------------------
    def get_value_grid(self):
        # Inizializza una nuova griglia con valori zero (o un altro valore predefinito)
        grid_values = np.zeros((self.grid.shape[0], self.grid.shape[1]))
        # Scorri ogni cella della griglia
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                grid_values[i, j] = self.get_value(i,j)  # Estrai il valore dalla tupla (valore, agente) e lo imposta nella nuova matrice
        return grid_values

    def get_agent_grid(self):
        grid_agents = np.empty((self.grid.shape[0], self.grid.shape[1],), dtype=object)
        # Scorri ogni cella della griglia
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                grid_agents[i, j] = self.get_agent(i, j)  # Estrai il valore dalla tupla (valore, agente) e lo imposta nella nuova matrice
        return grid_agents

    def get_cell(self, row, col):
        # Ottiene il valore di una cella specifica
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            return self.grid[row, col]
        else:
            print("Errore: le coordinate sono fuori dai limiti della griglia.")
            return None

    def get_value(self, row, col):
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            value = self.grid[row, col][0] # 0 indica il primo elemento (value)
            return value
        else:
            print("Errore: le coordinate sono fuori dai limiti della griglia.")
            return None

    def get_agent(self, row, col):
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            agent = self.grid[row, col][1] # 1 indica il secondo elemento (agent)
            return agent
        else:
            print("Errore: le coordinate sono fuori dai limiti della griglia.")
            return None

    def get_bound(self):
        return self.grid.shape[0], self.grid.shape[1]

    def get_map(self):
        return self.grid

# ----------------------------------------check fun---------------------------------------------------------------------
    def is_within_bounds(self, x, y):
        # Verifica se (x, y) è all'interno dei limiti della griglia
        return 0 <= x < self.grid.shape[0] and 0 <= y < self.grid.shape[1]

    def is_occupied(self, x, y):
        occ = False
        for dd in self.dronelist:
            pdx, pdy = dd.get_position()
            if x == pdx and y == pdy:
                occ = True
        return occ

    def is_wall(self, x, y):
        if self.get_value(x, y) == 'WALL':
            return True
        return False
# ----------------------------------------print fun---------------------------------------------------------------------
    def display(self):
        # Stampa la griglia
        print("\n",self.grid,"\n")

    def map_knoledge(self):
        tot = 0
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                temp = self.get_value(i, j)
                if temp == 'WALL':
                    temp = 0 # le pareti non contano
                tot += temp
        return tot / ((self.grid.shape[0] * self.grid.shape[1]) - self.num_walls) # tolgo le pareti dal conteggio


# ----------------------------------------logic fun---------------------------------------------------------------------
    def dimenticanza(self, value):
        return value * self.perdita

    def knloss(self): # aggiornato per le pareti
        # Applica la perdita di conoscenza solo ai valori numerici
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                value, agent = self.grid[i, j]  # Ottieni la tupla (valore, agente)
                if value != 'WALL':
                    # Applica la perdita al valore e ricrea la tupla
                    self.grid[i, j] = (self.dimenticanza(value), agent)

    # data una posizione e un raggio, calcola il la differenza totale del valore delle celle vicine se fossero settate a 1
    def cell_circle_value(self, posx, posy, drone): # aggiornato per le pareti
        valore_possibile = 0.0
        raggio = drone.lineofsight
        # deve calcolare il valore totale delle celle vicine alla posizione passata in un raggio circolare
        # Itera attraverso le celle circostanti, considerando il raggio
        for i in range(-raggio, raggio + 1):
            for j in range(-raggio, raggio + 1):
                # Calcola la posizione della cella vicina
                nx, ny = posx + i, posy + j
                # Calcola la distanza euclidea dalla posizione centrale
                distanza = math.sqrt(i ** 2 + j ** 2)

                # Controlla se la cella vicina è all'interno del raggio e all'interno dei limiti della griglia
                if ( (nx, ny) in drone.my_cells ) and ( distanza <= raggio ): # non controllo se è dentro i limiti della griglia in quanto la cella deve appartenere alle celle del drone
                    # calcola se la cella è già stata visitata
                    vv = self.get_value(nx, ny)
                    if vv == 'WALL': # se la cella è una parete
                        valore_possibile += 0.0
                    elif vv == 0.0:
                        valore_possibile += 4.0 # per aiutare i bordi non scoperti
                    elif vv <= 0.25:
                        valore_possibile += (2.0 - vv) # per aiutare i bordi
                    else: # se la cella non è stata visitata, le assegno un "premio" per invogliare il drone a visitarla
                        valore_possibile += (1.0 - vv)
        return valore_possibile

    def neerest_free(self, i, j):
        for r in range(1, 11 + 1):
            # itera su tutte le celle nell'anello
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if abs(dx) != r and abs(dy) != r: # evita di controllare le celle interne all'anello già controllate
                        continue
                    nx, ny = i + dx, j + dy
                    if self.is_within_bounds(nx, ny) and not self.is_wall(nx, ny):
                        return nx, ny
        # Fallback se nessuna cella è valida
        return None
#------------------------------------------------------partizione--------------------------------------------------------
        # partizione di Voronoi
    def partizione(self):  # aggiornato per le pareti
            # libero le celle assegnate ai droni
        self.dronelist_clear_cells()
        # per ogni cella della griglia e solo quelle
        for i in range(0, self.grid.shape[0]):
            for j in range(0, self.grid.shape[1]):
                # per ogni cella viene calcolato il drone più vicino
                min_distance = -1  # -1 indica che non è stata ancora calcolata la distanza
                min_drone = None  # nessun drone assegnato
                if self.get_value(i, j) == 'WALL':
                    continue
                px = i  # posizione x della cella
                py = j  # posizione y della cella
                for dd in self.dronelist:  # per ogni drone creato
                    pdx, pdy = dd.get_position()  # posizione x e y del drone
                    # calcola la distanza euclidea tra la cella e il drone
                    distance = math.sqrt((pdx - px) ** 2 + (pdy - py) ** 2)
                    # se la distanza è minore della distanza minima o non è stata ancora calcolata
                    if (distance < min_distance) or (min_distance == -1):
                        min_distance = distance
                        min_drone = dd  # salva il drone più vicino
                    # assign to the cell the closest drone
                min_drone.add_cell((i, j))  # passo una tupla contenente la pos della cella

#------------------------------------------------------dijkstra--------------------------------------------------------
    def dijkstra(self, start_x, start_y):
        rows, cols = self.grid.shape
        # Matrice delle distanze (infinito per tutte le celle all'inizio)
        dist = np.full((rows, cols), float('inf'))
        dist[start_x, start_y] = 0  # Distanza iniziale = 0

        # Priority queue (heap)
        pq = []
        heapq.heappush(pq, (0, start_x, start_y))  # (distanza, x, y)
        # Dizionario per tracciare il percorso
        prev = {}
        # Direzioni per esplorare le celle adiacenti
        directions = [(-1, 0), (1, 0),(0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        while pq:
            current_dist, x, y = heapq.heappop(pq)
            # Se la distanza corrente è maggiore di quella salvata, ignora
            if current_dist > dist[x, y]:
                continue
            # Esplora le celle adiacenti
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if self.is_within_bounds(nx, ny) and not self.is_wall(nx, ny):
                    # Calcola il costo per raggiungere la cella adiacente
                    cost = 1  # Costo uniforme
                    new_dist = current_dist + cost

                    # Aggiorna se troviamo un percorso più breve
                    if new_dist < dist[nx, ny]:
                        dist[nx, ny] = new_dist
                        prev[(nx, ny)] = (x, y)
                        heapq.heappush(pq, (new_dist, nx, ny))
        pq = []
        return dist, prev

    def partizione_dijkstra(self):
        self.dronelist_clear_cells()
        self.dronelist_clear_percorsi()
        self.dronelist_clear_distanze()
        self.dronelist_clear_path()

        # andrà a contenere le matrici delle distanze
        all_distances = []
        for drone in self.dronelist: # ogni drone crea la sua matrice delle distanze
            distances, predecessor = self.dijkstra(drone.x, drone.y) # distances è una matrice, predecessore contiene la lista di celle che devo fare
            drone.percorsi = predecessor
            drone.distanze = distances
            all_distances.append(distances) # all_distances è un array di matrici

        # Assign cells to the closest drone
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                min_distance = float('inf')
                closest_drone = None
                for t, distances in enumerate(all_distances):
                    if distances[i][j] < min_distance:
                        min_distance = distances[i][j]
                        closest_drone = self.dronelist[t]

                if closest_drone is not None:
                    closest_drone.add_cell((i, j))
