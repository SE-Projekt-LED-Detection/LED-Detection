class BoardChanges:
    def __init__(self, changes_dict):
        self.id = changes_dict["id"]
        self.time = changes_dict["time"]
        self.changes = changes_dict["changes"]


