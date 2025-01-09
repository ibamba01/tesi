#------------------------------------------------import---------------------------------------------------------------
import numpy as np
import random
import math
import heapq
from codice import Generator
#------------------------------------------------inizializazione------------------------------------------------------
class MapGrid:
    def __init__(self, rows, columns, initial_value=0.0, random_values=False, has_wall=False,
                 random_wall=False, loss_rate=0.98, wall_density=0.1):
        self.loss = loss_rate
        self.has_wall = has_wall
        self.random_wall = random_wall
        self.dronelist = []  # mantengo una lista di tutte le istanze dei droni vivi
        self.eventlist = []  # mantengo una lista di tutti gli eventi in vita
        self.num_walls = 0
        self.wall_density = wall_density
        self.grid = np.empty((rows, columns), dtype=object)
        if random_values:
            for i in range(rows):
                for j in range(columns):
                    valore_casuale = round(random.uniform(0, 1),2)
                    self.grid[i, j] = (valore_casuale, None)
        else:
            for i in range(rows):
                for j in range(columns):
                    self.grid[i, j] = (initial_value, None)
        if has_wall:
            if random_wall:
                self.num_walls = int(wall_density * rows * columns)
                for ii in range(self.num_walls):
                    x = random.randint(0, rows - 1)
                    y = random.randint(0, columns - 1)
                    self.grid[x, y] = ('WALL', None)
            else:
                self.construct_house()

    def construct_house(self):
        gen = Generator.Generator(self.grid)
        self.grid, self.num_walls = gen.update_matrix()

#--------------------------------------------------start logic--------------------------------------------------------
    def start(self, choice):
        if choice == 0:
            self.start_with_voronoi()
        elif choice == 1:
            self.start_with_dijkstra()
        else:
            raise ValueError("utilizzare 0 per Voronoi o 1 per Dijkstra")

    # fa partire la logica dei droni
    def start_with_voronoi(self):
        self.clear_finished_events()
        # perdita di conoscenza per turno
        self.knloss()
        # partizione di Voronoi
        self.partition()
        # per ogni drone calcola il target e si sposta
        for dd in self.dronelist:
            dd.calc_target()
            dd.to_target()
            dd.drone_sight()  # imposta a 1 le celle viste dal drone

    def start_with_dijkstra(self):
        self.clear_finished_events()
        self.knloss()
        # partizione delle celle attraverso la vicinaza secondo Dijkstra
        self.partition_dijkstra()
        for drone in self.dronelist:
            # utilizza la distanza di Dijkstra per calcolare il percorso
            drone.calc_target_dijkstra()
            drone.to_target_dijkstra()
            # svuoto il dizionario dei percorsi
            drone.clear_paths()
            # scopre le celle viste dal drone
            drone.drone_sight()

#----------------------------------------perdita di conoscenza-------------------------------------------------------
    # applica la perdita di conoscenza su tutta la mappa
    def knloss(self): # aggiornato per le pareti
        # Applica la perdita di conoscenza solo ai valori numerici
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                value, agent = self.grid[i, j]  # Ottieni la tupla (valore, agente)
                if value not in ('WALL', 'EVENT'):
                    # Applica la perdita al valore e ricrea la tupla
                    self.grid[i, j] = (self.dimenticanza(value), agent)

    # calcola la perdita di conoscenza sul valore passato
    def dimenticanza(self, value):
        return value * self.loss

