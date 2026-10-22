import sqlite3
from typing import Any

from langchain.tools import tool

ALLOW_LIST = [
    "battle_death",
    "car_1",
    "concert_singer",
    "course_teach",
    "cre_Doc_Template_Mgt",
    "dog_kennels",
    "employee_hire_evaluation",
    "flight_2",
    "museum_visit",
    "network_1",
    "orchestra",
    "pets_1",
    "poker_player",
    "real_estate_properties",
    "singer",
    "student_transcripts_tracking",
    "tvshow",
    "voter_1",
    "world_1",
    "wta_1",
]

DATABASE_ROOT_DIR = "./data/database"


def guarded_connect(table_name: str):
    """Connect to database after validating table name against allow list."""

    assert table_name in ALLOW_LIST

    path = f"{DATABASE_ROOT_DIR}/{table_name}/{table_name}.sqlite"
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    return con


def query_table(table: str, query: str) -> list[Any]:
    """Input to this tool is a table and a SQL query, output is a result from the database.
    If the query is not correct, an error message will be returned."""
    result = None
    try:
        con = guarded_connect(table)
        cur = con.cursor()
        cur.execute(query)
        rows = cur.fetchall()

        result = rows
    except Exception:
        result = []
    return result


@tool
def list_tables(table: str) -> str:
    """Input to the tool is the database name, output is a list of tables with columns in the database."""
    db_info = []

    try:
        con = guarded_connect(table)
        cur = con.cursor()

        # Find tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]

        res = []
        for idx, tab in enumerate(tables):
            result = f"{idx + 1}. {tab}, "
            cols = [
                cols[1] for cols in cur.execute(f"PRAGMA table_info({tab});").fetchall()
            ]
            result += f"COLUMNS = {', '.join(cols)}"
            res.append(result)

        result = f"DATABASE {table}, TABLES:\n" + "\n".join(res) + "\n"
        db_info.append(result)
        con.close()

    except Exception as e:
        db_info.append(f"\n{table}: Error - {e}")

    return "\n".join(db_info)


tools = [list_tables]
