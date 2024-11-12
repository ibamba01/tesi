import random

import numpy as np
import mappa
import drone
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    griglia = mappa.MapGrid(49, 49)

    # Inizializza un drone nella posizione
    #drone_1 = drone.Drone(griglia,4,4,los=4)
    #drone_2 = drone.Drone(griglia,rand=True,los=4)
    # Sposta il drone in varie direzioni
    #for t in range(100):
        # suddivido le zone
        #griglia.calc_zones()
        # i droni decidono dove andare
        # si spostano

    # fa vedere il tragitto



    drone_1 = drone.Drone(griglia, rand=True, los=3)
    drone_2 = drone.Drone(griglia, rand=True, los = 3)
    drone_3 = drone.Drone(griglia, rand=True, los = 3)
    drone_4 = drone.Drone(griglia, rand=True, los = 3)
    drone_5 = drone.Drone(griglia, rand=True, los = 3)

    for t in range(100):
        griglia.calc_zones()
        drone_1.see()
        if t % 10 == 0:
            mgrid = griglia.get_value_grid()
            sns.set_theme(style="darkgrid")
            ax = sns.heatmap(mgrid, vmin=0, vmax=1)
            plt.show()
        # i droni decidono dove andare
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
