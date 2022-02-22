import logging
import paho.mqtt.publish as publish
import config
from telegram.ext import BaseFilter
from datetime import datetime, timedelta
import json

class Logger:
    """
    It will log everything that happens with the bot.
    Including access to AETEL.
    """
    def __init__(self):
        pass

class SettingsLoader:
    """
    It will load the settings for the bot, like the token or chat id.
    It will read it from the config.py file! make sure it exists!
    """
    def __init__(self):
        pass

def open_door():
    """
    It will send an mqtt message to the door controller to open.
    """
    publish.single("cmnd/PUERTA/POWER", "1", hostname = config.door_mqtt_host, auth = config.door_mqtt_auth)

def cooldown(cooldown):
    """Sets a cooldown to not overflow the chat with stickers

    Args:
        cooldown (int): Cooldown time in minutes

    Returns:
        boolean: True/False if cooldown has finished/not
    """
    now = datetime.now()
    cooldown_time = timedelta(minutes=cooldown)
    with open('inside_variables.json') as json_file:
        inside_variables=json.load("inside_variables.json")

    result=False
    if inside_variables["last_time_nepe_called"]==0:
        inside_variables['last_time_nepe_called']=now
        result=True
    else:
        if datetime.now()>inside_variables['last_time_nepe_called'] + cooldown_time:
            inside_variables['last_time_nepe_called']=now
            result=True
        else:
            result=False
    with open('json_data.json', 'w') as outfile:
        json.dump(inside_variables, outfile)

    return result


class FilterByContainingNepe(BaseFilter):
    """Class to filter a message if contains an specific string ("nepe").
       Need to call the filter method to work.

    Args:
        BaseFilter : Telegram Filter base class
    """
    def filter(self, message):
        """Returns True/False if "nepe" is contained in the "message".

        Args:
            message (str): message that the user has typed
        Returns:
            boolean: True of False depending if the word is found or not
        """
        lower_message = str(message.text).lower()
        if "nepe" in lower_message:
            return True
        else:
            return False



class FilterByContainingText(BaseFilter):
    """Class to filter a message if contains an specific string.
       Need to call the filter method to work.

    Args:
        BaseFilter : Telegram Filter base class
    """
    def filter(self, message, word2find="nepe"):
        """Returns {word2find:True/False} if "word2find" is contained in the "message".

        Args:
            message (str): message that the user has typed
            word2find (str, optional): Word to be find in the messaage. Defaults to "nepe".

        Returns:
            boolean: True of False depending if the word is found or not
        """
        lower_message = str(message.text).lower()
        if word2find in lower_message:
            return {word2find:True}
        else:
            return {word2find:False}
