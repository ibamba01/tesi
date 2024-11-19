import random

import mappa
import drone

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


def generate_heatmap_with_colors(grid):
    # Recupera le dimensioni della griglia
    r_ighe, c_olonne = grid.get_bound()

    # Estrai i valori delle celle e degli agenti
    valori = grid.get_value_grid()
    agenti = grid.get_agent_grid()

    # Mappa di colori per gli agenti
    lista_agenti = grid.dronelist_set()
    # creo una mappa ogni agente ha un indice (i)
    # associo a ogni indice (tenendo conto che potrei avere un singolo agente) un colore dalla mappa tab10 che contiene 10 colori distinti
    colori_agenti = {agent: plt.cm.tab10(i / max(1, len(lista_agenti) - 1)) for i, agent in enumerate(lista_agenti)}

    # Costruisci l'immagine RGBA basata su agenti e valori
    heatmap = np.zeros((r_ighe, c_olonne, 4))  # 4 canali: R, G, B, Alpha (trasparenza)
    for i in range(r_ighe):
        for j in range(c_olonne):
            agent = agenti[i, j]
            value = valori[i, j]
            if agent is not None:
                # recupera il colore dell'agente
                colore = colori_agenti[agent]
                # assegna l'intensità del colore in base al valore della cella
                heatmap[i, j] = [c * value for c in colore[:3]] + [1.0]  # RGB con trasparenza Alpha = 1.0
            else:
                heatmap[i, j] = [0.0, 0.0, 0.0, 1.0]  # Nero per celle non esplorate

    # Visualizza la heatmap
    plt.figure(figsize=(8, 8))
    plt.imshow(heatmap, interpolation='nearest')
    #plt.colorbar(plt.cm.ScalarMappable(cmap="viridis"), label="Valore")
    plt.title("Heatmap delle celle esplorate")
    plt.show()

def uniform_heatmap(grid):
    mgrid = grid.get_value_grid()
    sns.set_theme(style="darkgrid")
    ax = sns.heatmap(mgrid, vmin=0, vmax=1)
    plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    righe = 40
    colonne = 40
    griglia = mappa.MapGrid(righe, colonne)

    drone_1 = drone.Drone(griglia, random.randint(0, righe), random.randint(0, colonne), los = 4)
    drone_2 = drone.Drone(griglia, random.randint(0, righe), random.randint(0, colonne), los = 4)
    drone_3 = drone.Drone(griglia, random.randint(0, righe), random.randint(0, colonne), los = 4)
    drone_4 = drone.Drone(griglia, random.randint(0, righe), random.randint(0, colonne), los = 4)

    max_valor = 0
    t_turn = 0
    media = 0
    for t in range(200):
        griglia.start()
        if t % 10 == 0:
            generate_heatmap_with_colors(griglia)
            media += griglia.map_knoledge()
            temp=griglia.map_knoledge()
            if temp > max_valor:
                max_valor = temp
                t_turn = t
            print(f"Turno: {t} - Valore massimo: {max_valor} - Turno massimo: {t_turn}")
            print(temp)
    media /= 20

    gg= 0.5873760959286027  # media calcolata con 200 turni 4 droni 40x40 con los=4 e ricerca circolare con r = 10
    print(f"Fine simulazione\n", f"Valore massimo: {max_valor} - ottenuto al Turno: {t_turn}")
    print(f"Media: {media}")
