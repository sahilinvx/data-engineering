import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5433"),
        user=os.getenv("PGUSER", "de_student"),
        password=os.getenv("PGPASSWORD", "de_student_pw"),
        dbname=os.getenv("PGDATABASE", "week4"),
    )
