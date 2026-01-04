from liste_hanoi import construit_deplacement
import tkinter as tk
from time import sleep
from threading import Lock, Thread

# variables globales
l,h = 900, 300
n = 0 # variable global nb de disques
disques = ([], [], [])
etapes_disques = [disques]
state = 0
colors = ('maroon','red4', 'red3', 'red', 'orange red',
          'DarkOrange2', 'dark orange', 'orange', 'gold',
          'yellow', 'light yellow')
verrou = Lock()

# fonctions de controle

def trace_background(cnv: tk.Canvas):
    """trace le fond de l'image (ciel, sol et mats)

    Arguments:
        cnv -- zone de destination du tracé
    """
    l, h = int(cnv.cget("width")), int(cnv.cget("height"))
    # cnv.create_rectangle(0,0,l,0.9*h, fill="powder blue", outline='powder blue', tag= "sky")
    cnv.create_rectangle(0,0.9*h, l, h, fill="dark olive green", outline='dark olive green', tag= "ground")
    t = l//6
    cnv.create_rectangle(t-5, 0.05*h, t+5, 0.95*h, fill='dark slate gray', tag= "mat0")
    cnv.create_rectangle(3*t-5, 0.05*h, 3*t+5, 0.95*h, fill='dark slate gray', tag= "mat1")
    cnv.create_rectangle(5*t-5, 0.05*h, 5*t+5, 0.95*h, fill='dark slate gray', tag= "mat2")
    
def trace_rect(cnv: tk.Canvas, mat: int, haut: int, larg: int):
    """trace un disque du plateau selon le mat choisi, la hauteur du disque et sa largeur

    Arguments:
        cnv -- Canvas de destination du tracé
        mat -- mat d'ancrage (0, 1 ou 2)
        haut -- hauteur du disque (de 0 à 8)
        larg -- "diamètre du disque (de 1 à 9)
    """
    l, h = int(cnv.cget("width")), int(cnv.cget("height"))
    half_wdth_max = l/6*0.85
    t = (mat*2+1)*l//6
    h_max = 0.95*h - 0.095*h*haut
    h_min = h_max - 0.095*h
    half_wdth = half_wdth_max*(larg+1)/9
    color = colors[larg]
    cnv.create_rectangle(t-half_wdth, h_min, 
                         t+half_wdth, h_max, 
                         fill= color, outline= color,
                         tag = "d"+str(larg))

def init_position(cnv: tk.Canvas, n_d: int):
    """initialise les mats selon le nombre de disques choisi, tout à gauche

    Arguments:
        cnv -- Canvas de destination du tracé
        n_d -- nb de disques choisi
    """
    for i in range(11):
        objs = cnv.find_withtag("d"+str(i))
        for obj in objs:
            cnv.delete(obj)
    trace_background(cnv)
    global disques, etapes_disques, n, state
    etapes_disques = construit_deplacement(n_d)
    disques = construit_deplacement(n_d)[0]
    n = n_d
    state = 0
    for mat in range(3):
        for haut in range(len(disques[mat])):
            larg = disques[mat][haut]
            trace_rect(cnv, mat, haut, larg)
    step.set("0")
    n_choix.set(n)
    entry_step.update()
    lbl_totalstep["text"] = f'/ {str(2**n_d-1)}'

def deplacement_disque(cnv: tk.Canvas, larg:int, mat_dep:int, mat_arr: int, h_dep: int, h_arr: int):
    """permet le mouvement du disque de largeur larg d'un mat à un autre et d'une hauteur à une autre
    en trois mouvements, on sort du mat on se décale et on s'empile sur le mat

    Arguments:
        cnv -- Canvas de destination du déplacement
        larg -- diamètre du disque (de 1 à 9)
        mat_dep -- n° du mat de départ (0 à 2)
        mat_arr -- n° de mat d'arrivée (0 à 2)
        h_dep -- hauteur de départ (0 à 8)
        h_arr -- hauteur d'arrivée (0 à 8)

    Raises:
        ValueError: si on ne trouve pas le disque ou qu'il y en plusieurs
    """
    l, h = int(cnv.cget("width")), int(cnv.cget("height"))
    dplct_haut = -0.095*(h_arr - h_dep)*h
    dplct_mat = l//3*(mat_arr - mat_dep)
    nom_rect = "d"+str(larg)
    dsq = cnv.find_withtag(nom_rect)
    if len(dsq) != 1:
        raise ValueError("le disque n'est pas seul ou n'existe pas")
    cnv.move(dsq[0], 0        , -0.85*h + 0.095*h*h_dep)
    sleep(0.1)
    cnv.update()
    cnv.move(dsq[0], dplct_mat, 0)
    sleep(0.1)
    cnv.update()
    cnv.move(dsq[0], 0        , 0.85*h - 0.095*h*h_arr)
    sleep(0.05)

def update_disques_fwd(cnv: tk.Canvas, etapes_disques: tuple):
    """effectue le déplacement du disque à suivre pour 
    la résolution des Tours de Hanoi

    Arguments:
        cnv -- Canvas de destination du déplacement
        etapes_disques -- liste de tuples de 3 listes produit par liste_hanoi.construit_deplacement
    """
    verrou.acquire()
    global state
    etape = state+1
    if etape < 2**n:
        suivant = etapes_disques[etape]
        precedent = etapes_disques[etape -1]
        mat_dep = [i for i in range(3) if len(suivant[i]) == len(precedent[i])-1][0]
        mat_arr = [i for i in range(3) if len(suivant[i]) == len(precedent[i])+1][0]
        larg = precedent[mat_dep][-1]
        h_dep = len(suivant[mat_dep])
        h_arr = len(precedent[mat_arr])
        deplacement_disque(cnv, larg, mat_dep, mat_arr, h_dep, h_arr)
        step.set(str(etape))
        entry_step.update()
        state = etape
    verrou.release()
    
