from codice import Mappa as Mappa, Config as Config, Drone as Drone
import json,os
from datetime import datetime

def funtest(r, c, m, n, l, f, hw, rw, rp):
    griglia = Mappa.MapGrid(r, c, has_wall=hw, random_wall=rw, loss_rate=f)
    for ii in range(0, n):
        drone_i = Drone.Drone(griglia, rand=rp, los=l)
        drone_i.name = f"drone_{ii}"
    best_kn = 0
    best_turn = 0
    bestchange = 0
    kn_list = []
    kn_media = 0
    print("Inizio simulazione")
    for t in range(m):
        griglia.start(1)
        kn = griglia.print_map_knoledge()
        kn_list.append(kn)
        kn_media += kn
        if kn > best_kn:
            best_kn = kn
            best_turn = t
            bestchange += 1
    kn_media /= m
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dati = {
        "data e ora": data,
        "algoritmo": "Dijkstra",
        "righe": r,
        "colonne": c,
        "numero droni": n,
        "numero iterazioni": m,
        "fattore di dimenticamza": griglia.loss,
        "campo visivo dei droni": l,
        "posizioni dei droni randomiche": drone_i.random_position,
        "muri": griglia.has_wall,
        "posizioni muri": griglia.random_wall,
        "numero muri": griglia.num_walls,

        "conoscenza media globale": kn_media,
        "miglior conoscenza": best_kn,
        "turno migliore": best_turn,
        "numero cambiamenti": bestchange,
    }
    file_path = "dati.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            dati_list = json.load(file)
    else:
        dati_list = []
    dati_list.append(dati)
    with open(file_path, "w") as file:
        json.dump(dati_list, file, indent=4)
    return kn_media

def runnable_show(r, c, m, n, l):
    Config.svuota_cartella('immagini')

    griglia = Mappa.MapGrid(r, c, has_wall=True)
    for ii in range(0, n):
        drone_i = Drone.Drone(griglia, rand=True, los=l)
        drone_i.name = f"drone_{ii}"
    print("Droni creati")

    best_kn = 0
    best_turn = 0
    bestchange = 0
    kn_list = []
    kn_media = 0
    print("Inizio simulazione")
    for t in range(m):
        griglia.start(1)
        print(f"Turno {t} di {m}")
        Config.heatmap(griglia, "a")  # all
        kn = griglia.print_map_knoledge()
        kn_list.append(kn)
        kn_media += kn
        if kn > best_kn:
            best_kn = kn
            best_turn = t
            bestchange += 1
    kn_media /= m
    print(f"Best knowledge: {best_kn} at turn {best_turn}")

    x = list(range(m))
    Config.graf_kn(x, kn_list)

    print("Inizio Gif")
    for drone in griglia.dronelist:
        Config.create_gif(f'immagini/matrix_distance/{drone.name}', '_matrix_map_', f'{drone.name}_distanze',m)
    Config.create_gif('immagini/color', 'color_map_', 'color', m)
    Config.create_gif('immagini/percorso', 'percorso_map_', 'percorso', m)
    Config.create_gif('immagini/partition', 'partition_map_', 'partition', m)
    Config.create_gif('immagini/zeri', 'zeri_map_', 'zeri', m)




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test_iteraction = 10

    righe = 40
    colonne = 40
    iteration = 25
    drone_number = 4
    line_of_sight = 2
    loss_factor = 0.98
    media = 0
    has_wall = True
    random_wall = True
    random_position = True
    for i in range(test_iteraction):
        media += funtest(righe,colonne,iteration,drone_number,line_of_sight,loss_factor,has_wall,random_wall,random_position) # serve per fare la media
        print(f"Test {i+1} di {test_iteraction}")
    media /= test_iteraction
    print(f"Media: {media}")
    risultati = {
        "algoritmo": "Dijkstra",
        "righe": righe,
        "colonne": colonne,
        "numero droni": drone_number,
        "numero iterazioni": iteration,
        "numero di test": iteration,
        "fattore di dimenticamza": loss_factor,
        "campo visivo dei droni": line_of_sight,
        "posizioni dei droni randomiche": random_position,
        "muri": has_wall,
        "posizioni muri": random_wall,
        "conoscenza media globale": media,
    }
    file_path = "risultati.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            risultati_list = json.load(file)
    else:
        risultati_list = []
    risultati_list.append(risultati)
    with open(file_path, "w") as file:
        json.dump(risultati_list, file, indent=4)

    runnable_show(righe, colonne, iteration, drone_number, line_of_sight)
