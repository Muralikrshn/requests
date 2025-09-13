from fastapi import FastAPI
import uvicorn
import pandas as pd
import csv
# import psycopg2 as pg

# DB connection
# connection = pg.connect(
#     dbname="inspections_db",
#     user="postgres",
#     password="postgres",
#     host="localhost",
#     port="5433"
# )
# cursor = connection.cursor()

app = FastAPI()

df = pd.read_csv('dtc-lease.csv')


@app.get("/")
def read_root():
    return {"message": "Hello World"}

# @app.get("/{name}")
# def get_data(name: str):
#     return {"message": f"Hello {name}"}

@app.get("/cars")
def get_cars():
    data = []
    with open("dtc-lease.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)  # keep values as strings
    return {"cars": data}


# @app.get("/users/{name}")
# def get_user(name: str):
#     create_table_query = '''
#       CREATE TABLE IF NOT EXISTS employees (
#           id SERIAL PRIMARY KEY,
#           name VARCHAR(100) NOT NULL,
#           role VARCHAR(50),
#           salary DECIMAL(10, 2)
#       );
#     '''
#     cursor.execute(create_table_query)
#     connection.commit()
#     return {"message": f"User {name} created"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