def update_disques_fd(cnv: tk.Canvas, etapes_disques: tuple):
    """Fil qui permet l'exécution atomique d'un déplacement de disque vers l'avant

    Arguments:
        cnv -- Canvas de destination du déplacement
        etapes_disques -- liste de tuples de 3 listes des differentes étapes
    """
    th = Thread(name= str(state+1), target=update_disques_fwd, args=[cnv, etapes_disques])
    th.start()

def update_disques_bckwd(cnv: tk.Canvas, etapes_disques: tuple):
    """effectue le déplacement du disque qui précédè pour 
    la résolution des Tours de Hanoi

    Arguments:
        cnv -- Canvas de destination du déplacement
        etapes_disques -- liste de tuples de 3 listes des différentes étapes
    """
    verrou.acquire()
    global state
    etape = state-1
    if etape >= 0:
        suivant = etapes_disques[etape]
        precedent = etapes_disques[etape +1]
        mat_dep = [i for i in range(3) if len(suivant[i]) == len(precedent[i])-1][0]
        mat_arr = [i for i in range(3) if len(suivant[i]) == len(precedent[i])+1][0]
        larg = precedent[mat_dep][-1]
        h_dep = len(suivant[mat_dep])
        h_arr = len(precedent[mat_arr])
        deplacement_disque(cnv, larg, mat_dep, mat_arr, h_dep, h_arr)
        step.set(str(etape))
        entry_step.update()
        state = etape
    verrou.release()
    
def update_disques_bwd(cnv: tk.Canvas, etapes_disques: tuple):
    """Fil qui permet l'exécution atomique d'un déplacement de disque vers l'arrière

    Arguments:
        cnv -- Canvas de destination du déplacement
        etapes_disques -- liste de tuples de 3 listes des différentes étapes
    """
    th = Thread(name= "b"+str(state+1), target=update_disques_bckwd, args=[cnv, etapes_disques])
    th.start()

def transition_disques(cnv: tk.Canvas, etapes_disques: tuple, start: int, end: int):
    """permet la transition de l'étape start à l'étape end

    Arguments:
        cnv -- Canvas de destination du déplacement
        etapes_disques -- liste de tuples de 3 listes des différentes étapes
        start -- rang de l'état initial avant mouvement
        end -- rang de l'état à attendre
    """
    start = max(0, min(2**n-1, start))
    end = max(0, min(2**n-1, end))
    if start < end:
        for etape in range(start+1, end+1):
            update_disques_fd(cnv, etapes_disques)
    elif start > end:
        for etape in range(start-1, end-1, -1):
            update_disques_bwd(cnv, etapes_disques)

# Création des widget et de la fenêtre principale
## Fenêtre principale
root = tk.Tk()
root.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='iconeNSI.png'))
root.geometry(str(l)+"x"+str(h))
root.resizable(width=False, height=False)
root.update()
root.title('Une fenêtre vers Hanoi')

## Widgets
cnv = tk.Canvas(root)
front_btn = tk.Button(root)
back_btn = tk.Button(root)
end_btn = tk.Button(root)
start_btn = tk.Button(root)
step = tk.StringVar()
entry_step = tk.Entry(root, text= step, font='DejaVu 15', width=3, justify="center")
totalstep = f'/ {str(2**n-1)}'
lbl_totalstep = tk.Label(text=totalstep, font='DejaVu 15')
n_choix = tk.DoubleVar(value = 1)
choice_n = tk.Spinbox(root, from_=1, to=9, font='DejaVu 15', width=1, textvariable=n_choix)

# Configuration des widgets
front_btn['text'] = '  ▶  '
back_btn['text'] =  '  ◀  '
start_btn['text'] = ' ┃◀◀ '
end_btn['text'] =   ' ▶▶┃ '
lbl_n = tk.Label(root, text='nb de\ndisques')

cnv["height"]=int(root.geometry()[root.geometry().index('x')+1: root.geometry().index('+')])-40
cnv["width"]=int(root.geometry()[:root.geometry().index('x')])
cnv["background"]="powder blue"
trace_background(cnv)
init_position(cnv, 1)
cnv.update()

# Configuration des commandes
choice_n["command"] = lambda : init_position(cnv, int(choice_n.get()))
choice_n.bind("<Return>", lambda _: init_position(cnv, min(10,int(choice_n.get()))))
back_btn.bind("<Button-1>", lambda _ : update_disques_bwd(cnv, etapes_disques))
front_btn.bind("<Button-1>", lambda _ : update_disques_fd(cnv, etapes_disques))
start_btn.bind("<Button-1>", lambda _ : transition_disques(cnv, etapes_disques, state, 0))
end_btn.bind("<Button-1>", lambda _ : transition_disques(cnv, etapes_disques, state, 2**n-1))
entry_step.bind("<Return>", lambda _ : transition_disques(cnv, etapes_disques, state, int(step.get())))

# Placement des widgets
cnv.grid(column=0, row=0, columnspan=8, sticky="we")
lbl_n.grid(column=0, row=1, sticky="we")
choice_n.grid(column=1, row=1, sticky="we")
start_btn.grid(column=2, row=1, sticky="we")
back_btn.grid(column=3, row=1, sticky="we")
entry_step.grid(column=4, row=1, sticky="we")
lbl_totalstep.grid(column=5, row=1, sticky="we")
front_btn.grid(column=6, row=1, sticky="we")
end_btn.grid(column=7, row=1, sticky="we")

root.mainloop()
