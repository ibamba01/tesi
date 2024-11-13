import random

import numpy as np
import mappa
import drone
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    griglia = mappa.MapGrid(40, 40)

    drone_1 = drone.Drone(griglia, 10, 10, los = 4)
    drone_2 = drone.Drone(griglia, 10, 30 , los = 4)
    drone_3 = drone.Drone(griglia, 30, 10 , los = 4)
    drone_4 = drone.Drone(griglia, 30, 30, los = 4)

    for t in range(200):
        griglia.start()
        if t % 10 == 0:
            mgrid = griglia.get_value_grid()
            sns.set_theme(style="darkgrid")
            ax = sns.heatmap(mgrid, vmin=0, vmax=1)
            plt.show()