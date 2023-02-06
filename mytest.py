import logging
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ConversationHandler
import bitget.spot.order_api as order

BOT_TOKEN = ""

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Costanti per le fasi della conversazione
INSERT_DATA, API_KEY, SECRET_KEY, PASSPHRASE = range(4)
TICKER, QUANTITY, PRICE = range(4, 7)
TICKER_PAC, QUANTITY_PAC, PRICE_PAC, INTERVALLO_PAC = range(7, 11)


async def start(update, context):
    await update.message.reply_text("Benvenuto! Scegli un'opzione: \n- /insert_data per inserire le API Key \n"
                                    "- /show_data per visualizzare i dati salvati\n"
                                    "- /purchase to start buy crypto\n"
                                    "- /set_pac to start PAC\n"
                                    "- /stop_pac to stop PAC")
    return INSERT_DATA


async def insert_data(update, context):
    await update.message.reply_text("Inserisci la API_KEY:")
    return API_KEY


async def api_key(update, context):
    context.user_data['API_KEY'] = update.message.text
    await update.message.reply_text("Inserisci la SECRET_KEY:")
    return SECRET_KEY


async def secret_key(update, context):
    context.user_data['SECRET_KEY'] = update.message.text
    await update.message.reply_text("Inserisci la PASSHPRASE:")
    return PASSPHRASE


async def passphrase(update, context):
    context.user_data['PASSPHRASE'] = update.message.text
    await update.message.reply_text("Grazie!")
    await update.message.reply_text("Digita /start per tornare al menù iniziale!")
    return ConversationHandler.END


async def show_data(update, context):
    try:
        API_KEY2 = context.user_data['API_KEY']
        SECRET_KEY2 = context.user_data['SECRET_KEY']
        PASSPHRASE2 = context.user_data['PASSPHRASE']
        await update.message.reply_text("API_KEY: {} \nSECRET_KEY: {} \nPASSPHRASE: {}".format(API_KEY2, SECRET_KEY2,
                                                                                               PASSPHRASE2))
        await update.message.reply_text("Digita /start per tornare al menù iniziale!")
    except KeyError:
        await update.message.reply_text("Non hai ancora inserito nessun dato")
        await update.message.reply_text("Digita /start per tornare al menù iniziale!")


async def purchase(update, context):
    if 'API_KEY' in context.user_data and 'SECRET_KEY' in context.user_data and 'PASSPHRASE' in context.user_data:
        await update.message.reply_text("Inserisci il ticker che desideri acquistare:")
        return TICKER
    else:
        await update.message.reply_text("Devi prima inserire i dati relativi alle API!")
        await update.message.reply_text("Digita /start per tornare al menù iniziale!")


async def ticker(update, context):
    context.user_data['TICKER'] = update.message.text
    await update.message.reply_text("Inserisci la quantità da acquistare:")
    return QUANTITY


async def quantity(update, context):
    context.user_data['QUANTITY'] = update.message.text
    await update.message.reply_text("Inserisci il prezzo limite:")
    return PRICE


async def price(update, context):
    context.user_data['PRICE'] = update.message.text
    await update.message.reply_text("Acquisto in corso...")
    API_KEY2 = context.user_data['API_KEY']
    SECRET_KEY2 = context.user_data['SECRET_KEY']
    PASSPHRASE2 = context.user_data['PASSPHRASE']
    SYMBOL2 = context.user_data['TICKER']
    QUANTITY2 = context.user_data['QUANTITY']
    PRICE2 = context.user_data['PRICE']
    orderApi = order.OrderApi(API_KEY2, SECRET_KEY2, PASSPHRASE2, use_server_time=False, first=False)
    result = orderApi.orders(symbol=SYMBOL2, price=PRICE2, quantity=QUANTITY2, side='buy', orderType='limit',
                             force='normal')
    await update.message.reply_text(result)
    await update.message.reply_text("Digita /start per tornare al menù iniziale!")
    return ConversationHandler.END


