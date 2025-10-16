import sqlite3
import pandas as pd
import duckdb
import requests 
import json
from io import StringIO

def example():
    conn = sqlite3.connect("dataset/Chinook_Sqlite.sqlite")  # połączenie do bazy danych - pliku
    df = pd.read_sql_query("SELECT * FROM Album", conn)
    conn.close()
def example_duckdb():
    conn = duckdb.connect()
    conn.execute("INSTALL sqlite_scanner;")
    conn.execute("LOAD sqlite_scanner;")

    # Attach the SQLite database
    conn.execute("ATTACH 'dataset/Chinook_Sqlite.sqlite' AS chinook_db (TYPE SQLITE);") # połączenie do bazy danych - pliku
    df = conn.execute("SELECT * FROM chinook_db.Album").fetchdf()
    conn.close()

    # Jeśli dane są zawarte np. w kilku plikach csv, można je odczytać bezpośrednio w zapytaniu SQL:
    # conn = duckdb.connect()   
    # df = conn.execute("SELECT * FROM read_csv_auto()'data/*.csv')").fetchdf()

def exercise1():
    conn = sqlite3.connect("dataset/Chinook_Sqlite.sqlite")  # połączenie do bazy danych - pliku
    df = pd.read_sql_query("SELECT  InvoiceId, CustomerId, BillingCity, Total FROM INVOICE WHERE BillingCountry='USA' ORDER BY BillingCity DESC", conn)
    conn.close()
    for index in df.index:
        print(f"invoice:{df['InvoiceId'][index]}, customer:{df['CustomerId'][index]}, city:{df['BillingCity'][index]}, total:{df['Total'][index]}")

def exercise2():
    conn = sqlite3.connect("dataset/Chinook_Sqlite.sqlite")  
    df = pd.read_sql_query("SELECT Album.Title, Artist.Name FROM Artist LEFT JOIN Album ON Album.ArtistId = Artist.ArtistId", conn)
    for index in df.index:
        print(f"album:{df['Title'][index]}, artist:{df['Name'][index]}")
    print (f"Total rows: {len(df)}")
    conn.close()

def exercise3():
    req = requests.get("https://blockchain.info/ticker")  # wysłanie zapytania GET pod odpowiedni adres, zapisanie odpowiedzi
    df = pd.read_json(StringIO(req.text), orient='index')  # odczytanie odpowiedzi jako JSON
    print(df.head())

def exercise4():
    url = "http://150.254.129.33:5000/books"
    data = {
        "title": "Sto lat samotności",
        "author": "Gabriel Garcia Marquez",
        "year": 1981
    }
    response = requests.post(url,json=data)

    print(response)

    response = requests.get(url)

    print(response)

    df = pd.DataFrame(response)

    df.to_csv("dataset/database.csv")


if __name__ == "__main__":
    exercise4()