import json

with open("src/storage/config.json", "r") as f:
    json_data = json.load(f)
    webhook = json_data["webhook"]
    token = json_data["token"]

non_slash_prefix = "!"
debug = True