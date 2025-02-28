from msg.groups import MagneticSpaceGroupData

from importlib import resources

with resources.open_text("msg.data", "database.json") as file:
    data = file.read()

database = MagneticSpaceGroupData.model_validate_json(data)

