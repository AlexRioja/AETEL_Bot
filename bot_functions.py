"""
The different dispatchers for the bot are located in this file
"""
from random import randint
import config
import helpers
import json

def start(bot, update, text=""):
    """/start->Starts the bot by sending a message to the chat.

    Args:
        bot (TelegramBot): bot
        update (TelegramUpdater): updater
        text (str): Message to send. Overwrites the message stored in settings.
    """
    if text =="":
        text=config.start_msg
    bot.send_message(chat_id=update.message.chat_id, text=text)

def help(bot, update, text=""):
    """/help->Sends a help message when asked

    Args:
        bot (TelegramBot): bot
        update (TelegramUpdater): updater
        text (str): Message to send. Overwrites the message stored in settings.
    """
    #bot.sendMessage(update.message.chat_id, text, parse_mode=telegram.ParseMode.MARKDOWN)
    if text =="":
        text=config.help_msg
    bot.sendMessage(update.message.chat_id, text)

def deleteMessage(bot, job):
    """Deletes the message that is passed in the "job" arg

    Args:
        bot (TelegramBot): bot
        job (TelegramJob): job containing the message to delete
    """
    bot.delete_message(job.context.chat_id, message_id=job.context.message_id)

def openDoorRequest(bot, update, job_queue, chat_data):
    """Opens the AETEL door by sending an specific
       mqtt message to the door controller.

    Args:
        bot (TelegramBot): bot
        update (TelegramUpdater): updater
        job_queue (TelegramJobQueue): JobQueue to be able to execute "deleteMessage" job after 2 sec
        chat_data (TelegramChatData): Telegram chat data
    """
    if update.message.chat_id == config.aetel_chat_id:
        job = job_queue.run_once(deleteMessage, 2, context=update.message)
        chat_data['job'] = job
        helpers.open_door()
    else:
        bot.sendMessage(chat_id=update.message.chat_id, text="Este comando solo se puede usar en el grupo de AETEL, no me seas pillín...")
        
def new_member(bot, update, job_queue, chat_data):
    """Sends the welcome picture whenever a new user enters the group.
       Also sets a job to delete that picture after 240 minutes.

    Args:
        bot (TelegramBot): bot
        update (TelegramUpdater): updater
        job_queue (TelegramJobQueue): JobQueue to be able to execute "deleteMessage" job after 14400 sec
        chat_data (TelegramChatData): Telegram chat data
    """
    for member in update.message.new_chat_members:
        update.message.reply_photo(photo=open(config.images + '/welcome.jpg', 'rb'))
        job = job_queue.run_once(deleteMessage, 14400, context=update.message)
        chat_data['job'] = job

def send_nepe(bot, update):
    """Sends nepe picture to the group. It also checks if the user has enough nepe points to send it

    Args:
        bot (TelegramBot): bot
        update (TelegramUpdater): updater
    """
    if helpers.cooldown(1):
        with open('inside_variables.json', 'r') as json_file:
            inside_variables=json.load("inside_variables.json")
        """
        Here we need to find the user that is asking, then search in the inside_variables if 
        the user has "tickets" for sending nepe, if yes, send and reduce ticket. If not, inform the user and 
        return to the main execution normally.
        """
        update_json=json.dumps(update)
        usernameTelegram=update_json["_effective_message"]["from"]["username"]
        msg_id=update_json['message']['message_id']
        for k,v in inside_variables["nepe_points"]:
            if k == usernameTelegram:
                if v<=0:
                    rand=randint(5)
                    if rand==0:
                        bot.sendMessage("¿Dónde están tus nepePoints compañero?", reply_to_message_id=msg_id)
                    if rand==1:
                        bot.sendMessage("Ejem...No tickets no juego...", reply_to_message_id=msg_id)
                    if rand==2:
                        bot.sendMessage("Te has portado mal y te ha tocado carbón...", reply_to_message_id=msg_id)
                    if rand==3:
                        bot.sendMessage("¿Y tus nepePoints?", reply_to_message_id=msg_id)
                    if rand==4:
                        bot.sendMessage("No tan rápido camarada... Necesitas nepePoints para eso...", reply_to_message_id=msg_id)
                    if rand==5:
                        bot.sendMessage("No te voy a dar el placer, pero me has caido bien, te digo: nepe", reply_to_message_id=msg_id)
                else:
                    inside_variables['nepe_points'][usernameTelegram]=v-1
                    bot.sendSticker(update.message.chat_id, "https://i.ibb.co/th3L8cw/Aetel-logo.webp")#send nepe
        with open("inside_variables.json", "w") as jsonFile:
            json.dump(inside_variables, jsonFile)

def checkNepePoints(bot, update):
    """Checks the nepePoints of the user who is asking for it.
        If user is not found in the list, no answer is made.

    Args:
        bot (TelegramBot): bot
        update (TelegramUpdater): updater
    """
    with open('inside_variables.json', 'r') as json_file:
        inside_variables=json.load("inside_variables.json")
    update_json=json.dumps(update)
    usernameTelegram=update_json["_effective_message"]["from"]["username"]
    for k,v in inside_variables["nepe_points"]:
            if k == usernameTelegram:
                bot.sendMessage("Tus puntos nepe son: ("+str(v)+") !!")
            else: #Ask administrators to add you to the list
                pass
    