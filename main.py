import mappa
import drone
import config as cfg

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cfg.svuota_cartella('immagini')
    righe = 40
    colonne = 40
    griglia = mappa.MapGrid(righe, colonne,has_wall=True,rando_wall=True,wall_density=0.2)
    n = 4
    for i in range(0, n):
        drone_i = drone.Drone(griglia, rand=True, los=2)
        drone_i.nome = f"drone_{i}"
    max_valor = 0
    t_turn = 0
    media = 0
    m = 10
    for t in range(m):
        griglia.start(1)

        cfg.heatmap(griglia, "c",) # ricorda u = uniform, c = color, p = partition
        cfg.heatmap(griglia, "p")
        media += griglia.map_knoledge()
        temp=griglia.map_knoledge()
    cfg.create_gif('immagini/color_heat','color_map_',"color", m)
    cfg.create_gif('immagini/partition_heat','part_map_', "partition", m)