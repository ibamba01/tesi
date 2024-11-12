import math
import random
class Drone:
# -------------------------------------------- class fun----------------------------------------------------------------
    def __init__(self, grid, x=0, y=0 ,los=2, rand=False):
        # imposta la mappa
        self.grid = grid
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

        # imposta il campo visivo del drone
        self.lineofsight = los
        # aggiunge il drone alla lista dei droni sulla mappa
        self.grid.add_drone(self)

    def __del__(self):
        if self in self.grid.dronelist:
            self.grid.remove_drone(self)

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
        self.see()

    def move_down(self):
        if self.grid.is_within_bounds(self.x + 1, self.y):
            self.x += 1
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")
        self.see()

    def move_left(self):
        if self.grid.is_within_bounds(self.x, self.y - 1):
            self.y -= 1
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")
        self.see()

    def move_right(self):
        if self.grid.is_within_bounds(self.x, self.y + 1):
            self.y += 1
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")
        self.see()

    def teleport(self, x, y):
        if self.grid.is_within_bounds(x, y):
            self.y = y
            self.x = x
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")
        self.see()

    def move(self, x=0, y=0):
        if self.grid.is_within_bounds(self.x, self.y + y):
            self.y += y
        if self.grid.is_within_bounds(self.x + x, self.y):
            self.x += x
        else:
            print("Movimento non consentito: fuori dai limiti della griglia.")
        #print(f"La posizione attuale è:",self.get_position())
        self.see()

    def move_random(self):
        x = random.randint(-1,1)
        y = random.randint(-1,1)
        if self.grid.is_within_bounds(self.x, self.y + y):
            self.y += y
        if self.grid.is_within_bounds(self.x + x, self.y):
            self.x += x
        #print(f"La posizione attuale è:",self.get_position())
        self.see()

# --------------------------------------- logic ------------------------------------------------------------------------
    def see(self):
        for dd in self.grid.dronelist:
            posx, posy = self.get_position()
            celle_visibili = []
            # campo di vista circolare
            for i in range(-self.lineofsight, self.lineofsight + 1):
                for j in range(-self.lineofsight, self.lineofsight + 1):
                    # Calcola la distanza euclidea
                    distance = math.sqrt(i ** 2 + j ** 2)

                    # Se la cella è dentro il raggio di lineofsight e dentro i limiti della griglia
                    if distance <= self.lineofsight and self.grid.is_within_bounds(posx + i, posy + j):
                        celle_visibili.append((posx + i, posy + j))
            #print(f"Celle visibili: {seecell}")  # Aggiungi una stampa per debug
            celle_visibili.append((posx, posy))
            self.grid.update(celle_visibili) # Aggiorna la griglia con quelle celle