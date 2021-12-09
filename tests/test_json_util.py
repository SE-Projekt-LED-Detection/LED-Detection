
import json
def test_from_json():
    f = open("./resources/model.json", "r")

    json_str = f.read()


    dict = json.load(json_str)
    pass

