import json
import sys

# visita in profondita' per cercare tutti gli item base usati in un craftato
def rec_visit(target, map):
    global items
    global craft
    global tot
    tot = tot + 1 # traccie il numero totale di chiamate alla funzione
    if( items[target]['craftable'] ):
        # se target e' un craftato, richiama la visita su tutti i suoi ingredienti
        for i in craft[target]:
            rec_visit(str(i),map)
    else:
        # target e' un item base, incrementa il contatore relativo nel dict 'map'
        map[target] = map.get(target,0) + 1

# -----------------------------------------------
# fase di caricamento e preparazione dei dati

items_list = json.load(open('lootitems_pretty.json'))['res']
items = {}
# crea una 'mappa' che fa corrispondere un id con tutte le info per l'oggetto relativo
for i in items_list:
    items[str(i['id'])] = i

# nel file di craft, ad ogni id corrisponde la lista dei suoi tre ingredienti
craft = json.load(open('lootcraft_pretty.json'))

target = ' '.join(sys.argv[1:]).lower()
target_i = 0
# cerca l'id dell'oggetto specificato nella riga di comando
for i in items:
    if( items[i]['name'].lower() == target ):
        target_i = i

# -----------------------------------------------
# ricerca vera e propria degli ingredienti base

# 'base' tiene il conto degli ingredienti base necessari
base = {}
tot = 0 # numero di chiamate alla funzione rec_visit
rec_visit(target_i,base)

# stampa il risultato
for key in base:
    qt = base[key]
    name = items[key]['name']
    print(f'{name} x {qt}')

print(f'Totale chiamate alla funzione rec_visit: {tot}')
