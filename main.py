from codice import Mappa as Mappa, Config as Config, Drone as Drone
import json,os
from datetime import datetime

def running(test_iteraction, righe, colonne, iteration, drone_number, line_of_sight, loss_factor, has_wall, random_wall,
                         random_position, alg):
    media = 0
    # inizio Test
    for i in range(test_iteraction):
        media += funtest(righe, colonne, iteration, drone_number, line_of_sight, loss_factor, has_wall, random_wall,
                         random_position, alg)  # serve per fare la media
        print(f"Test {i + 1} di {test_iteraction} completato")

    media /= test_iteraction
    print(f">> Media: {media} di conoscenza durante i test")

    if alg == 1:
        stringalg = "Dijkstra"
    else:
        stringalg = "Voronoi"
    # JSON
    # salva i dati dei test
    risultati = {
        "algoritmo": stringalg,
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
    # prende il path dei dati
    external_path = "C:/Users/Pietro/Desktop/risultati.json"
    # aggiunge i dati alla lista
    if os.path.exists(external_path):
        with open(external_path, "r") as file:
            risultati_list = json.load(file)
    else:
        risultati_list = []
    risultati_list.append(risultati)
    # salva i dati
    with open(external_path, "w") as file:
        json.dump(risultati_list, file, indent=4)


def funtest(r, c, m, n, l, f, hw, rw, rp, alg):
    griglia = Mappa.MapGrid(r, c, has_wall=hw, random_wall=rw, loss_rate=f)
    for ii in range(0, n):
        drone_i = Drone.Drone(griglia, rand=rp, los=l)
        drone_i.name = f"drone_{ii}"
    best_kn = 0
    best_turn = 0
    bestchange = 0
    kn_list = []
    kn_media = 0
    print(">>> Inizio simulazione")
    for t in range(m):
        print(f">>>> Turno",t,"di",m)
        griglia.start(alg)
        kn = griglia.print_map_knoledge()
        kn_list.append(kn)
        kn_media += kn
        if kn > best_kn:
            best_kn = kn
            best_turn = t
            bestchange += 1
    kn_media /= m
    if alg == 1:
        stringalg = "Dijkstra"
    else:
        stringalg = "Voronoi"
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dati = {
        "data e ora": data,
        "algoritmo": stringalg,
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
    file_path = "C:/Users/Pietro/Desktop/dati.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            dati_list = json.load(file)
    else:
        dati_list = []
    dati_list.append(dati)
    with open(file_path, "w") as file:
        json.dump(dati_list, file, indent=4)
    return kn_media

def runnable_show(r, c, m, n, l, f, hw, rw, rp, s, alg):
    Config.svuota_cartella('immagini')

    griglia = Mappa.MapGrid(r, c, has_wall=hw, random_wall=rw, loss_rate=f)
    for ii in range(0, n):
        drone_i = Drone.Drone(griglia, rand=rp, los=l)
        drone_i.name = f"drone_{ii}"
    print(">>> Droni creati")

    best_kn = 0
    best_turn = 0
    bestchange = 0
    kn_list = []
    kn_media = 0
    print(">>> Inizio simulazione")
    for t in range(m):
        griglia.start(alg)
        print(f">>>> Turno {t} di {m}")
        Config.heatmap(griglia, "a", s)  # all
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

    print(">>> Inizio Gif")

    Config.create_gif('immagini/color', 'color_map_', 'color', m)
    Config.create_gif('immagini/percorso', 'percorso_map_', 'percorso', m)
    Config.create_gif('immagini/partition', 'partition_map_', 'partition', m)
    Config.create_gif('immagini/zeri', 'zeri_map_', 'zeri', m)
    for drone in griglia.dronelist:
        Config.create_gif(f'immagini/matrix_distance/{drone.name}', '_matrix_map_', f'{drone.name}_distanze',m)

def teltest(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg):

    #
    #
    # TEST CON MURI ALG DIJKSTRA
    #
    #


    print("""
    
                    TEST stadard 
    
    
    """)
    # standard test
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # test variando los
    line_of_sight = 3
    print(f">>TEST con ", {test_iteraction}, {righe}, {colonne}, {iteration},
          {drone_number}, {line_of_sight}, {loss_factor},
          {has_wall}, {random_wall}, {random_position}, {alg})
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 4
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 2

    # Test variando il numero di droni
    drone_number = 3
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    drone_number = 5
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    drone_number = 6
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # Test droni e los
    line_of_sight = 3
    drone_number = 3
    # meno droni ma con campo visivo più grande
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 4
    drone_number = 3
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # Test al variare del fattore di dimenticanza
    line_of_sight = 2
    drone_number = 4
    loss_factor = 0.96 # dimenticano di più
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.94
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.92
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.90
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.99 # dimenticano di meno
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)


    # Test misti dimenticano di più ma con piu droni
    loss_factor = 0.94
    drone_number = 6
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.96
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.94
    drone_number = 5
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.96
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    print("Tutti i test sono stati completati con algoritmo 1")

    #
    #
    # TEST SENZA MURI ALG VORONOI
    #
    #

    has_wall = False  # se deve impostare i muri
    random_wall = False  # se i muri sono casuali
    random_position = True  # se la posizione di partenza dei droni è casuale
    alg = 0

    # standard test
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # test variando los
    line_of_sight = 3
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 4
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 2

    # Test variando il numero di droni
    drone_number = 3
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    drone_number = 5
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    drone_number = 6
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # Test droni e los
    line_of_sight = 3
    drone_number = 3
    # meno droni ma con campo visivo più grande
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 4
    drone_number = 3
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # Test al variare del fattore di dimenticanza
    line_of_sight = 2
    drone_number = 4
    loss_factor = 0.96  # dimenticano di più
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.94
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.92
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.90
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.99  # dimenticano di meno
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # Test misti dimenticano di più ma con piu droni
    loss_factor = 0.94
    drone_number = 6
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.96
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.94
    drone_number = 5
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.96
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    print("Tutti i test sono stati completati con algoritmo 0")

    #
    #
    # TEST SENZA MURI ALG DIJKSTRA
    #
    #

    has_wall = False  # se deve impostare i muri
    random_wall = False  # se i muri sono casuali
    random_position = True  # se la posizione di partenza dei droni è casuale
    alg = 1

    # standard test
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # test variando los
    line_of_sight = 3
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 4
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 2

    # Test variando il numero di droni
    drone_number = 3
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    drone_number = 5
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    drone_number = 6
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # Test droni e los
    line_of_sight = 3
    drone_number = 3
    # meno droni ma con campo visivo più grande
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 4
    drone_number = 3
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # Test al variare del fattore di dimenticanza
    line_of_sight = 2
    drone_number = 4
    loss_factor = 0.96  # dimenticano di più
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.94
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.92
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.90
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.99  # dimenticano di meno
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # Test misti dimenticano di più ma con piu droni
    loss_factor = 0.94
    drone_number = 6
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.96
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.94
    drone_number = 5
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.96
    running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    print("Tutti i test sono stati completati con algoritmo 1")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # variabili di test
    test_iteraction = 20
    # variabili di esecuzione
    righe = 40 # nuemro righe
    colonne = 40 # numero colonne
    iteration = 250 # numero di turni di esecuzione
    drone_number = 4 # numero di droni
    line_of_sight = 2 # distanza campo visivo dei droni
    loss_factor = 0.98 # fattore di dimenticanza
    has_wall = True # se deve impostare i muri
    random_wall = False # se i muri sono casuali
    random_position = True # se la posizione di partenza dei droni è casuale
    alg = 1

    # fa partire tutti i test
    teltest(test_iteraction, righe, colonne, iteration,drone_number, line_of_sight, loss_factor,has_wall, random_wall, random_position, alg)

    #print(">> Inizia lo show")
    #show = True # per far vedere le immagini mentre procede
    # Crea le immagini.
    #runnable_show(righe, colonne, iteration, drone_number, line_of_sight, loss_factor, has_wall, random_wall,
                         #random_position, show, alg)
