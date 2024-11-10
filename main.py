import numpy as np
from sqlalchemy.sql.functions import random
import mappa
import drone
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    griglia = mappa.MapGrid(49, 49)

    # Inizializza un drone nella posizione (0, 0)
    drone = drone.Drone(griglia,4,4)
    print(f"Posizione iniziale del drone: {drone.get_position()}")
    # Sposta il drone in varie direzioni
    for i in range(1, 50):
        drone.move_random()
    print(f"Posizione del drone finale: {drone.get_position()}")


    # fa vedere il tragitto
    mgrid =griglia.get_map()
    sns.set_theme(style="darkgrid")
    ax = sns.heatmap(mgrid, vmin=0, vmax=1)
    plt.show()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
