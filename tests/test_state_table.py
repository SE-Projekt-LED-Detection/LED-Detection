from BSP.state_handler.state_table import *
import time

def test_init_state_table():
    table = load_state_table("resources/example_log.csv")
    led_ids = table["led_id"].unique()
    assert np.all(led_ids == ["LED_1", "LED_2", "LED_3"])

def test_insert():
    timestamp = time.time_ns()
    insert_state_entry("LED_1", "off", "red", timestamp)
    last_entry = get_last_entry("LED_1")
    assert timestamp == last_entry["time"]


def test_plot():
    load_state_table("resources/example_log.csv")
    plot_all_led_time_series()

def test_insert_in_new():
    timestamp = time.time_ns()
    insert_state_entry("LED_1", "on", "red", timestamp)
    assert np.all(get_led_ids() == "LED_1")
    insert_state_entry("LED_1", "off", "green", timestamp+1)
    entry = get_last_entry("LED_1")
    assert entry["last_time_on"] == timestamp