#----------------------------------------------------partizione--------------------------------------------------------
    # partizione di Voronoi
    def partition(self):  # aggiornato per le pareti
        # libero le celle assegnate ai droni
        self.dronelist_clear_cells()
        for i in range(0, self.grid.shape[0]):
            for j in range(0, self.grid.shape[1]):
                if self.get_value(i, j) == 'WALL': #NON era qui l'errore
                    continue
                min_distance = float('inf')
                min_drone = None  # nessun drone assegnato
                for dd in self.dronelist:  # per ogni drone creato
                    if dd.is_busy():
                        continue
                    pdx, pdy = dd.get_position()  # posizione x e y del drone
                    # calcola la distanza euclidea tra la cella e il drone
                    distance = math.sqrt((pdx - i) ** 2 + (pdy - j) ** 2)
                    # se la distanza è minore della distanza minima o non è stata ancora calcolata
                    if distance < min_distance:
                        min_distance = distance
                        min_drone = dd  # salva il drone più vicino
                if min_drone is not None:
                    min_drone.add_cell((i, j)) # passo una tupla contenente la pos della cella
                    if self.has_event(i,j):
                        if not (i,j) in min_drone.my_events and self.get_event(i,j).active == False:
                            min_drone.add_event((i,j))

    def partition_dijkstra(self):
        # pulizia
        self.dronelist_clear_cells()
        self.dronelist_clear_percorsi()
        self.dronelist_clear_distanze()
        self.dronelist_clear_path()

        # andrà a contenere le matrici delle distanze
        all_distances = []
        for drone in self.dronelist:  # ogni drone crea la sua matrice delle distanze
            distances, predecessor = self.dijkstra(drone.x,
                                                   drone.y)  # distances è una matrice, predecessore contiene la lista di celle che devo fare
            drone.paths = predecessor # assegna il percorso al drone
            drone.distance_matrix = distances # assegna la matrice delle distanze al drone
            all_distances.append(distances)  # all_distances è un array di matrici

        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                min_distance = float('inf') # di base la distanza è infinito
                closest_drone = None
                for t, distances in enumerate(all_distances):
                    if self.dronelist[t].is_busy(): # se il drone è occupato in un evento
                        continue
                    if distances[i][j] < min_distance: # se la distanza è minore della distanza minima
                        min_distance = distances[i][j]
                        closest_drone = self.dronelist[t]

                if closest_drone is not None:
                    closest_drone.add_cell((i, j))
                    if self.has_event(i,j):
                        if not (i,j) in closest_drone.my_events and self.get_event(i,j).active == False:
                            closest_drone.add_event((i,j))

#----------------------------------------------------algoritmo dijkstra-----------------------------------------------
    # aloriomo di Dijkstra per calcolare la distanza data una posizione iniziale
    def dijkstra(self, start_x, start_y):
        rows, cols = self.grid.shape
        # Matrice delle distanze (infinito per tutte le celle all'inizio)
        dist = np.full((rows, cols), float('inf'))
        pq = [] # Priority queue
        prev = {} # Dizionario per tracciare il percorso

        dist[start_x, start_y] = 0  # Distanza iniziale = 0

        heapq.heappush(pq, (0, start_x, start_y))  # (distanza, x, y)

        # Direzioni per esplorare le celle adiacenti
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        while pq:
            # Estrai la cella con la distanza minima
            current_dist, x, y = heapq.heappop(pq)
            # Se la distanza corrente è maggiore di quella salvata, ignora
            if current_dist > dist[x, y]:
                continue
            # Esplora le celle adiacenti
            for dx, dy in directions:
                nx, ny = x + dx, y + dy # Nuove coordinate
                if self.is_within_bounds(nx, ny) and not self.is_wall(nx, ny): # Se la cella è valida
                    # Calcola il costo per raggiungere la cella adiacente
                    cost = 1 + self.get_value(nx,ny) if self.get_value(nx,ny) != 'EVENT' else 1 # Costo basato sulla conoscenza
                    new_dist = current_dist + cost # Nuova distanza

                    # Aggiorna se troviamo un percorso più breve
                    if new_dist < dist[nx, ny]:
                        dist[nx, ny] = new_dist
                        prev[(nx, ny)] = (x, y)
                        heapq.heappush(pq, (new_dist, nx, ny))
        pq = []
        return dist, prev

#---------------------------------------------calcola il valore possibile---------------------------------------------
    # data una posizione e un raggio, calcola il la differenza totale del valore delle celle vicine se fossero settate a 1
    def cell_circle_value(self, posx, posy, drone):
        poss_value = 0.0 # valore possibile, è quello che ritorna
        r = drone.lineofsight # raggio di visuale del drone
        for i in range(-r, r + 1):
            for j in range(-r, r + 1):
                nx, ny = posx + i, posy + j
                dist = math.sqrt(i ** 2 + j ** 2)
                if ((nx, ny) in drone.my_cells) and ( dist <= r): # se la cella è assegnata al drone e rientra nel raggio
                    vv = self.get_value(nx, ny) # valore della cella attuale
                    if vv == 'WALL':
                        poss_value += 0.5 # se è una parete il valore possibile è 0.5 (ammortizza la presenza di pareti)
                    elif vv == 'EVENT':
                        poss_value += 0.0 # se è un evento il valore possibile è 0.0 (non conta, viene messa come target in automatico)
                    elif vv == 0.0:
                        poss_value += 10.0 # se il valore è 0.0 il valore possibile è 5.0 (è una cella non esplorata, do un bonus di esplorazione)
                    elif vv <= 0.25:
                        poss_value += (6.0 - vv) # se il valore è basso, il valore possibile ha un bonus
                    else:
                        poss_value += (1.0 - vv)
        return poss_value


