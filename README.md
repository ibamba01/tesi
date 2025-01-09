


### Immagini e gif


Le possibilità di output delle immmagini sono 5, *Color*, *Uniform*, *Partition*, *Percorso*, *Distance*.
e possono essere mostrate durante l'escuzione mettendo show a True, altrimenti sono salvate nella cartella immagini 
e successivamente trasformate in gif e messe nella sotto cartella gif.
- Color: un colore per drone con graduazione di colore per rappresentare il livello di conoscenza 
(in grigio vengono posti i muri, in bianco i droni e in nero le celle non scoperte)
- Uniform: un unica graduazione per tutti i droni, (non vengono inserite le posizioni dei droni)
- Partition: colora tutte le celle di appartenenza a un drone del suo colore (i muri vengono messi in bianco)
- Percorso: indica la posizione del drone, la pos del suo target e il percorso che fa per arrivarci
- Distance: fa vedere la matrice delle distanze dei droni (non disponibile con Voronoi)


Le immagini sono create dalla funione, presente nel file Config, ```Config.heatmap(griglia, "a", s)``` 
la funzione richiede la mappa (griglia) e una modalità di visualizzazione in questo caso a (all), mentre la variabile 
s (Boolean), indica se si vuole vedere le immagini mentre vengono create.
Le modalità di visualizzazione sono: **a** (all), **c** (color), **p** (partition), **h** (percorso), **u** (uniform), 
**d** (distance), **e** (event).

Per vedere i risultati senza dover scrivere i vari passaggi, utilizzare la funzione
```runnable_show(40, 40, 20, 4, 2, 0.98, True, False,True, True, 1)```
Questo crea una griglia di 40x40 (**righe** e **colonne**), con 20 (**iteration**) turni di esplorazione, 4 
(**drone_number**) 
droni con distanza di vista 2 (**line_of_sight**), 0.98 di **fattore di dimenticanza**, 
**has_wall** = True (indica che devono essere presenti delle mura sulla mappa), **random_wall** = False 
(costruirà una struttura),
**rando_position** = True (posione di partenza dei droni causale, se impostato a False si deve andare 
alla definizione dei droni
e impostare li la posizione di ogni drone), **show** = True, **alg** = 1 (1 per algoritmo di Dijkstra, 0 per Voronoi)

### Test parametrici
La funzione ``` teletest(test_iteraction, righe, colonne, iteration,drone_number, line_of_sight, loss_factor,has_wall,
 random_wall, random_position, alg) ``` 
richiede anche il parametro **test_iteraction** che indica il numero di volte che ogni test viene eseguito
teletest fa partire l'analisi delle prestazioni della conoscenza globale in base ai diversi parametri. 
Per entrambi gli algoritmi (Voronoi, Dijkstra) e nel caso del secondo viene testaso sia con ostacoli che senza.

##### I test parametrici sono:
- line of sight (2,3,4)
- numero di droni (3,4,5,6)
- fattore di dimenticanza (0.98,0.96,0.94,0.92,0.90)
- le loro combinazioni (los-numdron e fatt-numdron)

ogni test è rappresentato dalla funzione ```running()``` , prende gli stessi parametri della funzione chiamante,
che esegue la simulazione per un numero di volte pari a **test_iteraction** e salva i risultati
in un json sul dekstop così da renderli consultabili successivamente. running chiama ```funtest()```
che esegue la singola simulazione e salva i propri dati in un json separato, 
così da avere informazioni sulle singole simulazioni.

### Metodi per far partire il programma
Se non si vuole utilizzare ```runnable_show(40, 40, 20, 4, 2, 0.98, True, False,True, True, 1)```
si deve utilizzare una combinazione dei seguenti metodi:
```
griglia = Mappa.MapGrid(righe, colonne, has_wall=True/False, random_wall=True/False, loss_rate=0.98)
dd1 = Drone.Drone(griglia, rand=True, los=2) # se rand = False puo non essere messo e inserire x,y
dd2 = Drone.Drone(griglia, rand=True, los=2)
dd3 = Drone.Drone(griglia, rand=True, los=2)
dd4 = Drone.Drone(griglia, rand=True, los=2)
dd1.name = "" # utile per dare il nome alle cartelle
.
.
.
for t in range(m)
    griglia.start(1) # 0 o 1
    Config.heatmap(griglia, "c") # se s non è inserito è falso
    print(griglia.print_map_knoledge())

Config.create_gif('immagini/color', 'color_map_', 'color', m)
```