import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

def svuota_cartella(cartella):
    for root, dirs, files in os.walk(cartella):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)  # Elimina il file

heatmap_counter = 0
def color_heatmap(grid):
    global heatmap_counter  # Usa la variabile globale
    # Recupera le dimensioni della griglia
    r_ighe, c_olonne = grid.get_bound()

    # Mappa di colori per gli agenti
    lista_agenti = grid.dronelist_set()
    # creo una mappa ogni agente ha un indice (i)
    # associo a ogni indice (tenendo conto che potrei avere un singolo agente) un colore dalla mappa tab10 che contiene 10 colori distinti
    colori_agenti = {agent: plt.cm.tab10(i / max(1, len(lista_agenti) - 1)) for i, agent in enumerate(lista_agenti)}

    # Costruisci l'immagine RGBA basata su agenti e valori
    heatmap = np.zeros((r_ighe, c_olonne, 4))  # 4 canali: R, G, B, Alpha (trasparenza)
    for i in range(r_ighe):
        for j in range(c_olonne):
            agent = grid.get_agent(i, j)
            value = grid.get_value(i, j)
            if value == 'WALL':
                heatmap[i, j] = [0.502, 0.502, 0.502, 1.0]
            elif agent is not None:
                # recupera il colore dell'agente
                colore = colori_agenti[agent]
                # assegna l'intensità del colore in base al valore della cella, [:3] serve a estrarre solo i primi 3
                heatmap[i, j] = [c * value for c in colore[:3]] + [1.0]  # RGB con trasparenza Alpha = 1.0
            else:
                heatmap[i, j] = [0.0, 0.0, 0.0, 1.0]  # Nero per celle non esplorate
    for dd in lista_agenti:
        px,py = dd.get_position()
        heatmap[px,py] = [1.0, 1.0, 1.0, 1.0]  # Rosso per la posizione del drone

    # Incrementa il contatore e salva il file
    filename = f'immagini/color_heat/heat_map_{heatmap_counter}.png'
    heatmap_counter += 1

    # Visualizza la heatmap
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.figure(figsize=(8, 8))
    plt.imshow(heatmap, interpolation='nearest')
    #plt.colorbar(plt.cm.ScalarMappable(cmap="viridis"), label="Valore")
    plt.title("Heatmap delle celle esplorate")
    plt.savefig(filename)
    plt.show()


def partition_heatmap(grid):
    global heatmap_counter
    r_ighe, c_olonne = grid.get_bound()
    lista_agenti = grid.dronelist_set()
    colori_agenti = {agent: plt.cm.tab10(i / max(1, len(lista_agenti) - 1)) for i, agent in enumerate(lista_agenti)}
    heatmap = np.zeros((r_ighe, c_olonne, 4))
    for dd in lista_agenti:
        for cell in dd.my_cells:
            i,j = cell
            colore = colori_agenti[dd]
            heatmap[i, j] = [c for c in colore[:3]] + [1.0]
    filename = f'immagini/partition_heat/part_map_{heatmap_counter}.png'
    heatmap_counter += 1
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.figure(figsize=(8, 8))
    plt.imshow(heatmap, interpolation='nearest')
    plt.title("Heatmap della partizione")
    plt.savefig(filename)
    plt.show()

def uniform_heatmap(grid):
    mgrid = grid.get_value_grid()
    sns.set_theme(style="darkgrid")
    ax = sns.heatmap(mgrid, vmin=0, vmax=1)
    plt.show()

def heatmap(grid, map="u"):
    if map == "u": #uniform
        uniform_heatmap(grid)
    elif map == "c": #color
        color_heatmap(grid)
    elif map == "p": #partition
        partition_heatmap(grid)