import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt

state_table = pd.DataFrame(columns=["led_id", "state", "color", "time", "last_time_off", "last_time_on", "frequency"])


def add_state(led_id,
              state,
              color):
    global state_table

    last_state = get_last_entry(led_id)
    _add_new_led_id(led_id, state, color)
    if last_state is None:
        return
    insert_last_time_state(led_id, state, last_state)

def get_state_table():
    """
    Returns the state table.
    :return:
    """
    global state_table
    return state_table

def insert_last_time_state(led_id, state, last_entry):
    """
    insert the last time entry for the given led_id.
    :param led_id:
    :param state:
    :return:
    """
    global state_table
    inverse_state = "off" if state == "on" else "on"
    column_name = "last_time_" + inverse_state
    if last_entry["state"] is state:
        state_table.loc[led_id, column_name][-1] = last_entry[column_name]
    else:
        state_table.loc[led_id, column_name][-1] = last_entry["time"]


def calculate_frequency(led_id):
    """
    Calculates the frequency of the given led_id.
    :param led_id:
    :return:
    """
    global state_table
    time_series = get_led_time_series(led_id)
    time_series["frequency"] = time_series["time"] - time_series["last_time_on"]
    return time_series["frequency"]


def _add_new_led_id(led_id,
                    state,
                    color):
    """
    adds a new row to the state_table for a new led_id.
    :param led_id:
    :param state:
    :param color:
    :return:
    """
    global state_table
    if (state == "on"):
        state_table = state_table.append(
            {"led_id": led_id, "state": state, "color": color, "time": time.time(), "last_time_off": np.NINF,
             "last_time_on": time.time(), "frequency": 0}, ignore_index=True)
    else:
        state_table = state_table.append(
            {"led_id": led_id, "state": state, "color": color, "time": time.time(), "last_time_off": time.time(),
             "last_time_on": np.NINF, "frequency": 0}, ignore_index=True)


def check_if_led_is_new(led_id):
    """
    Checks if the given led_id is new.
    :param led_id:
    :return:
    """
    global state_table
    return state_table.loc[state_table["led_id"] == led_id].empty


def get_last_entry(led_id):
    """
    Returns the entry.
    :param led_id: is the identifier of the led
    :param state: None if it doesn't matter, otherwise the state
    :return:
    """
    global state_table
    if check_if_led_is_new(led_id):
        return None

    return state_table.loc[state_table["led_id"] == led_id].iloc[-1]


def get_led_time_series(led_id):
    """
    Returns the time series of the given led_id.
    :param led_id:
    :return:
    """
    global state_table
    return state_table.loc[state_table["led_id"] == led_id]

def load_state_table(file_name: str):
    """
    Loads the state table from the given file.
    :param file_name:
    :return:
    """
    global state_table
    with open(file_name, "r") as file:
        new_state_table = pd.read_csv(file)
        # check if the new state table is valid
        assert new_state_table.columns == state_table.columns
        state_table = new_state_table


def save_state_table(file_name: str):
    """
    Saves the state table to the given file.
    :param file_name:
    :return:
    """
    global state_table
    with open(file_name, "w") as file:
        state_table.to_csv(file, index=True)

def get_led_as_time_series(led_id):
    """
    Returns the time series of the given led_id.
    :param led_id:
    :return:
    """
    global state_table
    table = state_table.loc[state_table["led_id"] == led_id]
    table.index = table["time"]
    return table

def plot_led_time_series(led_id):
    """
    Plots the time series of the given led_id.
    :param led_id:
    :return:
    """
    table = get_led_as_time_series(led_id)
    table["state"] = table["state"].map({"on": 1, "off": 0})

    table.plot(x="time", y="state")
    plt.show()


def get_led_ids():
    """
    Returns the led_ids.
    :return:
    """
    global state_table
    return state_table["led_id"].unique()


def plot_all_led_time_series():
    """
    Plots all leds as time series.
    :return:
    """
    for led_id in get_led_ids():
        plot_led_time_series(led_id)