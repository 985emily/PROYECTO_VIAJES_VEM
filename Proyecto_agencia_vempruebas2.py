#LIBRERIAS
from bs4 import BeautifulSoup
import requests
import pandas as pd
import logging
from random import randrange, choice
import random
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

# Habilitar el registro
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
# Definiciones de los estados para la conversación de alto nivel
SELECTING_ACTION, GUAYAQUIL, QUITO, DESCRIBING_G = map(chr, range(4))
# Definiciones para un subrango de la conversacion
SELECTING_LEVEL, SELECTING_LEVELW = map(chr, range(4, 6))
# Deficiciones para la descripion
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# Definicones de metodos
STOPPING, SHOWING = map(chr, range(8, 10))
S = map(chr, range(1,5))
# Un alto de las acciones
END = ConversationHandler.END
# Different constants for this example
(QUITUS, CHILDREN, GUAYAQUILS, GENDER, A1, A2, TIPO, LLOS, START_OVER, FEATURES,
 CURRENT_FEATURE, CURRENT_LEVEL) = map(chr, range(10, 22))
de= list()

#scrapin de una página con ciertos parametros
def button(llos,Tvuelo):
    if llos == "salidas":
        page = requests.get("https://www.aeropuertoquito.aero/es/vuelos-"+Tvuelo+"/salidas-"+Tvuelo+".html")
        soup = BeautifulSoup(page.content, 'html.parser')
    else:
        page = requests.get("https://www.aeropuertoquito.aero/es/vuelos-" + Tvuelo + "/llegadas-" + Tvuelo + ".html")
        soup = BeautifulSoup(page.content, 'html.parser')

    hora = soup.find_all('td', class_='td1 hora')
    ho = list()
    for i in hora:
        ho.append(i.text)
    print(ho)
    print(len(ho))
    aerolinea = soup.find_all('td', attrs={'class': 'td2'})
    aer = list()
    for i in aerolinea:
              aer.append(i.text)
    print(aer)
    print(len(aer))
    vuelo = soup.find_all('td', attrs={'class': 'td3'})
    vue = list()
    for i in vuelo:
           vue.append(i.text)
    print(vue)
    print(len(vue))
    destino = soup.find_all('td', class_='td4')
    dest = list()
    for i in destino:
        dest.append(i.text)
    print(dest)
    print(len(dest))
    dia = soup.find_all('td', class_='td5')
    dias = list()
    for i in dia:
        dias.append(i.text)
    print(dias)
    print(len(dias))
    df = pd.DataFrame({"Hora": ho, "Aerolinea": aer, "Vuelo": vue, "Destino": dest, "Disponibilidad": dias})
    print(df)
    for i in range(len(dias)):
        de.extend([[aer[i], dest[i], vue[i] , dias[i], ho[i] ]])
    print(de)

# Helper
def _name_switcher(level):
    if level == GUAYAQUILS:
        return (' ', ' ')

# CONVERSACION INICIADA
def start(update, context):
    text = 'PRESIONE EL BOTÓN DE MOSTRAR VUELOS. ' \
           '\n\n Si usted desea para esta acción -> /stop.'
    buttons = [[InlineKeyboardButton(text='Aeropuerto José Joaquín de Olmedo', callback_data=str(GUAYAQUIL))], [
        InlineKeyboardButton(text='Aeropuerto Mariscal Sucre', callback_data=str(QUITO))],
        [InlineKeyboardButton(text='MOSTRAR VUELOS', callback_data=str(SHOWING)), InlineKeyboardButton(text='FIN', callback_data=str(END))] ]
    keyboard = InlineKeyboardMarkup(buttons)
    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text('Hola, bienvenido/a a  Agencia de viajes VEM, este bot es una nueva modalidad a implementar en la agencia con el fin de interactuar más con nuestra clientela; para que sea lo más eficiente este bot elija primero el AEROPUERTO, caso contrario se mostraran TODOS los vuelos de los aeropuertos establecidos' \
                                '\n\n SIGA LAS INTRUCCIONES PARA ASEGURAR LA EFICIENCIA DEL PROGRAMA')
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION
#QUITO
def adding_self(update, context):
    context.user_data[CURRENT_LEVEL] = QUITUS
    text = 'Okay, presione el boton.'
    button = InlineKeyboardButton(text='Ingreso de datos', callback_data=str(A1))
    keyboard = InlineKeyboardMarkup.from_button(button)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return DESCRIBING_G

