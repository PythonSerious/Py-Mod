import os, sys
import json
import sqlite3
import time

try:
    os.system(f"{sys.executable} -m pip install -r src/requirements.txt")
except Exception as e:
    print(f"Failed to install requirements. {e}", "red")
    exit(1)


if os.name == "nt":
    clear = "cls"
else:
    clear = "clear"



def intro():
    from termcolor import colored
    if "--run" in sys.argv:
        run()
    os.system(clear)
    print(colored("""
          ____           ____  __           _ 
         |  _ \ _   _   / /  \/  | ___   __| |
         | |_) | | | | / /| |\/| |/ _ \ / _` |
         |  __/| |_| |/ / | |  | | (_) | (_| |
         |_|    \__, /_/  |_|  |_|\___/ \__,_|
                |___/                                             
        """, "yellow"))
    print(colored("Source code written by python#0001 | https://github.com/pythonserious", "blue"))


def launch():
    intro()
    print(
        "Welcome to the Py/Mod launcher. Please select an option below.\n\nr - Run Py/Mod | e - Modify Config | q - Quit Py/Mod\n")
    option = input("Option: ").lower()
    if option == "r":
        run()

    elif option == "e":
        modify_config()

    elif option == "q":
        print("Quitting Py/Mod...")
        sys.exit()


def run():
    intro()
    print("[ CHECKING FOR CONFIG FILE ]")
    if os.path.exists("src/storage/config.json"):
        print("[ CONFIG FILE FOUND ]")
    else:
        with open("src/storage/config.json", "w") as f:
            data = """{"application_id": null}"""
            f.write(data)
        print("[ CONFIG FILE CREATED ]")

    print("[ CHECKING FOR DATABASE(S) ]")

    if not os.path.exists("src/storage/databases/guild.db"):
        print("[ GUILD DATABASE NOT FOUND ]")
        db = sqlite3.connect("src/storage/databases/guild.db")
        cursor = db.cursor()
        cursor.execute(
            """CREATE TABLE guild (prefix TEXT, status TEXT, modlogs TEXT, actionlogs TEXT, modroles TEXT, adminroles TEXT)""")
        cursor.execute("""INSERT INTO guild VALUES (?, ?, ?, ?, ?, ?)""",
                       ("!", "3 0DATA_TYPE_SPLIT0 out for commands!", "", "", "", ""))
        cursor.close()
        db.commit()
        db.close()
        print("[ GUILD DATABASE CREATED ]")
    else:
        print("[ GUILD DATABASE FOUND ]")
    if not os.path.exists("src/storage/databases/bans.db"):
        print("[ BANS DATABASE NOT FOUND ]")
        db = sqlite3.connect("src/storage/databases/bans.db")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE bans (guild_id TEXT, member_id TEXT, unban_time TEXT)""")
        print("[ BANS DATABASE CREATED ]")

    else:
        print("[ BANS DATABASE FOUND ]")

    if not os.path.exists("src/storage/databases/moderations.db"):
        print("[ MODERATIONS DATABASE NOT FOUND ]")
        db = sqlite3.connect("src/storage/databases/moderations.db")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE "moderations" (
        "user"	TEXT,
        "reason"	TEXT,
        "action"	TEXT,
        "moderator"	TEXT,
        "date"	    TEXT,
        "cid"	    TEXT,
        duration    REAL
        );
        """)
        print("[ MODERATIONS DATABASE CREATED ]")
    else:
        print("[ MODERATIONS DATABASE FOUND ]")
    if not os.path.exists("src/storage/databases/tickets.db"):
        print("[ TICKETS DATABASE NOT FOUND ]")
        db = sqlite3.connect("src/storage/databases/tickets.db")
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE "tickets" (
            "user"	TEXT,
            "tid"	TEXT,
            "status"	TEXT,
            "parent"	TEXT,
            "msg"	TEXT
        );""")
        print("[ TICKETS DATABASE CREATED ]")

    else:
        print("[ TICKETS DATABASE FOUND ]")

    print("[ DATABASE(S) CHECKED ]")

    print("[ CHECKING FOR APPLICATION ID ]")
    with open("src/storage/config.json", "r") as f:
        config_json = json.load(f)
    if config_json["application_id"] is None:
        print("[ APPLICATION ID NOT FOUND ]")
        try:
            application_id = int(input("ENTER APPLICATION ID: "))
        except ValueError:
            print("INVALID APPLICATION ID.")
            exit(1)
        config_json["application_id"] = application_id
        with open("src/storage/config.json", "w") as f:
            json.dump(config_json, f, indent=4)
        print("[ APPLICATION ID SET ]")
    else:
        print("[ APPLICATION ID FOUND ]")
        print(config_json["application_id"])
        application_id = config_json["application_id"]
    try:
        int(application_id)
    except ValueError:
        print("INVALID APPLICATION ID.")
        exit(1)

    print("[ CHECKING FOR TOKEN ]")
    with open("src/storage/config.json", "r") as f:
        config_json = json.load(f)
    if config_json["token"] is None:
        print("[ TOKEN NOT FOUND ]")
        token = input("ENTER TOKEN: ")
        config_json["token"] = token
        with open("src/storage/config.json", "w") as f:
            json.dump(config_json, f, indent=4)
        print("[ TOKEN SET ]")
        from termcolor import colored
        print(colored(f"!!! PLEASE ENSURE TO TURN ON INTENTS https://discord.com/developers/applications/{application_id}/bot !!!", "red"))
    else:
        print("[ TOKEN FOUND ]")

    print("[ PRE-START CHECKS COMPLETE ]")
    time.sleep(5)
    intro()
    print(f"\nApplication ID: {application_id}\nRunning on Python {sys.version.split(' ')[0]}")
    print("------------------")
    from src.bot import start

    start(application_id)


def modify_config():
    intro()
    print("What would you like to edit?\n\n1 - Token\n2 - Application ID\n3 - Return to main menu\n")
    option = input("Option: ")
    if option == "1":
        with open("src/storage/config.json", "r") as f:
            config_json = json.load(f)
        if config_json["token"] is None:
            print("[ NO TOKEN FOUND ]")
        else:
            print("[ TOKEN FOUND ]")
        token = input("ENTER NEW TOKEN: ")
        config_json["token"] = token
        with open("src/storage/config.json", "w") as f:
            json.dump(config_json, f, indent=4)
        print("[ TOKEN SET ]")
        time.sleep(2)
        return modify_config()
    elif option == "2":
        with open("src/storage/config.json", "r") as f:
            config_json = json.load(f)
        if config_json["application_id"] is None:
            print("[ NO APPLICATION ID FOUND ]")
        else:
            print("[ APPLICATION ID FOUND ]")
        token = input("ENTER NEW APPLICATION ID: ")
        config_json["application_id"] = token
        with open("src/storage/config.json", "w") as f:
            json.dump(config_json, f, indent=4)
        print("[ APPLICATION ID SET ]")
        time.sleep(2)
        return modify_config()
    elif option == "3":
        return launch()


if __name__ == "__main__":
    launch()
