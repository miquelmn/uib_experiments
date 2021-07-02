# -*- coding: utf-8 -*-
""" Callback to send keras results to telegram bot.

This module defines a keras callback to send status messages through a telegram bot.
"""
from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np
import time

import telegram_send
from tensorflow import keras


class TelegramCallback(keras.callbacks.Callback):

    def __init__(self, show_plot=False, *args, **kwargs):
        self.__show_plot = show_plot
        self.__epoch_time_start = None

        super().__init__(*args, **kwargs)

    def on_train_begin(self, logs=None):
        """ Executes on the beginning of the train.

        Args:
            logs:

        Returns:

        """
        start_date = datetime.today().strftime('%d/%m/%Y %H:%M:%S')

        messages = [f"Train started at {start_date}"]

        telegram_send.send(messages=messages)

    def on_train_end(self, logs=None):
        end_date = datetime.today().strftime('%d/%m/%Y %H:%M:%S')
        messages = [f"Train finished at {end_date}"]

        plot = None
        if self.__show_plot:
            plot = TelegramCallback.__build_history_plot(logs=logs)

        telegram_send.send(messages=messages, images=plot)

    @staticmethod
    def __build_history_plot(logs=None):
        """ Returns a numpy array with the plot of loss functions.

        Args:
            logs:

        Returns:

        """

        data = None
        if logs is not None:
            # Make a random plot...
            fig = plt.figure()
            ax1 = fig.add_subplot(121)
            ax2 = fig.add_subplot(122)

            ax1.plot(logs['categorical_accuracy'])
            ax1.plot(logs['val_categorical_accuracy'])
            ax1.title.set_text('Model accuracy')
            ax1.set_ylabel('accuracy')
            ax1.set_xlabel('epoch')
            ax1.legend(['train', 'validation'], loc='upper left')

            # "Loss"
            ax2.plot(logs['loss'])
            ax2.plot(logs['val_loss'])
            ax2.title.set_text('Model loss')
            ax2.set_ylabel('loss')
            ax2.set_xlabel('epoch')
            ax2.legend(['train', 'validation'], loc='upper left')

            fig.canvas.draw()

            data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
            data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        return data

    def on_epoch_begin(self, batch, logs=None):
        self.__epoch_time_start = time.time()

    def on_epoch_end(self, epoch, logs=None):
        duration = time.time() - self.__epoch_time_start
        duration = round(duration, 2)

        messages = [f"The average loss for epoch {epoch} is {logs['loss']} \n "
                    f"the training of the epoch has last {duration} seconds"]

        telegram_send.send(messages=messages)
