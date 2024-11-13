import numpy as np
import random
import math
class MapGrid:
    def __init__(self, righe, colonne, valore_iniziale=0.0, rando=False, perdita=0.98):
        self.perdita = perdita
        # Crea una griglia di dimensioni (rows x cols) con valore iniziale specificato
        if rando:
            # crea una matrice vuota, n x m in cui ogni cella è un oggetto complesso
            self.grid = np.empty((righe, colonne))
            # itera su tutte le celle
            for i in range(righe):
                for j in range(colonne):
                    # assegna a ogni cella un valore casuale, e l'agente iniziale
                    valore_casuale = round(random.uniform(0, 1), 2)  # Valore casuale tra 0 e 1, arrotondato a 2 decimali
                    self.grid[i, j] = valore_casuale
        else:
            # dtype = object indica che ogni cella è un oggetto complesso in questo caso contiene una tupla
            # crea una griglia n (righe) x m (colonne), ogni cella è impostata a valore_iniziale default = 0 e "appartiene" a Agente iniziale default = nessuno
            # crea una griglia vuota, n x m
            self.grid = np.empty((righe, colonne))
            # iteriamo su tutte le celle della griglia inizializzando con il valore desiderato
            for i in range(righe):
                for j in range(colonne):
                    self.grid[i, j] = valore_iniziale
        self.dronelist = [] # mantengo una lista di tutte le istanze dei droni vivi

    # fa partire la logica dei droni
    def start(self):
        # perdita di pacchetti per turno
        self.knloss()
        # partizione di Voronoi
        self.partizione()
        # per ogni drone calcola il target e si sposta
        for dd in self.dronelist:
            dd.calc_target()
            dd.to_target()
            dd.vista_drone()  # imposta a 1 le celle viste dal drone

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
            dd.cler_cell()

# ----------------------------------------set fun-----------------------------------------------------------------------
    def set_cell(self, row, col, value=None):
        # controllo se la cella da modificare è valida
        if self.is_within_bounds(row, col):
            # se non è stato passato un valore
            if value is None:
                # imposto come valore da assegnare il valore corrente
                value = self.grid[row, col][0]
            # imposto il nuovo valore, possessore della cella
            self.grid[row, col] = value
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


    def get_cell(self, row, col):
        # Ottiene il valore di una cella specifica
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            return self.grid[row, col]
        else:
            print("Errore: le coordinate sono fuori dai limiti della griglia.")
            return None

    def get_value(self, row, col):
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            value = self.grid[row, col] # 0 indica il primo elemento (value)
            return value
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
# ----------------------------------------print fun---------------------------------------------------------------------
    def display(self):
        # Stampa la griglia
        print("\n",self.grid,"\n")

# ----------------------------------------logic fun---------------------------------------------------------------------
    def dimenticanza(self, value):
        return value * self.perdita

    def knloss(self):
        # Applica la perdita di pacchetti solo ai valori numerici
        v = np.vectorize(self.dimenticanza)
        self.grid = v(self.grid)

    # partizione di Voronoi
    def partizione(self):
        # libero le celle assegnate ai droni
        self.dronelist_clear_cells()
        # per ogni cella della griglia e solo quelle
        for i in range (0, self.grid.shape[0]):
            for j in range (0, self.grid.shape[1]):
                # per ogni cella viene calcolato il drone più vicino
                min_distance = -1 # -1 indica che non è stata ancora calcolata la distanza
                min_drone = None # nessun drone assegnato

                px = i # posizione x della cella
                py = j # posizione y della cella
                for dd in self.dronelist: # per ogni drone creato
                    pdx, pdy = dd.get_position() # posizione x e y del drone
                    # calcola la distanza euclidea tra la cella e il drone
                    distance = math.sqrt((pdx - px) ** 2 + (pdy - py) ** 2)
                    # se la distanza è minore della distanza minima o non è stata ancora calcolata
                    if (distance < min_distance) or (min_distance == -1):
                        min_distance = distance
                        min_drone = dd # salva il drone più vicino
                # assign to the cell the closest drone
                min_drone.add_cell( (i,j) ) # passo una tupla contenente la pos della cella

    # data una posizione e un raggio, calcola il la differenza totale del valore delle celle vicine se fossero settate a 1
    def cell_circle_value(self, posx, posy, drone):
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
                    if vv == 0.0:
                        valore_possibile += 2.5
                    else: # se la cella non è stata visitata, le assegno un "premio" per invogliare il drone a visitarla
                        valore_possibile += (1.0 - vv)
        return valore_possibile