from pyrogram import Client, Filters, Emoji, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import PeerIdInvalid

import requests
import re
import time
import json



app = Client(
    "Contrabbandiere",
    bot_token="831534591:AAGudiof9r07WD8FBH_QvYRTEInIKP9R91s"
)


token = "8JQplLaSFlLYy8pL11690"

PrezzoRarità={
	"C":{
		"scrigno":1200
	},
	"NC":{
		"prezzo":2000,
		"scrigno":2400
	},
	"R":{
		"prezzo":3000,
		"scrigno":4800
	},
	"UR":{
		"prezzo":5000,
		"scrigno":7200
	},
	"L":{
		"prezzo":7500,
		"scrigno":14000
	},
	"E":{
		"prezzo":10000,
		"scrigno":30000
	},
	"UE":{
		"prezzo":100000
	},
	"U":{
		"prezzo":250000
	},
	"X":{
		"prezzo":1000000
	}
}


# visita in profondita' per cercare tutti gli item base usati in un craftato
def rec_visit(target, map):
    global items
    global craft
    global prezzoOgg
    global prezzoScrigno
    rarità=items[target]['rarity']
    if(items[target]['craftable']):
        prezzoOgg=prezzoOgg+PrezzoRarità[rarità]["prezzo"]
        # se target e' un craftato, richiama la visita su tutti i suoi ingredienti
        for i in craft[target]:
            rec_visit(str(i), map)
    else:
        # target e' un item base, incrementa il contatore relativo nel dict 'map'
        map[target] = map.get(target, 0) + 1
        prezzoScrigno=prezzoScrigno+PrezzoRarità[rarità]["scrigno"]



def QuantitàOgg(oggetto):
    # -----------------------------------------------
    # fase di caricamento e preparazione dei dati
    global items
    global craft
    global prezzoOgg
    global prezzoScrigno
    items_list = json.load(open('lootitems_pretty.json'))['res']
    items = {}
    # crea una 'mappa' che fa corrispondere un id con tutte le info per l'oggetto relativo
    for i in items_list:
        items[str(i['id'])] = i

    # nel file di craft, ad ogni id corrisponde la lista dei suoi tre ingredienti
    craft = json.load(open('lootcraft_pretty.json'))

    target_i = 0
    # cerca l'id dell'oggetto specificato nella riga di comando
    for i in items:
        if(items[i]['name'].lower() == oggetto.lower()):
            target_i = i

    # -----------------------------------------------
    # ricerca vera e propria degli ingredienti base

    # 'base' tiene il conto degli ingredienti base necessari
    base = {}
    prezzoOgg=0
    prezzoScrigno=0
    rec_visit(target_i, base)
    quantitàOgg = ""
    # stampa il risultato
    for key in base:
        qt = base[key]
        name = items[key]['name']
        quantitàOgg = quantitàOgg+f'{name} x {qt}\n'

    return quantitàOgg

@app.on_message(Filters.command(["start"]))
def MessaggioContrabbandiere(client, message):
	app.send_message(message.chat.id,"Bot a solo utilizzo del team **Lootor** per gestire le offerte del vicolo")

@app.on_message(Filters.forwarded)
def MessaggioContrabbandiere(client, message):
    utente = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    username = message.from_user.username
    messaggio = message.text
    messaggio = messaggio.split("\n")
    rx = r'(.+) \(\w+\) al prezzo di ([\d\.]+)'
    for lines in messaggio:
        mo = re.match(rx, lines)
        if mo:
            global prezzoScrigno
            global prezzoOgg
            oggetto = mo.group(1)
            QuantitàOgg(oggetto)
            prezzo = int(mo.group(2).replace(".", ""))
            r = requests.get(
                f'http://fenixweb.net:3300/api/v2/{token}/items/{oggetto}')
            r = r.json()['res']
            if type(r) is list:
                for i in r:
                    if i['name'] == oggetto:
                        PC = i['craft_pnt']
            else:
                PC = r['craft_pnt']

            prezzoOfferta = int(prezzo - (prezzo * 0.1))
            OggScrigno = prezzoScrigno + prezzoOgg
            prezzoGuadagno = prezzoOfferta - OggScrigno

            prezzoOffertaTmp = '{0:,}'.format(prezzoOfferta)
            prezzoGuadagno = '{0:,}'.format(prezzoGuadagno)
            OggScrigno = '{0:,}'.format(OggScrigno)
            prezzoOgg = '{0:,}'.format(prezzoOgg)
            prezzoScrigno = '{0:,}'.format(prezzoScrigno)

            OggScrigno = OggScrigno.replace(",", ".")
            prezzoOgg = prezzoOgg.replace(",", ".")
            prezzoScrigno = prezzoScrigno.replace(",", ".")
            prezzoGuadagno = prezzoGuadagno.replace(",", ".")
            prezzoOffertaTmp = prezzoOffertaTmp.replace(",", ".")

            msgEdit = message.reply("Attendi...")

            MessaggioOffri = app.send_message(message.chat.id,f'/offri {oggetto},{prezzoOfferta},{username}').message_id
            MessaggioNegozio= app.send_message(message.chat.id,f'/negozio {oggetto}:{prezzoOfferta}:1').message_id

            messageId=f'{message.message_id}!{MessaggioOffri}!{MessaggioNegozio}'


            try:
                msg = f'{utente} `@{message.from_user.username}`\n\n**Costo Vendita (-10%):** {prezzoOffertaTmp}\n**Costo Craft ({PC} PC):** {prezzoOgg}§\n**Costo Craft+Scrigni ({PC} PC):** {OggScrigno}§\n**Guadagno:** {prezzoGuadagno}§\n\n**Craft:** `Crea {oggetto}`'
            except UnboundLocalError:
                PC = "Sconosciuti"
                msg = f'{utente} `@{message.from_user.username}`\n\n**Costo Vendita (-10%):** {prezzoOffertaTmp}\n**Costo Craft ({PC} PC)*:* {prezzoOgg}§\n**Costo Craft+Scrigni ({PC} PC):** {OggScrigno}§\n**Guadagno:** {prezzoGuadagno}§\n\n**Craft:** `Crea {oggetto}`'

            msgEdit.edit(
                msg,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [  # First row
                            InlineKeyboardButton(  # Generates a callback query when pressed
                                "Mi Prenoto",
                                # Note how callback_data must be bytes
                                callback_data=f"Prenoto|{message.from_user.username}|{messageId}"
                            ),
                            InlineKeyboardButton(  # Generates a callback query when pressed
                                "Concludi Richiesta",
                                # Note how callback_data must be bytes
                                callback_data=f"Concludi|{message.from_user.username}|{messageId}"
                            )
                        ]

                    ]
                )
            )


