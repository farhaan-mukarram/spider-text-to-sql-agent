import sqlite3

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
    if table_name not in ALLOW_LIST:
        raise ValueError(f"Table '{table_name}' is not in the allow list")

    path = f"{DATABASE_ROOT_DIR}/{table_name}/{table_name}.sqlite"
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    return con


@tool
def query_table(table: str, query: str) -> str:
    """Connect to table using guarded connection, run query, and return stringified results."""
    result = None
    try:
        con = guarded_connect(table)
        cur = con.cursor()
        cur.execute(query)
        rows = cur.fetchall()

        result = str(rows)
        pass
    except Exception as e:
        result = f"Error: {e}"
    return result


@tool
def list_tables() -> str:
    """List all tables in allow list with their columns and subtables."""
    output = ["Database Tables and Columns:", "=" * 50]

    for table in ALLOW_LIST:
        try:
            con = guarded_connect(table)
            cur = con.cursor()

            # Find subtables
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            subtables = [st[0] for st in cur.fetchall()]

            if subtables:
                # Parent table columns
                cur.execute(f"PRAGMA table_info({table})")
                parent_cols = [col[1] for col in cur.fetchall()]
                output.append(f"\n{table} (Parent): {', '.join(parent_cols)}")
                output.append("  Subtables:")
                for idx, st in enumerate(subtables):
                    cur.execute(f"PRAGMA table_info({st})")
                    cols = [col[1] for col in cur.fetchall()]
                    output.append(f"    {idx + 1}. {st}: {', '.join(cols)}")
            else:
                # No subtables
                cur.execute(f"PRAGMA table_info({table})")
                cols = [col[1] for col in cur.fetchall()]
                output.append(f"\n{table}: {', '.join(cols)}")

            con.close()
        except Exception as e:
            output.append(f"\n{table}: Error - {e!s}")

    return "\n".join(output)


tools = [list_tables, query_table]
