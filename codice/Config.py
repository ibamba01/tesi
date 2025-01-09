import matplotlib.pyplot as plt
from wand.image import Image
import seaborn as sns
import numpy as np
import os

color_counter = 0
partition_counter = 0
per_counter = 0
event_counter = 0
zeri_counter = 0

# crea una gif
def create_gif(input_folder='immagini/color', file_name='color_map_', name='output', n=200, delay=30):
    input_folder = rf'{input_folder}'
    image_files = [f"{input_folder}/{file_name}{i}.png" for i in range(n)]
    if not image_files:
        raise ValueError("Nessuna immagine trovata nella cartella specificata. Controlla i parametri di input.")

    output_gif = f'{name}.gif'
    output_path = os.path.join('immagini', 'gif')
    os.makedirs(output_path, exist_ok=True)

    # Crea una GIF animata con Wand
    with Image() as gif:
        for file in image_files:
            try:
                with Image(filename=file) as img:
                    gif.sequence.append(img)
            except Exception as e:
                print(f"Errore durante il caricamento dell'immagine '{file}': {e}")
        if not gif.sequence:
            raise ValueError("Non è stato possibile aggiungere alcuna immagine alla GIF.")
        for frame in gif.sequence:
            frame.delay = delay  # Delay di n centesimi di secondo (n ms)

        gif.type = 'optimize'
        gif.loop_count = 0  # Loop infinito
        output_file = os.path.join(output_path, output_gif)
        print("Salvataggio GIF in corso...")
        gif.save(filename=output_file)
        print(f"GIF salvata come '{output_file}'.")

def svuota_cartella(cartella):
    # Itera attraverso la cartella in modo r icorsivo
    for root, dirs, files in os.walk(cartella, topdown=False):  # topdown=False per gestire prima le sottocartelle
        # Elimina tutti i file
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)  # Elimina il file

    print(f"La cartella '{cartella}' è stata svuotata con successo.")


def color_heatmap(grid, show=False):
    global color_counter  # Usa la variabile globale
    # Recupera le dimensioni della griglia
    r_ighe, c_olonne = grid.get_bound()
    # Mappa di colori per gli agenti
    lista_agenti = grid.get_dronelist_set()
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
            elif value == 'EVENT':
                heatmap[i, j] = [0.0, 1.0, 0.0, 1.0]
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
    filename = f'immagini/color/color_map_{color_counter}.png'
    color_counter += 1

    # Visualizza la heatmap
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.figure(figsize=(8, 8))
    plt.imshow(heatmap, interpolation='nearest')
    #plt.colorbar(plt.cm.ScalarMappable(cmap="viridis"), label="Valore")
    plt.title("Heatmap delle celle esplorate")
    plt.savefig(filename)
    if show:
        plt.show()
    else:
        plt.close()


def partition_heatmap(grid):
    global partition_counter
    r_ighe, c_olonne = grid.get_bound()
    lista_agenti = grid.get_dronelist_set()
    colori_agenti = {agent: plt.cm.tab10(i / max(1, len(lista_agenti) - 1)) for i, agent in enumerate(lista_agenti)}
    heatmap = np.zeros((r_ighe, c_olonne, 4))
    for dd in lista_agenti:
        for cell in dd.my_cells:
            i,j = cell
            colore = colori_agenti[dd]
            heatmap[i, j] = [c for c in colore[:3]] + [1.0]
        i, j = dd.get_position()
        heatmap[i, j] = [0.0, 0.0, 0.0, 1.0]
    filename = f'immagini/partition/partition_map_{partition_counter}.png'
    partition_counter += 1
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.figure(figsize=(8, 8))
    plt.imshow(heatmap, interpolation='nearest')
    plt.title("Heatmap della partizione")
    plt.savefig(filename)
    plt.close()

def uniform_heatmap(grid):
    mgrid = grid.get_value_grid()
    sns.set_theme(style="darkgrid")
    ax = sns.heatmap(mgrid, vmin=0, vmax=1)
    plt.show()

def percorso_heatmap(grid):
    global per_counter
    r_ighe, c_olonne = grid.get_bound()
    lista_agenti = grid.get_dronelist_set()
    colori_agenti = {agent: plt.cm.tab10(i / max(1, len(lista_agenti) - 1)) for i, agent in enumerate(lista_agenti)}
    heatmap = np.zeros((r_ighe, c_olonne, 4))
    for dd in lista_agenti:
        for cell in dd.path_to_target:
            i,j = cell
            colore = colori_agenti[dd]
            heatmap[i, j] = [c for c in colore[:3]] + [1.0]
        i, j = dd.get_position()
        heatmap[i, j] = [0.0, 0.0, 0.0, 1.0]
        i, j = dd.target
        heatmap[i, j] = [0.0, 1.0, 0.0, 1.0]
    filename = f'immagini/percorso/percorso_map_{per_counter}.png'
    per_counter += 1
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.figure(figsize=(8, 8))
    plt.imshow(heatmap, interpolation='nearest')
    plt.title("Heatmap del percorso")
    plt.savefig(filename)
    plt.close()


