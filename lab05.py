import duckdb

def main():
    # 1.Wczytaj dane ze wszystkich plików do pojedynczej tablicy
    conn = duckdb.connect()
    df = conn.execute("SELECT * from read_csv('dataset/names/*.txt', header=false, columns={'name': 'VARCHAR', 'gender': 'VARCHAR', 'count': 'INTEGER'})").fetch_df()
    # df jest teraz DataFrame Pandas

    # 2. Określ liczbę unikalnych imion
    unique_names_count = df['name'].nunique()
    print(f"Liczba unikalnych imion: {unique_names_count}")

    # 3. Określ liczbę unikalych imion  zostało nadanych w tym czasie rozróżniając imiona męskie i żeńskie.
    unique_male_names_count = df[df['gender'] == 'M']['name'].nunique()
    unique_female_names_count = df[df['gender'] == 'F']['name'].nunique()
    print(f"Liczba unikalnych imion męskich: {unique_male_names_count}")
    print(f"Liczba unikalnych imion żeńskich: {unique_female_names_count}")
    print(f"Suma kontrolna: {unique_female_names_count + unique_male_names_count}")

    # 4. Stwórz nowe kolumny frequency male i frequency female
    df['frequency_male'] = 


if __name__ == "__main__":
        main()