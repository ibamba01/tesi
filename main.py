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

    # Inizializza una matrice a 0 che andrà a contenere i valori delle celle
    valori = np.zeros((r_ighe, c_olonne))
    # Inizializza una matrice di agenti (oggetti Drone) per la colorazione
    agenti = np.empty((r_ighe, c_olonne), dtype=object)
    # Estrai i valori delle celle e degli agenti
    for i in range(r_ighe):
        for j in range(c_olonne):
            cell_value, cell_agent = grid.get_cell(i, j)
            valori[i, j] = cell_value
            agenti[i, j] = cell_agent

    # Mappa di colori per gli agenti
    # trasformo la matrice agenti in un array e rimuovo i valori None e tutti i duplicati infine lo trasformo in una lista per stabilità
    agenti_unici = list(set(agent for agent in agenti.flatten() if agent is not None))
    # creo una mappa ogni agente ha un indice (i)
    # associo a ogni indice (tenendo conto che potrei avere un singolo agente) un colore dalla mappa tab10 che contiene 10 colori distinti
    colori_agenti = {agent: plt.cm.tab10(i / max(1, len(agenti_unici) - 1)) for i, agent in enumerate(agenti_unici)}

    # Costruisci l'immagine RGBA basata su agenti e valori
    heatmap = np.zeros((r_ighe, c_olonne, 4))  # 4 canali: R, G, B, Alpha
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
                heatmap[i, j] = [1.0, 1.0, 1.0, 1.0]  # Bianco per celle non esplorate

    # Visualizza la heatmap
    plt.figure(figsize=(8, 8))
    plt.imshow(heatmap, interpolation='nearest')
    plt.colorbar(plt.cm.ScalarMappable(cmap="viridis"), label="Valore")
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

    drone_1 = drone.Drone(griglia, 10, 10, los = 4)
    drone_2 = drone.Drone(griglia, 10, 30 , los = 4)
    drone_3 = drone.Drone(griglia, 30, 10 , los = 4)
    drone_4 = drone.Drone(griglia, 30, 30, los = 4)

    max_valor = 0
    t_turn = 0
    for t in range(200):
        griglia.start()
        if t % 10 == 0:
            generate_heatmap_with_colors(griglia)
            temp=griglia.map_knoledge()
            if temp > max_valor:
                max_valor = temp
                t_turn = t
            print(f"Turno: {t} - Valore massimo: {max_valor} - Turno massimo: {t_turn}")
            print(temp)
    print(f"Fine simulazione\n", f"Valore massimo: {max_valor} - ottenuto al Turno: {t_turn}")

