from fileinput import filename

from codice import Mappa as Mappa, Config as Config, Drone as Drone
import json,os
from datetime import datetime
import matplotlib.pyplot as plt

def running(test_iteraction, righe, colonne, iteration, drone_number, line_of_sight, loss_factor, has_wall, random_wall,
                         random_position, alg):
    print(f">>TEST con ", "test_iteraction:", test_iteraction, "righe:", righe, "colonne:", colonne, "iteration:",
          iteration, "drone_number:", drone_number, "line_of_sight:", line_of_sight, "loss_factor:", loss_factor,
          "has_wall:", has_wall,
          "random_wall:", random_wall, "random_position:", random_position, "alg:", alg)
    media = 0
    media_lista = None
    # inizio Test
    for i in range(test_iteraction):
        # mm è la media di conoscenza di un singolo test e listf è la lista di conoscenze di ogni turno di un singolo test
        mm, listf = funtest(righe, colonne, iteration, drone_number, line_of_sight, loss_factor, has_wall, random_wall,
                         random_position, alg)  # serve per fare la media
        media += mm
        if media_lista is None:
            media_lista = listf[:]  # Usa una copia per mantenere indipendenza
        else:
            for j in range(len(listf)):
                media_lista[j] += listf[j]
        print(f"Test {i + 1} di {test_iteraction} completato")

    for j in range(len(media_lista)):
        media_lista[j] /= test_iteraction

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

    return media_lista



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
    return kn_media, kn_list # ritorna la media di conoscenza e la lista di conoscenze

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
    result_standard  = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)



    # test variando los
    line_of_sight = 3
    result_l3 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    line_of_sight = 4
    result_l4 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    line_of_sight = 2 # normale


    # Test variando il numero di droni
    drone_number = 3
    result_d3 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)


    drone_number = 5
    result_d5 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)


    drone_number = 6
    result_d6 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    drone_number = 4  # normale



    # Test al variare del fattore di dimenticanza
    loss_factor = 0.96  # dimenticano di più
    result_lo6 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.94
    result_lo4 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.92
    result_lo2 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.90
    result_lo0 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.99  # dimenticano di meno
    result_lo9 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    loss_factor = 0.98 # normale