#--------------------------------------------------dronelist--------------------------------------------------------------
    # stampa la lista dei droni con posizione e line-of-sight
    def display_dronelist(self):
        print("Lista dei droni sulla mappa:")
        for i, drone in enumerate(self.dronelist, start=1):
            x, y = drone.get_position()
            print(f"{drone.name}: posizione ({x}, {y}), line-of-sight {drone.lineofsight}")

    # aggiunge un drone alla lista condivisa
    def add_drone(self, drone):
        self.dronelist.append(drone)

    # rimuove un drone dalla lista condivisa
    def remove_drone(self, drone):
        self.dronelist.remove(drone)

    # rimuove tutti i droni dalla lista condivisa
    def clear_dronelist(self):
        self.dronelist.clear()
        print("Tutti i droni sono stati rimossi dalla mappa.")

    # rimuove tutte le celle assegnate ai droni
    def dronelist_clear_cells(self):
        for dd in self.dronelist:
            dd.clear_cell()

    # rimuove tutti i percorsi assegnati ai droni
    def dronelist_clear_percorsi(self):
        for dd in self.dronelist:
            dd.clear_paths()

    # rimuove tutte le matrici delle distanze assegnate ai droni
    def dronelist_clear_distanze(self):
        for dd in self.dronelist:
            dd.clear_distance_matrix()

    # rimuove tutti i percorsi assegnati ai droni
    def dronelist_clear_path(self):
        for dd in self.dronelist:
            dd.clear_path_to_target()

     # restituisce la lista degli agenti senza ripetizioni
    def get_dronelist_set(self):
        agentlist = list(set(dd for dd in self.dronelist))
        return agentlist

#--------------------------------------------------set---------------------------------------------------------------
    # imposta il valore e possessore di una cella
    def set_cell(self, row, col, value=None, agente=None):
        # controllo se la cella da modificare è valida
        if not self.is_within_bounds(row, col):
            print(f"Set-Cell Errore: le coordinate(",{row},",",{col},") sono fuori dai limiti della griglia.","Drone chiamante:",{agente.name})
            return
        # se non è stato passato un valore
        if value is None:
            # imposto come valore da assegnare il valore corrente
            value = self.grid[row, col][0]
        if agente is None:
            # imposto come possessore da assegnare il possessore corrente
            agente = self.grid[row, col][1]
        # imposto il nuovo valore, possessore della cella
        self.grid[row, col] = (value, agente)

    # imposta una cella come parete
    def set_wall(self, row, col):
        self.grid[row, col] = ('WALL', None)
        self.num_walls += 1 # incremento il contatore delle pareti

#--------------------------------------------------get---------------------------------------------------------------
    # restituisce una matrice di soli valori
    def get_value_grid(self):
        # Inizializza una nuova griglia con valori zero (o un altro valore predefinito)
        grid_values = np.zeros((self.grid.shape[0], self.grid.shape[1]))
        # Scorri ogni cella della griglia
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                grid_values[i, j] = self.get_value(i,j)  # Estrai il valore dalla tupla (valore, agente) e lo imposta nella nuova matrice
        return grid_values

    # restituisce un matrice di soli possessori
    def get_agent_grid(self):
        grid_agents = np.empty((self.grid.shape[0], self.grid.shape[1],), dtype=object)
        # Scorri ogni cella della griglia
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                grid_agents[i, j] = self.get_agent(i,j)  # Estrai il valore dalla tupla (valore, agente) e lo imposta nella nuova matrice
        return grid_agents

    # restituisce il contenuto di una cella
    def get_cell(self, row, col):
        # Ottiene il valore di una cella specifica
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            return self.grid[row, col]
        else:
            print("Get Cell Errore: le coordinate sono fuori dai limiti della griglia.")
            return None

    # restituisce il valore di una cella
    def get_value(self, row, col):
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            value = self.grid[row, col][0]  # 0 indica il primo elemento (value)
            return value
        else:
            print("Get Value Errore: le coordinate sono fuori dai limiti della griglia.")
            return None

    # restituisce il possessore di una cella
    def get_agent(self, row, col):
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            agent = self.grid[row, col][1]  # 1 indica il secondo elemento (agent)
            return agent
        else:
            print("Get Agent Errore: le coordinate sono fuori dai limiti della griglia.")
            return None

    # restituisce la dimensione della matrice
    def get_bound(self):
        return self.grid.shape

    # restituisce la matrice e tutto il suo contenuto
    def get_map(self):
        return self.grid

    # restituisce la cella più vicina libera
    def get_neerest_free(self, i, j):
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

