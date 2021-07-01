# -*- coding: utf-8 -*-
""" Callbacks to send keras results to telegram bot.

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
        super.__init__(*args, **kwargs)

    def on_train_begin(self, logs=None):
        start_date = datetime.today().strftime('%d/%m/%Y %H:%M:%S')

        messages = [f"Train started at {start_date}"]

        telegram_send.send(messages=messages)

    def on_train_end(self, logs=None):
        end_date = datetime.today().strftime('%d/%m/%Y %H:%M:%S')
        messages = [f"Train started finished at {end_date}"]

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
            ax1.title('Model accuracy')
            ax1.ylabel('accuracy')
            ax1.xlabel('epoch')
            ax1.legend(['train', 'validation'], loc='upper left')

            # "Loss"
            ax2.plot(logs['loss'])
            ax2.plot(logs['val_loss'])
            ax2.title('Model loss')
            ax2.ylabel('loss')
            ax2.xlabel('epoch')
            ax2.legend(['train', 'validation'], loc='upper left')

            # If we haven't already shown or saved the plot, then we need to
            # draw the figure first...
            fig.canvas.draw()

            # Now we can save it to a numpy array.
            data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
            data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

        return data

    def on_epoch_begin(self, batch, logs=None):
        self.epoch_time_start = time.time()

    def on_epoch_end(self, epoch, logs=None):
        duration = time.time() - self.epoch_time_start

        messages = [f"The average loss for epoch {epoch} is {logs['loss']}",
                    f"The train lasts {duration} seconds"]

        telegram_send.send(messages=messages)
