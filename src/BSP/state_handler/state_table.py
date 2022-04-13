import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt

state_table = pd.DataFrame(columns=["led_id", "state", "color", "time", "last_time_off", "last_time_on", "frequency"])


def insert_state_entry(led_id:str,
                       state:str,
                       color:str,
                       timestamp=None):
    """
    insert a new row to the state_table
    :param led_id: is the name of the LED type: str
    :param state: the current state. Can be "on" or "off"
    :param color: the color as str
    :param timestamp: the timestamp or None if time.time() should be used.
    :return:
    """
    global state_table

    last_state = get_last_entry(led_id)
    entry = _add_new_led_id(led_id, state, color, timestamp)
    if last_state is not None:
        entry = insert_last_time_state(entry, last_state)
    state_table = state_table.append(entry, ignore_index=True)



def get_state_table():
    """
    Returns the state table.
    :return:
    """
    global state_table
    return state_table


def insert_last_time_state(current_entry, last_entry):
    """
    insert the last time entry for the given led_id.
    :param led_id:
    :param state:
    :return:
    """

    inverse_state = "off" if current_entry["state"] == "on" else "on"
    column_name = "last_time_" + inverse_state
    if current_entry["state"] is last_entry["state"]:
        current_entry[column_name] = last_entry[column_name]
    else:
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
    adds a new row to the state_table for a new led_id.
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
        assert np.all(new_state_table.columns==state_table.columns)
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
    #table["time"] = pd.to_datetime(table["time"])
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
    Returns the last detected state of all leds
    :return:
    """
    global state_table
    assert not state_table.empty # check if the state table is empty
    last_time = state_table["time"].iloc[-1]
    return state_table.loc[state_table["time"] == last_time]

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
    global state_table
    led_ids = get_led_ids()
    fig, axs = plt.subplots(len(led_ids))
    for id, val in enumerate(led_ids):
        table = get_led_as_time_series(val)
        table["state"] = table["state"].map({"on": 1, "off": 0})
        axs[id].step(table.index, table["state"], where="post")
        axs[id].set_title(val)
        axs[id].set_ylim([-0.3,1.3])

    plt.show()

