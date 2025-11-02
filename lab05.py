import duckdb
import pandas as pd
import pandasgui
import numpy as np
import matplotlib.pyplot as plt

class Projekt1:
    def __init__(self):
        self.df = pd.DataFrame()
        self.male_1000_names_descending = pd.DataFrame()
        self.female_1000_names_descending = pd.DataFrame()

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
        '''3. Określ liczbę unikalnych imion rozróżniając imiona męskie i żeńskie'''
        unique_male_names_count = self.df[self.df['gender'] == 'M']['name'].nunique()
        unique_female_names_count = self.df[self.df['gender'] == 'F']['name'].nunique()
        return unique_male_names_count, unique_female_names_count

    def frekwencja_imion(self):
        '''4. Określ popularność każdego z imion w danym każdym roku'''
        # Grupuj dane według roku
        total_births = self.df.groupby(['year', 'gender'])['count'].sum().reset_index()
        total_births.columns = ['year', 'gender', 'total_births']

        # Dołącz całkowitą liczbę urodzeń do oryginalnego DataFrame
        self.df = self.df.merge(total_births, on=['year', 'gender'])
        # oblicz frekwencję
        self.df['frequency'] = self.df['count'] / self.df['total_births']

        # Podziel na czestotliwość występowania imion dla obu płci
        self.df['frequency_male'] = np.where(self.df['gender'] == 'M', self.df['frequency'], 0.0)
        self.df['frequency_female'] = np.where(self.df['gender'] == 'F', self.df['frequency'], 0.0)
        
    def liczba_urodzin_wykres(self):
        '''5. Określ i wyświetl wykres złożony z dwóch podwykresów, gdzie osią x jest skala czasu, a oś y reprezentuje:
        liczbę urodzin w danym roku (wykres na górze)
        stosunek liczby narodzin dziewczynek do liczby narodzin chłopców w każdym roku(wykres na dole)'''

        fig, axs = plt.subplots(2, 1, figsize=(12, 10))

        # Wykres 1: Liczba urodzin w danym roku
        self.df.groupby('year')['count'].sum().plot(ax=axs[0])
        axs[0].set_title('Liczba urodzin w danym roku')
        axs[0].set_xlabel('Rok')
        axs[0].set_ylabel('Liczba urodzin')

        # Wykres 2: Stosunek liczby narodzin dziewczynek do chłopców
        ratio = self.df[self.df['gender'] == 'F'].groupby('year')['count'].sum() / \
                self.df[self.df['gender'] == 'M'].groupby('year')['count'].sum()
        ratio.plot(ax=axs[1])
        axs[1].set_title('Stosunek liczby narodzin dziewczynek do chłopców')
        axs[1].set_xlabel('Rok')
        axs[1].set_ylabel('Ratio')

        # Znajdź rok i wartość maksimum
        max_year = ratio.idxmax()
        max_value = np.max(ratio)
        min_year = ratio.idxmin()
        min_value = np.min(ratio)

        # Zaznacz punkty maksimum i minimum na wykresie
        axs[1].annotate(f'Max: {max_value:.2f}, {max_year}', xy=(max_year, max_value), xytext=(max_year + 0.1, max_value + 0.1), arrowprops=dict(arrowstyle='->'))
        axs[1].annotate(f'Min: {min_value:.2f}, {min_year}', xy=(min_year, min_value), xytext=(min_year + 3.0, min_value + 0.1), arrowprops=dict(arrowstyle='->'))

        plt.tight_layout()
        plt.show()

    def najpopularniejsze_imiona(self):
        '''6. Wyznacz 1000 najpopularniejszych imion osobno dla każdej płci w całym zakresie czasowym. 
        Jako najpopularniejsze należy uznać imiona, których średnia popularność liczona w całym horyzoncie czasu jest największa'''

        # liczymy średnią popularność imion dla każdej płci i sortujemy je malejąco
        self.male_1000_names_descending = self.df.groupby('name').agg({'frequency_male': 'mean'}).sort_values(by='frequency_male', ascending=False).reset_index().head(1000)
        self.female_1000_names_descending = self.df.groupby('name').agg({'frequency_female': 'mean'}).sort_values(by='frequency_female', ascending=False).reset_index().head(1000)

    def najpopularniejsze_imiona_wykres(self):
        '''7.Wyświetl na jednym wykresie zmiany dla drugiego najpopularniejszego imienia męskiego w okresie od 2000r
          i pierwszego najpopularniejszego imienia żeńskiego rankingu top-1000 '''

        # Aby znaleźć drugie najpopularniejsze imię męskie od 2000 roku też obliczam średnią popularność ale od 2000 roku
        male_from_2000 = self.df[self.df['year'] >= 2000 & (self.df['gender'] == 'M')]
        count_male = male_from_2000.groupby('name').agg({'frequency_male': 'mean'}).reset_index().sort_values(by='frequency_male', ascending=False)
        second_most_popular_male_name = count_male.iloc[1]['name']
        first_top_1000_female_name = self.female_1000_names_descending.iloc[0]['name']
        fig, ax = plt.subplots(figsize=(12, 6))

         # Pobierz dane dla konkretnych imion
        male_data = self.df[(self.df['name'] == second_most_popular_male_name) & (self.df['gender'] == 'M')]
        female_data = self.df[(self.df['name'] == first_top_1000_female_name) & (self.df['gender'] == 'F')]
        ax.plot(male_data['year'], male_data['count'], label=second_most_popular_male_name)
        ax.annotate(f'{male_data[male_data['year'] == 1934]['count'].values[0]} razy', xy=(1934, male_data[male_data['year'] == 1934]['count'].values[0]), 
                    xytext=(1934, male_data[male_data['year'] == 1934]['count'].values[0] - 10000), ha='center', arrowprops=dict(arrowstyle='->'))
        ax.annotate(f'{male_data[male_data['year'] == 1980]['count'].values[0]} razy', xy=(1980, male_data[male_data['year'] == 1980]['count'].values[0]), 
                    xytext=(1980, male_data[male_data['year'] == 1980]['count'].values[0] + 20000), ha='center', arrowprops=dict(arrowstyle='->'))   
        ax.annotate(f'{male_data[male_data['year'] == 2024]['count'].values[0]} razy', xy=(2024, male_data[male_data['year'] == 2024]['count'].values[0]), 
                    xytext=(2024, male_data[male_data['year'] == 2024]['count'].values[0] + 20000), ha='center', arrowprops=dict(arrowstyle='->'))
        ax.plot(female_data['year'], female_data['count'], label=first_top_1000_female_name, color='orange')
        ax.annotate(f'{female_data[female_data['year'] == 1934]['count'].values[0]} razy', xy=(1934, female_data[female_data['year'] == 1934]['count'].values[0]), xytext=(1934, female_data[female_data['year'] == 1934]['count'].values[0] + 20000), ha='center', arrowprops=dict(arrowstyle='->'))
        ax.annotate(f'{female_data[female_data['year'] == 1980]['count'].values[0]} razy', xy=(1980, female_data[female_data['year'] == 1980]['count'].values[0]), xytext=(1980, female_data[female_data['year'] == 1980]['count'].values[0] - 10000), ha='center', arrowprops=dict(arrowstyle='->'))
        ax.annotate(f'{female_data[female_data['year'] == 2024]['count'].values[0]} razy', xy=(2024, female_data[female_data['year'] == 2024]['count'].values[0]), xytext=(2024, female_data[female_data['year'] == 2024]['count'].values[0] + 5000), ha='center', arrowprops=dict(arrowstyle='->'))
        ax.set_xlabel('Rok')
        ax.set_ylabel('Liczba nadanych imion')

        # Druga oś Y po prawej stronie - frequency
        ax2 = ax.twinx()

        # Znajdź zakres frequency dla tych imion aby ustawić odpowiednią skalę
        male_freq = self.df[(self.df['name'] == second_most_popular_male_name)]['frequency']
        female_freq = self.df[(self.df['name'] == first_top_1000_female_name)]['frequency']
        all_freq = pd.concat([male_freq, female_freq])
    
        # Ustaw limity osi Y2 na podstawie rzeczywistych wartości frequency
        ax2.set_ylim(all_freq.min() * 0.9, all_freq.max() * 1.1)
        ax2.set_ylabel('Częstość nadawania imion (frequency)', color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        ax.set_title(f'Popularność  imienia męskiego, które było drugim najpopularniejszym imieniem od 2000 roku i pierwszego najpopularniejszego imienia żeńskiego w czasie')
        ax.legend()

        plt.show()

if __name__ == "__main__":
        projekt1 = Projekt1()
        projekt1.wczytaj_dane_SSA()
        unique_names_count = projekt1.liczba_unikalnych_imion()
        print(f"Rozwiązanie zadania 2. Liczba unikalnych imion nadanych w USA w latach 1880-2024: {unique_names_count}")
        unique_male_names_count, unique_female_names_count = projekt1.liczba_unikalnych_imion_gender()
        print(f"Rozwiązanie zadania 3. Liczba unikalnych imion męskich: {unique_male_names_count}, żeńskich: {unique_female_names_count}")
        projekt1.frekwencja_imion()
        projekt1.liczba_urodzin_wykres()
        projekt1.najpopularniejsze_imiona()
        projekt1.najpopularniejsze_imiona_wykres()