async def set_pac(update, context):
    if 'API_KEY' in context.user_data and 'SECRET_KEY' in context.user_data and 'PASSPHRASE' in context.user_data:
        await update.message.reply_text("Inserisci l'intervallo di tempo in cui ripetere l'acquisto (sec):")
        return INTERVALLO_PAC
    else:
        await update.message.reply_text("Devi prima inserire i dati relativi alle API!")
        await update.message.reply_text("Digita /start per tornare al menù iniziale!")


async def interval_pac(update, context):
    context.user_data['INTERVAL_PAC'] = update.message.text
    await update.message.reply_text("Inserisci il ticker che desideri acquistare:")
    return TICKER_PAC


async def ticker_pac(update, context):
    context.user_data['TICKER_PAC'] = update.message.text
    await update.message.reply_text("Inserisci la quantità da acquistare:")
    return QUANTITY_PAC


async def quantity_pac(update, context):
    context.user_data['QUANTITY_PAC'] = update.message.text
    await update.message.reply_text("Inserisci il prezzo limite:")
    return PRICE_PAC


async def price_pac(update, context):
    context.user_data['PRICE_PAC'] = update.message.text
    await update.message.reply_text("PAC avviato con successo!")
    context.job_queue.run_repeating(callback=pac, interval=int(context.user_data['INTERVAL_PAC']),
                                    data=context.user_data, chat_id=update.effective_message.chat_id,
                                    name="PAC")
    return ConversationHandler.END


async def pac(context):
    job = context.job
    '''
    API_KEY2 = job.data['API_KEY']
    SECRET_KEY2 = job.data['SECRET_KEY']
    PASSPHRASE2 = job.data['PASSPHRASE']
    SYMBOL2 = job.data['TICKER_PAC']
    QUANTITY2 = job.data['QUANTITY_PAC']
    PRICE2 = job.data['PRICE_PAC']
    orderApi = order.OrderApi(API_KEY2, SECRET_KEY2, PASSPHRASE2, use_server_time=False, first=False)
    result = orderApi.orders(symbol=SYMBOL2, price=PRICE2, quantity=QUANTITY2, side='buy', orderType='limit',
                             force='normal')
    await context.bot.send_message(job.chat_id, text=result)
    '''
    await context.bot.send_message(job.chat_id, text="Digita /start per tornare al menù iniziale!")
    return ConversationHandler.END


async def stop_pac(update, context):
    jobs = context.job_queue.get_jobs_by_name("PAC")
    if not jobs:
        await update.message.reply_text("Non è ancora stato attivato un PAC!")
        await update.message.reply_text("Digita /start per tornare al menù iniziale!")
    else:
        for job in jobs:
            job.schedule_removal()
        await update.message.reply_text("PAC disattivato con successo!")
        await update.message.reply_text("Digita /start per tornare al menù iniziale!")


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            INSERT_DATA: [CommandHandler('insert_data', insert_data)],
            API_KEY: [MessageHandler(filters.TEXT, api_key)],
            SECRET_KEY: [MessageHandler(filters.TEXT, secret_key)],
            PASSPHRASE: [MessageHandler(filters.TEXT, passphrase)]
        },
        fallbacks=[CommandHandler('start', start)],
    )

    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('purchase', purchase)],
        states={
            TICKER: [MessageHandler(filters.TEXT, ticker)],
            QUANTITY: [MessageHandler(filters.TEXT, quantity)],
            PRICE: [MessageHandler(filters.TEXT, price)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    conv_handler3 = ConversationHandler(
        entry_points=[CommandHandler('set_pac', set_pac)],
        states={
            INTERVALLO_PAC: [MessageHandler(filters.TEXT, interval_pac)],
            TICKER_PAC: [MessageHandler(filters.TEXT, ticker_pac)],
            QUANTITY_PAC: [MessageHandler(filters.TEXT, quantity_pac)],
            PRICE_PAC: [MessageHandler(filters.TEXT, price_pac)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    showdata_handler = CommandHandler('show_data', show_data)
    stop_pac_handler = CommandHandler('stop_pac', stop_pac)

    application.add_handler(conv_handler)
    application.add_handler(showdata_handler)
    application.add_handler(conv_handler2)
    application.add_handler(conv_handler3)
    application.add_handler(stop_pac_handler)

    application.run_polling()