@app.on_callback_query()
def TastieraInline(client, callback_query):
    if "Prenoto" in callback_query.data:
        utenteOfferta = callback_query.data.split("|")[1]
        messageId = callback_query.data.split("|")[2]
        time.sleep(0.1)
        message = callback_query.message
        utente = f"[{callback_query.from_user.first_name}](tg://user?id={callback_query.from_user.id})"
        msg = f'{message.text.markdown}\n\n**Utente prenotato:** {utente}'
        message.edit(
            msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [  # First row
                        InlineKeyboardButton(  # Generates a callback query when pressed
                            "Rinuncia",
                            # Note how callback_data must be bytes
                            callback_data=f"Rinuncia|{callback_query.from_user.username}|{messageId}|{utenteOfferta}"
                        ),
                        InlineKeyboardButton(  # Generates a callback query when pressed
                            "Concludi Richiesta",
                            # Note how callback_data must be bytes
                            callback_data=f"Concludi|{utenteOfferta}|{messageId}"
                        )
                    ]
                ]
            )
        )


    if "Rinuncia" in callback_query.data:
        time.sleep(0.1)
        utente = callback_query.data.split("|")[1]
        messageId = callback_query.data.split("|")[2]
        utenteOfferta = callback_query.data.split("|")[3]
        print(callback_query.data)
        if utente == callback_query.from_user.username:
            message = callback_query.message
            msgTmp = message.text.split("\n")
            msg = message.text.markdown.split("\n")
            rx = r'Utente prenotato: .+'
            for lines in msgTmp:
                mo = re.match(rx, lines)
                if mo:
                    i = msgTmp.index(lines)

            del msg[i]
            msg = "\n".join(msg)

            message.edit(
                msg,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [  # First row
                            InlineKeyboardButton(  # Generates a callback query when pressed
                                "Mi Prenoto",
                                callback_data=f"Prenoto|{utenteOfferta}|{messageId}"  # Note how callback_data must be bytes
                            ),
                            InlineKeyboardButton(  # Generates a callback query when pressed
                                "Concludi Richiesta",
                                # Note how callback_data must be bytes
                                callback_data=f"Concludi|{utenteOfferta}|{messageId}"
                            )
                        ]
                    ]
                )
            )

            message.reply(f"[{callback_query.from_user.first_name}](tg://user?id={callback_query.from_user.id}) ha rinunciato l'offerta")

        else:
            callback_query.answer("Non la hai prenotata tu!")

    if "Concludi" in callback_query.data:
        print(callback_query.data)
        utente = callback_query.data.split("|")[1]
        messageId = callback_query.data.split("|")[2]
        messageId = messageId.split("!")
        print(messageId)
        messageId = [int(i) for i in messageId]	

        time.sleep(0.1)
        message = callback_query.message
        if callback_query.from_user.username == utente:
            message.edit(message.text.markdown + "\n\nOfferta chiusa "+Emoji.CROSS_MARK)
            message.delete()
            for i in messageId:
            	app.delete_messages(message.chat.id,i)

            callback_query.answer("Offerta chiusa, ho cancellato i messaggi!")
        else:
            callback_query.answer("Non puoi chiudere le offerte degli altri!")

app.run()
