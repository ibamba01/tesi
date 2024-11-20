import mappa
import drone
import config as cfg

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cfg.svuota_cartella('immagini/color_heat')
    righe = 40
    colonne = 40
    griglia = mappa.MapGrid(righe, colonne)
    n = 4
    for i in range(0, n):
        drone_i = drone.Drone(griglia, rand=True, los=2)
        drone_i.nome = f"drone_{i}"

    max_valor = 0
    t_turn = 0
    media = 0
    for t in range(200):
        griglia.start()
        if t % 10 == 0: # da cambiare e mettere a 1 (a ogni iterazione)
            cfg.heatmap(griglia, "c") # ricorda u = uniform, c = color, p = partition
            media += griglia.map_knoledge()
            temp=griglia.map_knoledge()
            if temp > max_valor:
                max_valor = temp
                t_turn = t
            print(f"Turno: {t} - Valore massimo: {max_valor} - Turno massimo: {t_turn}")
            print(temp)
    media /= 20
    print(f"Fine simulazione\n", f"Valore massimo: {max_valor} - ottenuto al Turno: {t_turn}")
    print(f"Media: {media}")