#mostrar los datos sacados
def show_data(update, context):
    def prettyprint(user_data, level):
        people = user_data.get(level)
        if not people:
            return '\nNo se ha ingresado datos, se  mostrara todos los vuelos disponibles'
        text = ''
        if level == QUITUS:
            for person in user_data[level]:
                text += '\nTIPO: {}, \n VUELO: {}'.format(person.get(LLOS, '-'), person.get(TIPO, '-'))
                text2 = "{}".format(person.get(LLOS))
                text3= "{}".format(person.get(TIPO))

                if (text2 == "nacionales" or  text2 == "Nacionales"):
                    if (text3=="llegada" or text3 == "Llegada"):
                        button("llegadas","nacionales")
                    else:
                        button("salidas", "nacionales")
                else:
                    if text3=="Llegada" or text3 == "llegada":
                        button("llegadas", "internacionales")
                    else:
                        button("salidas", "internacionales")
        else:

            male, female = _name_switcher(level)

            for person in user_data[level]:
                gender = female if person[GENDER] == A2 else male
                text += '\n{}: TIPO: {}, VUELO DE: {}'.format(gender, person.get(LLOS, '-'),
                                                        person.get(TIPO, '-'))

        return text
    ud = context.user_data
    text = 'Aeropuerto Mariscal Sucre: ' + prettyprint(ud, QUITUS)
    text += '\n\n Aeropuerto José Joaquín de Olmedo: ' + prettyprint(ud, GUAYAQUILS)
    buttons = [[
        InlineKeyboardButton(text='Confirmar Datos', callback_data=str(S)),
        InlineKeyboardButton(text='Regresar', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    ud[START_OVER] = True
    return SHOWING

#SE PRESENTA UN MENSAJE PARA COMENZAR POR COMANDOS
def listavie(update, context):
    update.callback_query.edit_message_text(text="Para reservar un vuelo en el areopuerto escogido -> /vuelo \n\n PARA VISUALIZAR TODOS-> /tvuelos")
    return S

#ES COGE EL NUMERO DE VUELO
def l (update, context):
    c = 0
    for i in range(len(de)):
       update.message.reply_text(text=de[i], callback_data=i)
       c = i
    update.message.reply_text("ESCRIBA UN NÚMERO DEL 0 AL {} PARA ESCOGER EL VUELO ".format(c))

#TODOS LOS VUELOS DEL SISTEMA
def todosvuelos(update,context):
    page = requests.get("https://www.aeropuertoquito.aero/es/vuelos-nacionales/llegadas-nacionales.html")
    page2 = requests.get("https://www.aeropuertoquito.aero/es/vuelos-nacionales/salidas-nacionales.html")
    page3 = requests.get("https://www.aeropuertoquito.aero/es/vuelos-internacionales/llegadas-internacionales.html")
    page4 = requests.get("https://www.aeropuertoquito.aero/es/vuelos-internacionales/salidas-internacionales.html")
    soup = BeautifulSoup(page.content, 'html.parser')
    soup2 = BeautifulSoup(page2.content, 'html.parser')
    soup3 = BeautifulSoup(page3.content, 'html.parser')
    soup4 = BeautifulSoup(page4.content, 'html.parser')
    hora = soup.find_all('td', class_='td1 hora') +  soup2.find_all('td', class_='td1 hora') + soup3.find_all('td', class_='td1 hora') + soup4.find_all('td', class_='td1 hora')
    ho = list()
    for i in hora:
        ho.append(i.text)
    print(ho)
    print(len(ho))
    aerolinea = soup.find_all('td', attrs={'class': 'td2'}) + soup2.find_all('td',
                                                                             attrs={'class': 'td2'}) + soup3.find_all(
        'td', attrs={'class': 'td2'}) + soup4.find_all('td', attrs={'class': 'td2'})

    aer = list()
    for i in aerolinea:
        if (len(aer) < len(ho)):
            aer.append(i.text)
    print(aer)
    print(len(aer))
    vuelo = soup.find_all('td', attrs={'class': 'td3'}) + soup2.find_all('td', attrs={'class': 'td3'}) + soup3.find_all(
        'td', attrs={'class': 'td3'}) + soup4.find_all('td', attrs={'class': 'td3'})
    vue = list()
    for i in vuelo:
        if (len(vue) < len(aer)):
            vue.append(i.text)
    print(vue)
    print(len(vue))
    destino = soup.find_all('td', class_='td4') + soup2.find_all('td', class_='td4') + soup3.find_all('td',
                                                                                                      class_='td4') + soup4.find_all(
        'td', class_='td4')
    dest = list()
    for i in destino:
        dest.append(i.text)
    print(dest)
    print(len(dest))
    dias = list()
    dia = soup.find_all('td', class_='td5') + soup2.find_all('td', class_='td5') + soup3.find_all('td',
                                                                                                  class_='td5') + soup4.find_all(
        'td', class_='td5')
    for i in dia:
        dias.append(i.text)
    print(dias)
    print(len(dias))
    df = pd.DataFrame({"Hora": ho, "Aerolinea": aer, "Vuelo": vue, "Destino": dest, "Disponibilidad": dias})
    print(df)
    for i in range(len(dias)):
        de.extend([[aer[i], dest[i], vue[i] , dias[i], ho[i] ]])
    print(de)
    c=1
    update.message.reply_text("ESCRIBA UN NÚMERO DEL 0 AL {} PARA ESCOGER EL VUELO ".format(c))

#ESGOGE CUAL QUE PROCESO PRESENTAR
def listaviee(update, context):
    text = update.message.text
    d = int(text)
    destino = list()
    for i in range(len(de)):
             if i == d:
                destino.append(de[i])
    update.message.reply_text("¿Es su viaje de \n ida y vuelta = Ida y vuelta \n  o  \n solo de ida = Ida? \n Escriba respectivamente")



#
def select_q(update, context):
    context.user_data[CURRENT_LEVEL] = GUAYAQUILS
    text = 'Okay, presione el botón.'
    button = InlineKeyboardButton(text='Ingrese a hacia donde esta dirigido', callback_data=str(A1))
    keyboard = InlineKeyboardMarkup.from_button(button)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    return SELECTING_LEVELW


def end_second_level(update, context):
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    start(update, context)
    return END


def stop(update, context):
    update.message.reply_text('Okay, bye.')
    return END

#METODO PARA TERMINAR
def end(update, context):
    update.callback_query.answer()
    text = 'Nos vemos'
    update.callback_query.edit_message_text(text=text)
    return END

#PARA SELCCIONAR LAS CARACTERISTICAS
def select_feature(update, context):
    buttons = [[InlineKeyboardButton(text='¿Nacional o Internacional?', callback_data=str(LLOS))],
         [InlineKeyboardButton(text='LISTO', callback_data=str(END))]]
    keyboard = InlineKeyboardMarkup(buttons)
    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {GENDER: update.callback_query.data}
        text = 'Siga las instruciones: \n\n Presione el botón'\
            '\n\n Escriba: "Nacionales"  o "Internacionales" respectivamente '
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:

        text = '¡Lo tengo! Presione el botón \n\n Escriba: "Llegada" en caso que desee viajar hacia el lugar escogido o "Salida" en caso que desee viajar desde el lugar escogido\n\n\t SI, USTES YA REALIZO ESTE PRESIONE EL BOTÓN DE  "LISTO".'
        buttons = [[InlineKeyboardButton(text='¿Llegada o salida?', callback_data=str(TIPO))],
                   [InlineKeyboardButton(text='LISTO', callback_data=str(END))]]
        keyboard = InlineKeyboardMarkup(buttons)
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE

#preguntapra repetir la accion
def ask_for_input(update, context):
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    text = 'Escriba según lo explicado anteriormente:'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    return TYPING

def save_input(update, context):
    #GUARDA LOS DATOS
    ud = context.user_data
    ud[FEATURES][ud[CURRENT_FEATURE]] = update.message.text
    ud[START_OVER] = True
    return select_feature(update, context)

#termina la accion de pra volver
def end_describing(update, context):
    ud = context.user_data
    level = ud[CURRENT_LEVEL]
    if not ud.get(level):
        ud[level] = []
    ud[level].append(ud[FEATURES])
    if level == QUITUS:
        ud[START_OVER] = True
        start(update, context)
    else:
        context.user_data[START_OVER] = True
        start(update, context)
    return END

#corta la accion directament
def stop_nested(update, context):
    update.message.reply_text('Okay, Cuidate.')
    return STOPPING

#llama a todos lo metodos
def main():
    updater = Updater("1331458519:AAHVlBlXmZ7lDfj0gUDFry2UQnMor_xp34M", use_context=True)
    dp = updater.dispatcher
    description_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_feature,
                                           pattern='^' + str(A1) + '$|^' + str(A2) + '$')],
        states={
            SELECTING_FEATURE: [CallbackQueryHandler(ask_for_input,
                                                     pattern='^(?!' + str(END) + ').*$')],
            S: [CallbackQueryHandler(end_describing, pattern='^' + str(S))],

            TYPING: [MessageHandler(Filters.text & ~Filters.command, save_input)],
        },

        fallbacks=[
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested), CommandHandler("vuelo",l)
        ],

        map_to_parent={
            END: SELECTING_LEVEL,
            STOPPING: STOPPING,
        }
    )
    add_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_q,
                                           pattern='^' + str(GUAYAQUIL) + '$')],

        states={
                        SELECTING_LEVELW: [description_conv]
        },

        fallbacks=[
            CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
            CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            SHOWING: SHOWING,
            END: SELECTING_ACTION,
            STOPPING: END,
        }
    )

    selection_bac = [
        CallbackQueryHandler(listavie, pattern='^' + str(S)),
        CallbackQueryHandler(start, pattern='^' + str(END) + '$'),
    ]
    selection_handlers = [
        add_conv,
        CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
        CallbackQueryHandler(adding_self, pattern='^' + str(QUITO) + '$'),
        CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SHOWING: selection_bac,
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            DESCRIBING_G: [description_conv],
            STOPPING: [CommandHandler('start', start)],
        },

        fallbacks=[CommandHandler('stop', stop)  ],

    )
    #comandos
    dp.add_handler(CommandHandler("vuelo", l))
    dp.add_handler(MessageHandler(Filters.regex("^(1|0|2|3|4|5|6|7|8|9|10|11|12|11|13|14|15|17|18|19|20|21|22|21|23|24|25|27|28|29|30|31|32|31|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|50)$"), listaviee))
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()