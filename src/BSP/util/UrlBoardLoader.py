import os
import zipfile
import wget
import BDG.utils.json_util as jsutil
from BDG.model.board_model import Board


def load_board_from_url(config_folder: str, url: str) -> Board:
    resources_path = os.path.join(config_folder, "boards")

    if not os.path.exists(resources_path):
        os.mkdir(resources_path)

    file_name = wget.download(url, out=resources_path)
    file_name_without_extension = os.path.splitext(os.path.basename(file_name))[0]

    if not zipfile.is_zipfile(file_name):
        raise Exception("Downloaded file is not a zip file. Please use the zip file generated by the BDG.")

    board_dir_path = os.path.join(resources_path, file_name_without_extension)

    if os.path.exists(board_dir_path):
        os.remove(file_name)
        raise Exception(f"A board config with the name %s already exists." % file_name_without_extension)

    os.mkdir(board_dir_path)

    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(board_dir_path)

    os.remove(file_name)

    config_path = os.path.join(resources_path, file_name_without_extension, file_name_without_extension + ".json")
    return jsutil.from_json(file_path=config_path)




