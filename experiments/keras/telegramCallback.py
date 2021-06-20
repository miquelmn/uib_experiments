# -*- coding: utf-8 -*-
""" Callbacks to send keras results to telegram bot.

"""
from datetime import datetime
import time

import telegram_send
from tensorflow import keras


class TelegramCallback(keras.callbacks.Callback):

    def on_train_begin(self, logs=None):
        start_date = datetime.today().strftime('%d/%m/%Y %H:%M:%S')
        messages = [f"Train started at {start_date}"]

        telegram_send.send(messages=messages)

    def on_train_end(self, logs=None):
        end_date = datetime.today().strftime('%d/%m/%Y %H:%M:%S')
        messages = [f"Train finished at {end_date}"]

        telegram_send.send(messages=messages)

    def on_epoch_begin(self, batch, logs=None):
        self.epoch_time_start = time.time()

    def on_epoch_end(self, epoch, logs=None):
        duration = time.time() - self.epoch_time_start

        messages = [f"The average loss for epoch {epoch} is {logs['loss']}",
                    f"The train lasts {duration} seconds"]

        telegram_send.send(messages=messages)
