import numpy as np
import random
import math
class MapGrid:
    def __init__(self, righe, colonne, valore_iniziale=0, agente_iniziale=None , rando=False):
        # Crea una griglia di dimensioni (rows x cols) con valore iniziale specificato
        if rando:
            # crea una matrice vuota, n x m in cui ogni cella è un oggetto complesso
            self.grid = np.empty((righe, colonne), dtype=object)
            # itera su tutte le celle
            for i in range(righe):
                for j in range(colonne):
                    # assegna a ogni cella un valore casuale, e l'agente iniziale
                    valore_casuale = round(random.uniform(0, 1), 2)  # Valore casuale tra 0 e 1, arrotondato a 2 decimali
                    self.grid[i, j] = (valore_casuale, agente_iniziale)
        else:
            # dtype = object indica che ogni cella è un oggetto complesso in questo caso contiene una tupla
            # crea una griglia n (righe) x m (colonne), ogni cella è impostata a valore_iniziale default = 0 e "appartiene" a Agente iniziale default = nessuno
            # crea una griglia vuota, n x m
            self.grid = np.empty((righe, colonne), dtype=object)
            # iteriamo su tutte le celle della griglia inizializzando con il valore desiderato
            for i in range(righe):
                for j in range(colonne):
                    self.grid[i, j] = (valore_iniziale, agente_iniziale)
        self.dronelist = [] # mantengo una lista di tutte le istanze dei droni vivi

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

# ----------------------------------------set fun-----------------------------------------------------------------------
    def set_cell(self, row, col, value=None, agente=None):
        # controllo se la cella da modificare è valida
        if self.is_within_bounds(row, col):
            # se non è stato passato un valore
            if value is None:
                # imposto come valore da assegnare il valore corrente
                value = self.grid[row, col][0]
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
        # Inizializza una nuova griglia con valori zero (o un altro valore predefinito)
        grid_agents = np.zeros((self.grid.shape[0], self.grid.shape[1]))
        # Scorri ogni cella della griglia
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                grid_agents[i, j] = self.get_agent(i,j) # Estrai l'agente dalla tupla (valore, agente)
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
            agent = self.grid[row, col][1] # 1 indica il secondo elemento (agente)
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
# ----------------------------------------print fun---------------------------------------------------------------------
    def display(self):
        # Stampa la griglia
        print("\n",self.grid,"\n")
# ----------------------------------------logic fun---------------------------------------------------------------------
    @staticmethod
    def knloss(value):
        return value * 0.98

    def update(self, seencelllist):
        # Applica la perdita di pacchetti solo ai valori numerici
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                valore, agente = self.grid[i, j]
                nuovo_valore = self.knloss(valore)
                self.grid[i, j] = (nuovo_valore, agente)

        for pos in seencelllist:
            posx, posy = pos
            self.set_cell(posx, posy, 1)  # Imposta 1 per le celle visibili

    def calc_zones(self):
        for i in range (0, self.grid.shape[0]):
            for j in range (0, self.grid.shape[1]):
                min_distance = -1
                min_drone = None
                px = i
                py = j
                for dd in self.dronelist:
                    pdx, pdy = dd.get_position()
                    distance = math.sqrt((pdx - px) ** 2 + (pdy - py) ** 2)
                    if distance < min_distance or min_distance == -1:
                        min_distance = distance
                        min_drone = dd
                # assign to the cell the closest drone
                self.set_cell(i, j, agente=min_drone)
                min_drone.add_cell((i,j)) # passo una tupla contenente la pos della cella
        for dd in self.dronelist:
            dd.calc_target()
            dd.move_to_target()


    # data una posizione e un raggio, calcola il la differenza totale del valore delle celle vicine se fossero settate a 1
    def cell_circle_value(self, posx, posy, raggio):
        valore_possibile = 0
        # deve calcolare il valore totale delle celle vicine alla posizione passata in un raggio circolare
        # Itera attraverso le celle circostanti, considerando il raggio
        for i in range(-raggio, raggio + 1):
            for j in range(-raggio, raggio + 1):
                # Calcola la posizione della cella vicina
                nx, ny = posx + i, posy + j

                # Calcola la distanza euclidea dalla posizione centrale
                distanza = math.sqrt(i ** 2 + j ** 2)

                # Controlla se la cella vicina è all'interno del raggio e all'interno dei limiti della griglia
                if ( distanza <= raggio ) and ( self.is_within_bounds(nx, ny) ):# and ( (nx, ny) in self.my_cells ):
                    valore_possibile += (1 - self.get_value(nx, ny) )

        return valore_possibile