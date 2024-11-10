import numpy as np

class MapGrid:
    def __init__(self, righe, colonne, valore_iniziale=0,rando=False):
        # Crea una griglia di dimensioni (rows x cols) con valore iniziale specificato
        if rando:
            self.grid = np.random.rand(righe, colonne) # riempie la griglia di valori randomici tra 0 e 1
        else:
            if valore_iniziale == 0: # griglia di zeri
                self.grid = np.zeros((righe, colonne))  # doppia parentesi perchè zeros richiede una tupla
            else:
                self.grid = np.full((righe, colonne), valore_iniziale)

    def set_cell(self, row, col, value):
        # .shape[0] rende il num dle righe e .shape[1] rende il num dle colonne
        # Modifica il valore di una cella specifica
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            self.grid[row, col] = value
        else:
            print("Errore: le coordinate sono fuori dai limiti della griglia.")

    def get_cell(self, row, col):
        # Ottiene il valore di una cella specifica
        if 0 <= row < self.grid.shape[0] and 0 <= col < self.grid.shape[1]:
            return self.grid[row, col]
        else:
            print("Errore: le coordinate sono fuori dai limiti della griglia.")
            return None
    def get_bound(self):
        return self.grid.shape[0], self.grid.shape[1]

    def is_within_bounds(self, x, y):
        # Verifica se (x, y) è all'interno dei limiti della griglia
        return 0 <= x < self.grid.shape[0] and 0 <= y < self.grid.shape[1]

    def display(self):
        # Stampa la griglia
        print("\n",self.grid,"\n")

    def loss(self,value):
        return value * 0.9
    def get_map(self):
        return self.grid
    def update(self, seencelllist):
        v = np.vectorize(self.loss)
        self.grid = v(self.grid)

        for pos in seencelllist:
            posx, posy = pos
            self.set_cell(posx, posy, 1)  # Imposta 1 per le celle visibili