# TEST MISTI
    # Test droni e los
    line_of_sight = 3 # piu grande
    drone_number = 3 # meno droni
    # meno droni ma con campo visivo più grande
    result_d3l3 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    line_of_sight = 4
    drone_number = 2
    result_d2l4 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    line_of_sight = 4
    drone_number = 3
    result_d3l4 = running(test_iteraction, righe, colonne, iteration,
                          drone_number, line_of_sight, loss_factor,
                          has_wall, random_wall, random_position, alg)
    line_of_sight = 2 # normale


    # Test misti dimenticano di più ma con piu droni
    # 6 droni
    loss_factor = 0.94
    drone_number = 6
    result_lo4d6 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.96
    result_lo6d6 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    # 5 droni
    loss_factor = 0.94
    drone_number = 5
    result_lo4d5 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.96
    result_lo6d5 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)
    drone_number = 4 # normale


    # Test misti dimenticano di più ma con vista maggiore
    loss_factor = 0.96
    line_of_sight = 3
    result_lo6l3 = running(test_iteraction, righe, colonne, iteration,
                           drone_number, line_of_sight, loss_factor,
                           has_wall, random_wall, random_position, alg)
    line_of_sight = 4
    result_lo6l4 = running(test_iteraction, righe, colonne, iteration,
                           drone_number, line_of_sight, loss_factor,
                           has_wall, random_wall, random_position, alg)
    loss_factor = 0.94
    result_lo4l4 = running(test_iteraction, righe, colonne, iteration,
                           drone_number, line_of_sight, loss_factor,
                           has_wall, random_wall, random_position, alg)
    line_of_sight = 3
    result_lo4l3 = running(test_iteraction, righe, colonne, iteration,
                           drone_number, line_of_sight, loss_factor,
                           has_wall, random_wall, random_position, alg)




    # Test misti dimenticano di più ma con piu droni
    loss_factor = 0.94
    drone_number = 6
    line_of_sight = 3
    result_lo4d6l3 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.96
    result_lo6d6l3 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.94
    drone_number = 5
    result_lo4d5l3 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.96
    result_lo6d5l3 = running(test_iteraction, righe, colonne, iteration,
            drone_number, line_of_sight, loss_factor,
            has_wall, random_wall, random_position, alg)

    loss_factor = 0.99
    drone_number = 2
    line_of_sight = 2
    result_lo9d2l2 = running(test_iteraction, righe, colonne, iteration,
                             drone_number, line_of_sight, loss_factor,
                             has_wall, random_wall, random_position, alg)

    drone_number = 2
    line_of_sight = 3
    result_lo9d2l3 = running(test_iteraction, righe, colonne, iteration,
                             drone_number, line_of_sight, loss_factor,
                             has_wall, random_wall, random_position, alg)

    drone_number = 3
    line_of_sight = 3
    result_lo9d3l3 = running(test_iteraction, righe, colonne, iteration,
                             drone_number, line_of_sight, loss_factor,
                             has_wall, random_wall, random_position, alg)

    arrx = list(range(iteration))
    Config.svuota_cartella('immagini/grafici')
    filename = f'immagini/grafici/standard.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.clf()
    plt.plot(arrx, result_standard, color='blue', label='Standard')
    plt.xlabel('Tempo')
    plt.ylabel('Livello di conoscenza')
    plt.savefig(filename)
    plt.close()


    filename = f'immagini/grafici/confronto_droni.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.clf()
    plt.plot(arrx, result_standard, color='blue', label='Standard')
    plt.plot(arrx, result_d3, color='red', label='3 droni')
    plt.plot(arrx, result_d5, color='green', label='5 droni')
    plt.plot(arrx, result_d6, color='orange', label='6 droni')
    plt.xlabel('Tempo')
    plt.ylabel('Livello di conoscenza')
    plt.legend()
    plt.savefig(filename)
    plt.close()

    filename = f'immagini/grafici/confronto_los.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.clf()
    plt.plot(arrx, result_standard, color='blue', label='Standard')
    plt.plot(arrx, result_l3, color='red', label='LOS 3')
    plt.plot(arrx, result_l4, color='green', label='LOS 4')
    plt.xlabel('Tempo')
    plt.ylabel('Livello di conoscenza')
    plt.legend()
    plt.savefig(filename)
    plt.close()

    filename = f'immagini/grafici/confronto_loss.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.clf()
    plt.plot(arrx, result_standard, color='blue', label='Standard')
    plt.plot(arrx, result_lo6, color='red', label='Loss factor 0.96')
    plt.plot(arrx, result_lo4, color='green', label='Loss factor 0.94')
    plt.plot(arrx, result_lo2, color='orange', label='Loss factor 0.92')
    plt.plot(arrx, result_lo0, color='purple', label='Loss factor 0.90')
    plt.plot(arrx, result_lo9, color='black', label='Loss factor 0.99')
    plt.xlabel('Tempo')
    plt.ylabel('Livello di conoscenza')
    plt.legend()
    plt.savefig(filename)
    plt.close()

    filename = f'immagini/grafici/confronto_misti_droni_los.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.clf()
    plt.plot(arrx, result_standard, color='blue', label='Standard')
    plt.plot(arrx, result_d3l3, color='red', label='3 droni LOS 3')
    plt.plot(arrx, result_d3l4, color='green', label='3 droni LOS 4')
    plt.plot(arrx, result_d2l4, color='orange', label='2 droni LOS 4')
    plt.xlabel('Tempo')
    plt.ylabel('Livello di conoscenza')
    plt.legend()
    plt.savefig(filename)
    plt.close()

    filename = f'immagini/grafici/confronto_misti_loss_droni.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.clf()
    plt.plot(arrx, result_standard, color='blue', label='Standard')
    plt.plot(arrx, result_lo4d5, color='red', label='Loss factor 0.94 5 droni')
    plt.plot(arrx, result_lo6d5, color='green', label='Loss factor 0.96 5 droni')
    plt.plot(arrx, result_lo4d6, color='orange', label='Loss factor 0.94 6 droni')
    plt.plot(arrx, result_lo6d6, color='purple', label='Loss factor 0.96 6 droni')
    plt.xlabel('Tempo')
    plt.ylabel('Livello di conoscenza')
    plt.legend()
    plt.savefig(filename)
    plt.close()


    filename = f'immagini/grafici/confronto_misti_loss_los.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.clf()
    plt.plot(arrx, result_standard, color='blue', label='Standard')
    plt.plot(arrx, result_lo6l3, color='red', label='Loss factor 0.96 LOS 3')
    plt.plot(arrx, result_lo6l4, color='green', label='Loss factor 0.96 LOS 4')
    plt.plot(arrx, result_lo4l3, color='orange', label='Loss factor 0.94 LOS 3')
    plt.plot(arrx, result_lo4l4, color='purple', label='Loss factor 0.94 LOS 4')
    plt.xlabel('Tempo')
    plt.ylabel('Livello di conoscenza')
    plt.legend()
    plt.savefig(filename)
    plt.close()

    filename = f'immagini/grafici/confronto_misti.png'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.clf()
    plt.plot(arrx, result_standard, color='blue', label='Standard')
    plt.plot(arrx, result_lo9d2l2, color='black', label='Loss factor 0.99 2 droni LOS 2')
    plt.plot(arrx, result_lo9d2l3, color='yellow', label='Loss factor 0.99 2 droni LOS 3')
    plt.plot(arrx, result_lo9d3l3, color='brown', label='Loss factor 0.99 3 droni LOS 3')
    plt.plot(arrx, result_lo4d5l3, color='red', label='Loss factor 0.94 5 droni LOS 3')
    plt.plot(arrx, result_lo6d5l3, color='green', label='Loss factor 0.96 5 droni LOS 3')
    plt.plot(arrx, result_lo4d6l3, color='orange', label='Loss factor 0.94 6 droni LOS 3')
    plt.plot(arrx, result_lo6d6l3, color='purple', label='Loss factor 0.96 6 droni LOS 3')
    plt.xlabel('Tempo')
    plt.ylabel('Livello di conoscenza')
    plt.legend()
    plt.savefig(filename)
    plt.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # variabili di test
    test_iteraction = 10
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

