import datetime
import re


def duration_check(duration_value):
    found = False
    duration_value = duration_value.lower()
    dur = duration_value
    if duration_value.endswith("d"):
        found = True
        try:
            list_of_values = []
            ints = dur.replace("d", '')
            time = datetime.datetime.now().astimezone()
            undo_time = time + datetime.timedelta(days=int(ints))
            list_of_values.append("d")
            list_of_values.append(undo_time)
            if re.search("1d", duration_value):
                list_of_values.append("day")
            elif not re.search("1d", duration_value):
                list_of_values.append("days")
            found = True
            list_of_values.append(ints)
        except Exception as err:
            print(err)
            return ['perm']

        return list_of_values
    elif duration_value.endswith("m"):
        found = True
        try:
            list_of_values = []
            ints = dur.replace("m", '')
            time = datetime.datetime.now().astimezone()
            undo_time = time + datetime.timedelta(minutes=int(ints))
            list_of_values.append("m")
            list_of_values.append(undo_time)
            if re.search("1m", duration_value):
                list_of_values.append("minute")
            elif not re.search("1m", duration_value):
                list_of_values.append("minutes")
            list_of_values.append(ints)


            return list_of_values
        except Exception as err:
            print(err)
            return ['perm']
    if duration_value.endswith("h"):
        found = True
        try:
            list_of_values = []
            ints = dur.replace("h", '')
            time = datetime.datetime.now().astimezone()
            undo_time = time + datetime.timedelta(hours=int(ints))
            list_of_values.append("h")
            list_of_values.append(undo_time)
            if re.search("1h", duration_value):
                list_of_values.append("hour")
            elif not re.search("1h", duration_value):
                list_of_values.append("hours")
            list_of_values.append(ints)
            found = True
            return list_of_values
        except Exception as err:
            print(err)
            return ['perm']
    if found is False:
        print("false")
        found = True
        return ['perm']