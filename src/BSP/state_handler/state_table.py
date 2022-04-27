import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)  # Ignore the warning of the dataframe append

import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
from threading import Lock

state_table = pd.DataFrame(columns=["led_id", "state", "color", "time", "last_time_off", "last_time_on", "frequency"])


def insert_state_entry(led_id: str,
                       state: str,
                       color: str,
                       timestamp=None):
    """
    Insert a new row to the state_table

    :param led_id: is the name of the LED type: str
    :param state: the current state. Can be "on" or "off"
    :param color: the color as str
    :param timestamp: the timestamp or None if time.time() should be used.
    :return: The created entry
    """
    global state_table
    with Lock():
        last_state = get_last_entry(led_id)
        entry = _add_new_led_id(led_id, state, color, timestamp)
        if last_state is not None:
            entry = insert_last_time_state(entry, last_state)
        state_table = state_table.append(entry, ignore_index=True)
        return entry


def get_state_table():
    """
    Returns an copy of the state table.

    :return:
    """
    global state_table
    return state_table.copy()


def insert_frequency(current_entry, last_entry, inverse_state):
    if inverse_state == "off":
        frequence = calc_frequency(current_time=current_entry["time"], last_time_on=last_entry["last_time_on"])
    else:
        frequence = last_entry["frequency"]
    current_entry["frequency"] = frequence


def calc_frequency(current_time, last_time_on):
    return 1 / np.sqrt((current_time - last_time_on) ** 2)


def insert_last_time_state(current_entry, last_entry):
    """
    Insert the last time entry for the given led_id.

    :param led_id:
    :param state:
    :return:
    """

    inverse_state = "off" if current_entry["state"] == "on" else "on"
    column_name = "last_time_" + inverse_state
    if current_entry["state"] is last_entry["state"]:
        current_entry[column_name] = last_entry[column_name]
    else:
        insert_frequency(current_entry, last_entry, inverse_state)
        current_entry[column_name] = last_entry["time"]
    return current_entry


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
                    color,
                    timestamp=None):
    """
    Adds a new row to the state_table for a new led_id.

    :param led_id: is the name of the led
    :param state: is the current state and can be "on" or "off"
    :param color: is the color given as str
    :param timestamp: the current timestamp or None if time.time() should be used.
    :return:
    """
    global state_table
    time_now = timestamp if timestamp is not None else time.time()
    if (state == "on"):
        return pd.Series({"led_id": led_id, "state": state, "color": color, "time": time_now, "last_time_off": np.NINF,
                          "last_time_on": time_now, "frequency": 0})

    else:
        return pd.Series({"led_id": led_id, "state": state, "color": color, "time": time_now, "last_time_off": time_now,
                          "last_time_on": np.NINF, "frequency": 0})


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
    :return: the state table
    """
    global state_table
    with open(file_name, "r") as file:
        new_state_table = pd.read_csv(file, delimiter=";")
        # check if the new state table is valid
        assert np.all(new_state_table.columns == state_table.columns)
        state_table = new_state_table
    return state_table


def save_state_table(file_name: str):
    """
    Saves the state table to the given file.

    :param file_name:
    :return:
    """
    global state_table
    with open(file_name, "w") as file:
        state_table.to_csv(file, index=True)


def get_led_as_time_series(led_id: str):
    """
    Returns the time series of the given led_id.

    :param led_id:
    :return:
    """
    global state_table
    table = state_table.loc[state_table["led_id"] == led_id]
    # table["time"] = pd.to_datetime(table["time"])
    table = table.set_index("time")

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


def get_current_state():
    """
    Returns the last detected state of all leds.

    :return:
    """
    global state_table
    assert not state_table.empty  # check if the state table is empty
    last_time = state_table["time"].iloc[-1]
    return state_table.loc[state_table["time"] == last_time]


def get_led_ids():
    """
    Returns the led_ids.

    :return:
    """
    global state_table
    return state_table["led_id"].unique()


def clear_state_table():
    global state_table
    state_table.drop(state_table.index, inplace=True)

