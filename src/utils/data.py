# SQLITE HANDLER #
import sqlite3
import os
import sys
from typing import Union

import src.utils.logger as logger


def write(table, data) -> None:
    db = sqlite3.connect(f"src/storage/databases/{table}.db")
    cursor = db.cursor()
    qs = []
    for item in data:
        qs.append("?")
    qs = ", ".join(qs)
    cursor.execute(f"INSERT INTO {table} VALUES ({qs})", data)
    cursor.close()
    db.commit()
    db.close()
    logger.log(f"database {table} has been written to.", logger.logtypes.debug)


def count(table):
    db = sqlite3.connect(f"src/storage/databases/{table}.db")
    cursor = db.cursor()
    cursor.execute(f"select * from {table}")
    results = cursor.fetchall()
    return len(results)


def read(table, data=None, case=None, all=False) -> Union[list, str]:
    db = sqlite3.connect(f"src/storage/databases/{table}.db")
    cursor = db.cursor()
    if data is None:
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()
    elif data is not None and all is True:
        cursor.execute(f"SELECT * FROM {table} WHERE {case} = '{data}'")
        data = cursor.fetchall()

    else:
        cursor.execute(f"SELECT * FROM {table} WHERE {case} = '{data}'")
        data = cursor.fetchone()
    cursor.close()
    db.close()
    logger.log(f"database {table} has been read from.", logger.logtypes.debug)

    return data


def delete(table, case, data) -> None:
    db = sqlite3.connect(f"src/storage/databases/{table}.db")
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE {case} = '{data}'")
    cursor.close()
    db.commit()
    db.close()
    logger.log(f"database {table} has had data deleted.", logger.logtypes.debug)


def update(table, data, new_data, case, case_value, safe=True) -> None:
    db = sqlite3.connect(f"src/storage/databases/{table}.db")
    cursor = db.cursor()
    if safe:
        cursor.execute(f"UPDATE {table} SET ({data}) = ({new_data}) WHERE '{case}' = '{case_value}'")
    else:
        cursor.execute(f"UPDATE {table} SET {data} = {new_data} WHERE {case} = {case_value}")

    cursor.close()
    db.commit()
    db.close()
    logger.log(f"database {table} has had data updated.", logger.logtypes.debug)


def update_all(table, data, new_data) -> None:
    db = sqlite3.connect(f"src/storage/databases/{table}.db")
    cursor = db.cursor()
    cursor.execute(f"UPDATE {table} SET {data} = {new_data}")
    db.commit()
    cursor.close()
    db.close()
    logger.log(f"database {table} has had data updated.", logger.logtypes.debug)


def exists(table, data, case) -> bool:
    db = sqlite3.connect(f"src/storage/databases/{table}.db")
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {table} WHERE {case} = '{data}'")
    data = cursor.fetchone()
    cursor.close()
    db.close()
    logger.log(f"database {table} has been data checked.", logger.logtypes.debug)
    return data is not None
