import os

import BSP.UrlBoardLoader


def test_load_board():
    """
    Downloads an valid config file from github, unzips it and if successful deletes all directories again
    """
    test_url = "https://github.com/SE-Projekt-LED-Detection/LED-Detection/raw/7b105b37c7d97f256fde8be933bfa5a55988f2b9/tests/resources/ZCU102/reference/ref.zip"
    path = os.path.dirname(os.path.abspath(__file__))
    board = BSP.UrlBoardLoader.load_board_from_url(path, test_url)

    resources_path = os.path.join(path, "boards")
    config_file = os.path.join(resources_path, "ref", "ref.json")
    config_image = os.path.join(resources_path, "ref", "ref.jpg")

    assert os.path.exists(config_file)
    assert len(board.led) > 0

    # Cleanup
    os.remove(config_file)
    os.remove(config_image)
    os.rmdir(os.path.join(resources_path, "ref"))
    os.rmdir(resources_path)