#--------------------------------------------------check------------------------------------------------------------
    # controlla se una cella è all'interno dei limiti della griglia
    def is_within_bounds(self, x, y):
        # Verifica se (x, y) è all'interno dei limiti della griglia
        return 0 <= x < self.grid.shape[0] and 0 <= y < self.grid.shape[1]

    # controlla se una cella è occupata dal un altro drone
    def is_occupied(self, x, y):
        occ = False
        for dd in self.dronelist:
            pdx, pdy = dd.get_position()
            if x == pdx and y == pdy:
                occ = True
        return occ

    # controlla se una cella è una parete
    def is_wall(self, x, y):
        if self.get_value(x, y) == 'WALL': #NON era qui l'errore
            return True
        return False

#--------------------------------------------------print------------------------------------------------------------
    # stampa la griglia
    def printa_map(self):
        # Stampa la griglia
        print("\n", self.grid, "\n")

    # stampa la conoscenza media della mappa
    def print_map_knoledge(self):
        tot = 0
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                val = self.get_value(i, j)
                if val == 'WALL':
                    val = 0  # le pareti non contano
                if val == 'EVENT':
                    ag = self.get_event(i, j)
                    if ag.is_active():
                        val = 1
                    else:
                        val = 0
                tot += val
        return tot / ((self.grid.shape[0] * self.grid.shape[1]) - self.num_walls)  # tolgo le pareti dal conteggio

#--------------------------------------------------event------------------------------------------------------------
    # controlla se una cella contiene un evento
    def has_event(self, x, y):
        if self.get_value(x, y) == 'EVENT':
            return True
        return False

    # restituisce l'evento contenuto in una cella
    def get_event(self, x, y):
        if self.has_event(x, y):
            return self.get_agent(x, y)  #l'evento è l'agente della cella
        raise ValueError("Non c'è nessun evento in questa cella")

    # aggiunge un evento alla lista degli eventi
    def add_event_to_list(self, e):# e = event
        self.eventlist.append(e)

    # rimuove un evento dalla lista degli eventi
    def remove_event_from_list(self, e):
        self.eventlist.remove(e)

    # rimuove l'evento dalla cella
    def clear_event(self, x, y, drone):
        e = self.get_event(x, y)
        self.remove_event_from_list(e)
        drone.remove_event()
        self.set_cell(x, y, 1.0, drone)

    # crea un evento in una cella
    def start_event(self, x, y):
        if self.has_event(x, y):
            x = random.randint(self.grid.shape[0], self.grid.shape[1])
            y = random.randint(self.grid.shape[0], self.grid.shape[1])
        e = Event(self, x, y, 3) # crea un evento nella posizione x,y e persiste per 3 turni
        self.add_event_to_list(e)

    # stampa la lista degli eventi assegnati a ogni drone
    def print_event(self):
        for drone in self.dronelist:
            print("il ",drone.name,"ha eventi in:",drone.my_events)

    # rimuove gli eventi terminati dalla lista degli eventi
    def clear_finished_events(self):
        for ev in self.eventlist:
            if ev.terminated:
                self.eventlist.remove(ev)

# creo un evento nella posizione x,y e persiste per una durata di 5 turni (quando attivato)
class Event:
    def __init__(self,grid, x, y, duration=5):
        self.x = x
        self.y = y
        self.duration = duration
        self.grid = grid
        self.active = False
        self.terminated = False
        self.value_on_map()

    # posso voler cambiare la durata dopo la creazione
    def set_duration(self, duration):
        self.duration = duration

    def get_remaining_duration(self):
        return self.duration

    # non posso cambiare la posizione
    def get_position(self):
        return self.x, self.y

    # serve a far passare un turno, se la durata è arrivata a 0 ritorna True
    def trigger(self):
        print("trigger chiama")
        if self.active:
            self.duration -= 1
        if self.duration <= 0:
            self.terminated = True

    def is_terminated(self):
        if self.terminated:
            return True
        else:
            return False

    # imposta a attivo l'evento
    def activate(self):
        self.active = True

    def is_active(self):
        return self.active

    # imposta a terminato l'evento
    def finished(self):
        if self.active:
            self.terminated = True
        else:
            raise ValueError("L'evento non è ancora attivo")

    # imposta il valore della cella a EVENT
    def value_on_map(self): # imposta il valore della cella a EVENT, e l'ultimo a controllarla è l'evento stesso
        self.grid.set_cell(self.x, self.y, 'EVENT', self)