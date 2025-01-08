from codice import Mappa as Mappa, Config as Config, Drone as Drone
import json,os
from datetime import datetime

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Config.svuota_cartella('immagini')

    righe = 40
    colonne = 40
    m = 250
    n = 4
    los = 2

    griglia = Mappa.MapGrid(righe, colonne, has_wall=True)

    for i in range(0, n):
        drone_i = Drone.Drone(griglia, rand=True, los=los)
        drone_i.name = f"drone_{i}"
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
        #Config.heatmap(griglia, "a") # all
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
    Config.graf_kn(x,kn_list)

    print("Inizio Gif")
    #for drone in griglia.dronelist:
     #   Config.create_gif(f'immagini/matrix_distance/{drone.name}', '_matrix_map_', f'{drone.name}_distanze', m)
    #Config.create_gif('immagini/color', 'color_map_', 'color', m)
    #Config.create_gif('immagini/percorso', 'percorso_map_', 'percorso', m)
    #Config.create_gif('immagini/partition', 'partition_map_', 'partition', m)
    #Config.create_gif('immagini/zeri', 'zeri_map_', 'zeri', m)

    data =datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dati = {
        "data e ora": data,
        "righe": righe,
        "colonne": colonne,
        "numero droni": n,
        "numero iterazioni": m,
        "fattore di dimenticamza": griglia.loss,
        "campo visivo dei droni": los,
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

    print("Dati aggiunti al file JSON!")