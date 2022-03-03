

COD_USCITA = 0
GS = {COD_USCITA: "uscire", 1: "quadrata", 2: "rettangolare", 3: "circolare"}
GS2 = {}
for key,v in GS.items(): GS2[v] = key
    

def input_numerico(messaggio):
    while True:
        val_str = input(messaggio)
        try:
            val = int(val_str)
            return val
        except:
            print("{} non e' un valore numerico, ripetere inserimento\n".format(val_str))

    
gs_prompt = "inserire geometria sezione\n{} per {}\n{} per {}\n{} per {}\n{} per {}\n".format(
    1, GS[1], 2,GS[2], 3,GS[3], 0, GS[0])

gs = -1
while gs not in range(0,3+1):
    gs = input_numerico(gs_prompt)
    if gs == 0:
        print("inserito {} esco".format(gs))
        exit(0)
    
distanza_appoggio = input_numerico("inserire distanza appoggio: ")
forza = input_numerico("inserire forza: ")
summary = "\ninseriti:\ngeometria: {}\ndistanza appoggio: {}\nforza {}".format(GS[gs], distanza_appoggio, forza)

momento_flettente = (distanza_appoggio*forza)/4
print("risultato intermedio, momento flettente: {}".format(momento_flettente))

# specifiche non chiare, uso variabile generica valore in attesa di chiarificazione
if gs == GS2["quadrata"]:
    base = input_numerico("inserire il lato della sezione quadrata: ")
    summary += "\nbase: {}".format(base)
    valore = base**3/6
elif gs == GS2["rettangolare"]:
    base = input_numerico("inserire la base della sezione rettangolare: ")
    summary += "\nbase: {}".format(base)
    altezza = input_numerico("inserire l'altezza della sezione rettangolare: ")
    summary += "\naltezza: {}".format(altezza)
    valore = base*altezza**2/6
elif gs == GS2["circolare"]:
    diametro = input_numerico("inserire il diametro della sezione circolare: ")
    summary += "\ndiametro: {}".format(diametro)
    valore = 0.1*diametro**3
else:
    print("valore illegale di geometria sezione {} esco".format(gs))

wf = valore # non sicuro data incertezza interpretazione specifiche
print("risultato intermedio, wf: {}".format(wf))

rfm = momento_flettente/wf

print(summary+"\n\ngeometria {} rfm e': {}".format(GS[gs], rfm))