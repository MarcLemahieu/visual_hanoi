def init_hanoi(n:int)->tuple:
    return ([i for i in range(n, 0, -1)],[],[])

def construit_deplacement(n:int, first:bool =True, lst= None, start:int = 0, end:int = 2):
    if first:
        l1, l2, l3 = init_hanoi(n)
        lst = []
        lst.append((l1, l2, l3))
    if n > 0 :
        intermediaire = 3 - (start+ end)
        construit_deplacement(n-1, False, lst, start, intermediaire)
        mats = tuple([lst[-1][i].copy() for i in range(3)])
        mats[end].append(mats[start].pop())
        lst.append(mats)
        construit_deplacement(n-1, False, lst, intermediaire, end)
    return lst

if __name__ == '__main__':
    n = 5
    etapes = construit_deplacement(n)
    for t in etapes:
        print(f"{t[0]}{(3*n+(4 if len(t[0]) else 2)-3*len(t[0]))*' '}{t[1]}{(3*n+(4 if len(t[1]) else 2)-3*len(t[1]))*' '}{t[2]}")
        