def zero_heatmap(grid):
    global zeri_counter
    r_ighe, c_olonne = grid.get_bound()
    heatmap = np.zeros((r_ighe, c_olonne))
    for i in range(r_ighe):
        for j in range(c_olonne):
            value = grid.get_value(i, j)
            if value == 'WALL':
                heatmap[i, j] = -1
            else:
                heatmap[i, j] = value
    filename = f'immagini/zeri/zeri_map_{zeri_counter}.png'
    zeri_counter += 1
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.figure(figsize=(8, 8))
    cmap = plt.cm.get_cmap('viridis')
    cmap.set_under(color='gray')
    plt.imshow(heatmap, cmap=cmap, interpolation='nearest', vmin=0.0)
    plt.colorbar(label="Valore della mappa")
    plt.title("Heatmap globale")
    plt.savefig(filename)
    plt.close()

def distance_heatmap(grid, drone):
    r_ighe, c_olonne = grid.get_bound()
    heatmap = np.zeros((r_ighe, c_olonne))
    for i in range(r_ighe):
        for j in range(c_olonne):
            value = drone.distance_matrix[i][j]
            if value is None:
                heatmap[i, j] = -1
            else:
                heatmap[i, j] = value
    filename = f'immagini/matrix_distance/{drone.name}/_matrix_map_{drone.matrix_counter}.png'
    drone.matrix_counter += 1
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.figure(figsize=(8, 8))
    cmap = plt.cm.get_cmap('inferno_r')
    cmap.set_under(color='gray')
    plt.imshow(heatmap, cmap=cmap, interpolation='nearest', vmin=0.0)
    plt.colorbar(label="Valore della distanza")
    plt.title("Matrice delle distanze")
    plt.savefig(filename)
    plt.close()

def event_heatmap(grid):
    global event_counter
    r_ighe, c_olonne = grid.get_bound()
    heatmap = np.zeros((r_ighe, c_olonne, 4))
    for i in range(r_ighe):
        for j in range(c_olonne):
            value = grid.get_value(i, j)
            if value == 'WALL':
                heatmap[i, j] = [0.502, 0.502, 0.502, 1.0]
            elif value == 'EVENT':
                heatmap[i, j] = [1.0, 0.0, 0.0, 1.0]
            else:
                heatmap[i, j] = [0.0, 0.0, 0.0, 1.0]  # Nero per celle non esplorate
    filename = f'immagini/event/event_map_{event_counter}.png'
    event_counter += 1
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.figure(figsize=(8, 8))
    plt.imshow(heatmap, interpolation='nearest')
    plt.title("Heatmap del percorso")
    plt.savefig(filename)
    plt.close()
    
def heatmap(grid, map="c", s=False):
    if map == "c": #color
        color_heatmap(grid,s)
    elif map == "p": #partition
        partition_heatmap(grid)
    elif map == "e": #percorso
        percorso_heatmap(grid)
    elif map == "z": #zero
        zero_heatmap(grid)
    elif map == "a": #all
        color_heatmap(grid)
        partition_heatmap(grid)
        percorso_heatmap(grid)
        zero_heatmap(grid)
        for drone in grid.dronelist:
            distance_heatmap(grid, drone)
    elif map == 'event':
        event_heatmap(grid)
    else: #error
        print("Mappa non valida")
        return


def print_tree(startpath, indent=""):
    for item in os.listdir(startpath):
        path = os.path.join(startpath, item)
        if os.path.isdir(path):
            print(f"{indent}📂 {item}")
            print_tree(path, indent + "    ")
        else:
            print(f"{indent}📄 {item}")

# Sostituisci con il path del tuo progetto

def graf_kn(arrx,arry):
    filename = f'immagini/grafici/conoscenza.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.clf()
    plt.plot(arrx, arry, color='blue', label='Variazione del livello di conoscenza in base al tempo')
    plt.xlabel('Tempo')
    plt.ylabel('Livello di conoscenza')
    plt.title('Livello di conoscenza globale')
    plt.legend()
    plt.savefig(filename)
    plt.close()
