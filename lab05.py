import duckdb
import pandas as pd

class Projekt1:
    def __init__(self):
        self.df = pd.DataFrame()

    def wczytaj_dane_SSA(self):
        '''1.Wczytaj dane ze wszystkich plików do pojedynczej tablicy'''
        conn = duckdb.connect()
        self.df = conn.execute("SELECT * from read_csv('dataset/names/*.txt', header=false, " \
        "columns={'name': 'VARCHAR', 'gender': 'VARCHAR', 'count': 'INTEGER'}, filename=True)").fetch_df() # df jest teraz DataFrame Pandas
        # Ustawiamy filename=True, aby uzyskać rok w którym zostały zebrane dane

        # Wyciągnij rok z nazwy pliku (np. yob2023.txt -> 2023)
        self.df['year'] = self.df['filename'].str.extract(r'yob(\d{4})\.txt')[0].astype(int)
    
        # Usuń kolumnę filename
        self.df = self.df.drop('filename', axis=1)
    
    def wczytaj_dane_pl(self):
        '''11. Wczytaj zestaw danych zawierający liczbę nadawanych imion w okresie 2000-2024 w Polsce'''
        pass

    def liczba_unikalnych_imion(self):
        '''2. Określ liczbę unikalnych imion'''
        unique_names_count = self.df['name'].nunique()
        return unique_names_count

    def liczba_unikalnych_imion_gender(self):
        '''3. Określ liczbę unikalalych imion rozróżniając imiona męskie i żeńskie'''
        unique_male_names_count = self.df[self.df['gender'] == 'M']['name'].nunique()
        unique_female_names_count = self.df[self.df['gender'] == 'F']['name'].nunique()
        return unique_male_names_count, unique_female_names_count

if __name__ == "__main__":
        projekt1 = Projekt1()
        projekt1.wczytaj_dane_SSA()
        unique_names_count = projekt1.liczba_unikalnych_imion()
        print(f"Rozwiązanie zadania 2. Liczba unikalnych imion nadanych w USA w latach 1880-2024: {unique_names_count}")
        unique_male_names_count, unique_female_names_count = projekt1.liczba_unikalnych_imion_gender()
        print(f"Rozwiązanie zadania 3. Liczba unikalnych imion męskich: {unique_male_names_count}, żeńskich: {unique_female_names_count}")
