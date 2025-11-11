import duckdb
import pandas as pd
import pandasgui
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

class Projekt1:
    def __init__(self):
        self.df = pd.DataFrame()
        self.male_1000_names_descending = pd.DataFrame()
        self.female_1000_names_descending = pd.DataFrame()
        self.df_pl = pd.DataFrame()

    def wczytaj_dane_SSA(self):
        '''1.Wczytaj dane ze wszystkich plików do pojedynczej tablicy'''
        conn = duckdb.connect()
        self.df = conn.execute("SELECT * from read_csv('./data/names/*.txt', header=false, " \
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

    def frekwencja_imion(self, dataframe):
        '''4. Określ popularność każdego z imion w danym każdym roku'''
        # Grupuj dane według roku
        total_births = dataframe.groupby(['year', 'gender'])['count'].sum().reset_index()
        total_births.columns = ['year', 'gender', 'total_births']

        # Dołącz całkowitą liczbę urodzeń do oryginalnego DataFrame
        dataframe = dataframe.merge(total_births, on=['year', 'gender'])
        # oblicz frekwencję
        dataframe['frequency'] = dataframe['count'] / dataframe['total_births']

        # Podziel na czestotliwość występowania imion dla obu płci
        dataframe['frequency_male'] = np.where(dataframe['gender'] == 'M', dataframe['frequency'], 0.0)
        dataframe['frequency_female'] = np.where(dataframe['gender'] == 'F', dataframe['frequency'], 0.0)

        return dataframe
        
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

    def najpopularniejsze_imiona(self, df, number=1000):
        '''6. Wyznacz 1000 najpopularniejszych imion osobno dla każdej płci w całym zakresie czasowym. 
        Jako najpopularniejsze należy uznać imiona, których średnia popularność liczona w całym horyzoncie czasu jest największa'''

        # liczymy średnią popularność imion dla każdej płci i sortujemy je malejąco
        top_n_male_names_descending = df.groupby('name').agg({'frequency_male': 'mean'}).sort_values(by='frequency_male', ascending=False).reset_index().head(number)
        top_n_female_names_descending = df.groupby('name').agg({'frequency_female': 'mean'}).sort_values(by='frequency_female', ascending=False).reset_index().head(number)
        return top_n_male_names_descending, top_n_female_names_descending

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

    def zmiana_roznorodnosci_imion_wykres(self):
        '''8. Określ zmiany różnorodności imion w czasie'''
        fig, ax = plt.subplots(figsize=(12, 6))

        # Pobierz zestawy 1000 najpopularniejszych imion dla obu płci
        top_male = set(self.male_1000_names_descending['name'])
        top_female = set(self.female_1000_names_descending['name'])

        # Filtruj oryginalny DataFrame, aby sprawdzić, czy imię należy do top 1000     
        df_m = self.df[self.df['gender'] == 'M']
        df_f = self.df[self.df['gender'] == 'F']
        cov_m = df_m[df_m['name'].isin(top_male)].groupby('year').count() # liczba imion z top 1000 które się pokrywają z imionami w danym roku
        cov_f = df_f[df_f['name'].isin(top_female)].groupby('year').count()

        max_dif = np.argmax(np.abs(cov_m['name'] - cov_f['name']))
        max_dif_year = cov_m.index[max_dif]

        ax.plot(self.df['year'].unique(), cov_m['name']/10, label='Męskie', color='blue')
        ax.plot(self.df['year'].unique(), cov_f['name']/10, label='Żeńskie', color='pink')
        ax.annotate(f'Max różnica: {max_dif_year} rok', xy=(max_dif_year, cov_m.loc[max_dif_year]['name']/10), xytext=(max_dif_year, cov_m.loc[max_dif_year]['name']/10+5), arrowprops=dict(arrowstyle='->'))
        ax.set_title('Zmiany różnorodności imion w czasie na przestrzeni lat 1880-2024')
        ax.set_xlabel('Rok')
        ax.set_ylabel('Procent nadawanych imion z top 1000')
        ax.legend()
        plt.show()
        print(f'Maksymalna różnica między płciami w procentach nadawanych imion z top 1000 wynosi: {max_dif}% w roku {max_dif_year}')
        print(f'Na początku badanego okresu występowała znacznie większa różnorodność nadawanych imion męskich jednak wraz z biegiem lat różnorodność imion męskich i żeńskich wzrastała liniowo i osiągnęła najwyższe zbliżone wartości w ostatnich latach badania')

    def hipoteza(self):
        '''9. Zweryfikuj hipotezę czy prawdą jest, że w obserwowanym okresie rozkład ostatnich liter imion męskich uległ istotnej zmianie'''
        
        self.df['last_letter'] = self.df['name'].str[-1]
        # agregacja: suma urodzeń (count) dla każdej kombinacji year, gender, last_letter
        df_agg = (
            self.df
            .groupby(['year', 'gender', 'last_letter'])['count']
            .sum()
            .reset_index(name='births')
        )
        # wyodrębnij dane dla lat 1900, 1975, 2024 dla mężczyzn
        male = df_agg[df_agg['gender'] == 'M'] 

        # Stwórz tabelę przestawną
        pivot = male.pivot(index='last_letter', columns='year', values='births')

        # Znormalizuj dane względem całkowitej liczby urodzin w danym roku
        pivot = pivot.div(pivot.sum(axis=0), axis=1) * 100

        years = [1900, 1975, 2024]
        letters = pivot.index.tolist()
        x = np.arange(len(letters))  
        width = 0.25

        fig, ax = plt.subplots(figsize=(14, 7))
        for i, year in enumerate(years):
            vals = pivot.get(year).values
            ax.bar(x + (i - 1) * width, vals, width=width, label=str(year))

        ax.set_xticks(x)
        ax.set_xticklabels(letters, rotation=0)
        ax.set_xlabel('Ostatnia litera imienia')
        ax.set_ylabel('Procent liczby urodzin w danym roku [%]')
        ax.set_title('Popularność ostatnich liter imion męskich (1900, 1975, 2024)')
        ax.legend(title='Rok')
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()

        #  Wyświetl, dla której litery wystąpił największy wzrost/spadek między rokiem 1900 a 2024
        changes = pivot[2024] - pivot[1900]
        max_increase_letter = changes.idxmax()
        max_decrease_letter = changes.idxmin()
        print('Rozwiązanie zadania 9:')
        print(f'Największy wzrost między latami 1900 a 2024 wystąpił dla litery: {max_increase_letter} ({changes[max_increase_letter]:.2f}%)')
        print(f'Największy spadek między latami 1900 a 2024 wystąpił dla litery: {max_decrease_letter} ({changes[max_decrease_letter]:.2f}%)')

        # Dla 3 liter dla których zaobserwowano największą zmianę wyświetl przebieg trendu popularności w całym okresie czasu (dla każdego roku)
        top_3_letters = changes.abs().sort_values(ascending=False).head(3).index.tolist()
        
        

        fig, ax = plt.subplots(figsize=(14, 7))
        for letter in top_3_letters:
            letter_data = pivot[pivot.index == letter]
            ax.plot(letter_data.columns, letter_data.values.flatten(), label=letter)

        plt.title('Trendy popularności ostatnich liter imion męskich')
        plt.xlabel('Ostatnia litera imienia')
        plt.ylabel('Procent liczby urodzin w danym roku [%]')
        plt.legend(title='Rok')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()

    def konotacje_imion(self):
        '''10. Przeprowadź analizę konotacji imion nadawanych chłopcom i dziewczynkom'''

        # Znajdź imiona unisex w top 1000
        top_male_names = set(self.male_1000_names_descending['name'])
        top_female_names = set(self.female_1000_names_descending['name'])
        unisex_names = top_male_names.intersection(top_female_names)

        # Dane do 1920 roku dla imion unisex
        df_unisex_1920 = self.df[
            (self.df['year'] <= 1920) &
            (self.df['name'].isin(unisex_names))
        ]
        
        # Zsumuj count dla każdego imienia i płci
        cross_1920 = pd.crosstab(
            index=df_unisex_1920['name'],
            columns=df_unisex_1920['gender'],
            values=df_unisex_1920['count'],
            aggfunc='sum'
        ).fillna(0)

        # Oblicz całkowitą liczbę urodzin i wskaźniki konotacji
        cross_1920['total'] = cross_1920['M'] + cross_1920['F']
        cross_1920['w_m'] = cross_1920['M'] / cross_1920['total']
        cross_1920['w_f'] = cross_1920['F'] / cross_1920['total']


        # Analogicznie dla okresu od 2000 roku
        df_unisex_2000 = self.df[
            (self.df['year'] >= 2000) &
            (self.df['name'].isin(unisex_names))
        ]

        cross_2000 = pd.crosstab(
            index=df_unisex_2000['name'],
            columns=df_unisex_2000['gender'],
            values=df_unisex_2000['count'],
            aggfunc='sum'
        ).fillna(0)

        cross_2000['total'] = cross_2000['M'] + cross_2000['F']
        cross_2000['w_m'] = cross_2000['M'] / cross_2000['total']
        cross_2000['w_f'] = cross_2000['F'] / cross_2000['total']

        # Znajdź imiona które występują w obu okresach
        common_names = cross_1920.index.intersection(cross_2000.index)

        # oblicz zmiany konotacji
        changes = pd.DataFrame(index=common_names)

        changes['w_m_1920'] = cross_1920.loc[common_names, 'w_m']
        changes['w_f_1920'] = cross_1920.loc[common_names, 'w_f']
        changes['w_m_2000'] = cross_2000.loc[common_names, 'w_m']
        changes['w_f_2000'] = cross_2000.loc[common_names, 'w_f']
        
        # Zmiana z męskiego na żeńskie: (w_m(1920) + w_f(2000)) / 2
        changes['male_to_female'] = (changes['w_m_1920'] + changes['w_f_2000']) / 2
        
        # Zmiana z żeńskiego na męskie: (w_f(1920) + w_m(2000)) / 2
        changes['female_to_male'] = (changes['w_f_1920'] + changes['w_m_2000']) / 2
        
        # Znajdź największe zmiany
        # Imię które było męskie (w_m_1920 > 0.7) a teraz żeńskie (w_f_2000 > 0.7)
        male_to_female_candidates = changes.sort_values('male_to_female', ascending=False)
        
        # Imię które było żeńskie (w_f_1920 > 0.7) a teraz męskie (w_m_2000 > 0.7)
        female_to_male_candidates = changes.sort_values('female_to_male', ascending=False)
        print("Rozwiązanie zadania 10:")
    
        for i, (name, row) in enumerate(male_to_female_candidates.head(1).iterrows()):
            print(f"\n{i+1}. Imię: {name}")
            print(f"   Do 1920: {row['w_m_1920']*100:.1f}% męskie, {row['w_f_1920']*100:.1f}% żeńskie")
            print(f"   Od 2000: {row['w_m_2000']*100:.1f}% męskie, {row['w_f_2000']*100:.1f}% żeńskie")
            print(f"   Wskaźnik zmiany: {row['male_to_female']:.3f}")
            
            # Dodaj liczby absolutne
            births_1920_m = cross_1920.loc[name, 'M']
            births_1920_f = cross_1920.loc[name, 'F']
            births_2000_m = cross_2000.loc[name, 'M']
            births_2000_f = cross_2000.loc[name, 'F']
            print(f" Liczby: 1920: M={births_1920_m:.0f}, F={births_1920_f:.0f} | 2000+: M={births_2000_m:.0f}, F={births_2000_f:.0f}")

        for i, (name, row) in enumerate(female_to_male_candidates.head(1).iterrows()):
            print(f"\n{i+1}. Imię: {name}")
            print(f"   Do 1920: {row['w_m_1920']*100:.1f}% męskie, {row['w_f_1920']*100:.1f}% żeńskie")
            print(f"   Od 2000: {row['w_m_2000']*100:.1f}% męskie, {row['w_f_2000']*100:.1f}% żeńskie")
            print(f"   Wskaźnik zmiany: {row['male_to_female']:.3f}")
            
            # Dodaj liczby absolutne
            births_1920_m = cross_1920.loc[name, 'M']
            births_1920_f = cross_1920.loc[name, 'F']
            births_2000_m = cross_2000.loc[name, 'M']
            births_2000_f = cross_2000.loc[name, 'F']
            print(f" Liczby: 1920: M={births_1920_m:.0f}, F={births_1920_f:.0f} | 2000+: M={births_2000_m:.0f}, F={births_2000_f:.0f}")     
        
        # Weź top 2 imiona z największymi zmianami
        top_male_to_female = male_to_female_candidates.head(1).index[0]
        top_female_to_male = female_to_male_candidates.head(1).index[0]
        
        # Przygotuj dane dla wykresu trendu konotacji
        selected_names = [top_male_to_female, top_female_to_male]
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        for idx, name in enumerate(selected_names):
            # Pobierz dane dla danego imienia we wszystkich latach
            name_data = self.df[self.df['name'] == name]
            
            # Oblicz wskaźnik konotacji dla każdego roku
            yearly_connotation = name_data.groupby(['year', 'gender'])['count'].sum().unstack(fill_value=0)
            
            # Upewnij się, że mamy obie kolumny
            if 'M' not in yearly_connotation.columns:
                yearly_connotation['M'] = 0
            if 'F' not in yearly_connotation.columns:
                yearly_connotation['F'] = 0
                
            yearly_connotation['total'] = yearly_connotation['M'] + yearly_connotation['F']
            yearly_connotation['w_m'] = yearly_connotation['M'] / yearly_connotation['total']
            yearly_connotation['w_f'] = yearly_connotation['F'] / yearly_connotation['total']
            
            # Wykres trendu
            ax = axes[idx]
            ax.plot(yearly_connotation.index, yearly_connotation['w_m'] * 100, 
                   label='Męskie (%)', color='blue', linewidth=2)
            ax.plot(yearly_connotation.index, yearly_connotation['w_f'] * 100, 
                   label='Żeńskie (%)', color='pink', linewidth=2)
            
            # Zaznacz przedziały analizy
            ax.axvspan(1880, 1920, alpha=0.2, color='yellow', label='Okres do 1920')
            ax.axvspan(2000, 2024, alpha=0.2, color='lightgreen', label='Okres od 2000')
            
            # Dodaj adnotacje dla kluczowych punktów
            w_m_1920 = changes.loc[name, 'w_m_1920']
            w_f_1920 = changes.loc[name, 'w_f_1920']
            w_m_2000 = changes.loc[name, 'w_m_2000']
            w_f_2000 = changes.loc[name, 'w_f_2000']
            
            ax.annotate(f'1920: {w_m_1920*100:.1f}% M, {w_f_1920*100:.1f}% F',
                       xy=(1920, w_m_1920*100 if w_m_1920 > w_f_1920 else w_f_1920*100),
                       xytext=(1920, 85), fontsize=9,
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            ax.annotate(f'2000+: {w_m_2000*100:.1f}% M, {w_f_2000*100:.1f}% F',
                       xy=(2000, w_m_2000*100 if w_m_2000 > w_f_2000 else w_f_2000*100),
                       xytext=(1960, 15), fontsize=9,
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
            
            ax.set_xlabel('Rok', fontsize=11)
            ax.set_ylabel('Procent (%)', fontsize=11)
            ax.set_title(f'Zmiana konotacji imienia "{name}" na przestrzeni lat', 
                        fontsize=12, fontweight='bold')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            ax.set_ylim(-5, 105)
            
        plt.tight_layout()
        plt.show()
                
    def wczytaj_dane_pl(self):
        conn = sqlite3.connect('./data/names_pl_2000-24.sqlite')
        # Zapytanie SQL łączące dane dla obu płci z dodaniem kolumny gender
        query = """
        SELECT 
            Imię as name,
            Rok as year,
            'M' as gender,
            Liczba as count
        FROM 
            males

        UNION ALL

        SELECT 
            Imię as name,
            Rok as year,
            'F' as gender,
            Liczba as count
        FROM
            females

        ORDER BY year, name, gender
        """
        self.df_pl = pd.read_sql_query(query, conn)
        conn.close()

    def ranking_imion_pl(self):
        '''11. Stwórz ranking 200 najpopularniejszych imion nadawanych w Polsce dla każdej płci w latach 2000-2024'''
        self.df_pl = self.frekwencja_imion(self.df_pl)
        top_male, top_female = self.najpopularniejsze_imiona(self.df_pl, number=200)
        top_male = set(top_male['name'])
        top_female = set(top_female['name'])

        # Filtruj oryginalny DataFrame, aby sprawdzić, czy imię należy do top 1000
        years = [2000, 2013, 2024]     
        df_m = self.df_pl[self.df_pl['gender'] == 'M']
        df_f = self.df_pl[self.df_pl['gender'] == 'F']
        cov_m = df_m[df_m['name'].isin(top_male)].groupby('year').count() # liczba imion z top 200 które się pokrywają z imionami w danym roku
        cov_f = df_f[df_f['name'].isin(top_female)].groupby('year').count()
        cov_m = cov_m[cov_m.index.isin(years)]
        cov_f = cov_f[cov_f.index.isin(years)]

        

        fig, ax = plt.subplots(figsize=(12, 6))
        width = 0.4  # szerokość słupków
        x = np.arange(len(years))
        ax.set_xticks(x)
        ax.set_xticklabels(years)

        ax.bar(x - width/2, cov_m['name'], label='Męskie', color='blue', width=width)
        ax.bar(x + width/2, cov_f['name'], label='Żeńskie', color='pink', width=width)
        ax.set_title('Liczba imiona męskich i żeńskich które pokrywają się z top 200 imionami w Polsce w latach 2000-2024')
        ax.set_xlabel('Rok')
        ax.set_ylabel('Liczba nadawanych imion z top 200')
        ax.legend()
        plt.show()
        print(f'Odpowiedź do zadania 11: Na histogramie widać że różnorodność imion dla obu płci wzrosła przy czym różnorodność imion męskich jest podobna do różnorodności imion żeńskich w 2013 roku(w 2000 roku rożnorodność imion żeńskich była niższa w stosunku do różnorodności imion męskich. Nie potrafię zidentyfikować innych czynników wpływających na tę sytuację na podstawie dostępnych danych.')
        
        # Przeanalizuj czy w Polsce również preferowane są imiona kończące się na określone litery (jak w USA).
        self.df_pl['last_letter'] = self.df['name'].str[-1]
        # agregacja: suma urodzeń (count) dla każdej kombinacji year, gender, last_letter
        df_agg = (
            self.df_pl
            .groupby(['year', 'gender', 'last_letter'])['count']
            .sum()
            .reset_index(name='births')
        )
        # wyodrębnij dane dla lat 2000 - 2024 dla mężczyzn
        male = df_agg[df_agg['gender'] == 'M'] 

        # Stwórz tabelę przestawną
        pivot = male.pivot(index='last_letter', columns='year', values='births')

        # Znormalizuj dane względem całkowitej liczby urodzin w danym roku
        pivot = pivot.div(pivot.sum(axis=0), axis=1) * 100

        #  Wyświetl, dla której litery wystąpił największy wzrost/spadek między rokiem 1900 a 2024
        changes = pivot[2024] - pivot[2000]
        max_increase_letter = changes.idxmax()
        max_decrease_letter = changes.idxmin()
        print(f'Największy wzrost między latami 2000 a 2024 dla imion męskich wystąpił dla litery: {max_increase_letter} ({changes[max_increase_letter]:.2f}%)')
        print(f'Największy spadek między latami 2000 a 2024 dla imion męskich wystąpił dla litery: {max_decrease_letter} ({changes[max_decrease_letter]:.2f}%)')

        # Dla 3 liter dla których zaobserwowano największą zmianę wyświetl przebieg trendu popularności w całym okresie czasu (dla każdego roku)
        top_3_letters = changes.abs().sort_values(ascending=False).head(3).index.tolist()
        
        

        fig, ax = plt.subplots(figsize=(14, 7))
        for letter in top_3_letters:
            letter_data = pivot[pivot.index == letter]
            ax.plot(letter_data.columns, letter_data.values.flatten(), label=letter)

        plt.title('Trendy popularności ostatnich liter imion męskich')
        plt.xlabel('Ostatnia litera imienia')
        plt.ylabel('Procent liczby urodzin w danym roku [%]')
        plt.legend(title='Rok')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
        
        

if __name__ == "__main__":
        # Utworzenie instancji klasy Projektu1
        projekt1 = Projekt1()
        # Wywołanie poszczególnych metod w celu wykonania zadań związanych z danymi z USA
        projekt1.wczytaj_dane_SSA()
        unique_names_count = projekt1.liczba_unikalnych_imion()
        print(f"Rozwiązanie zadania 2. Liczba unikalnych imion nadanych w USA w latach 1880-2024: {unique_names_count}")
        unique_male_names_count, unique_female_names_count = projekt1.liczba_unikalnych_imion_gender()
        print(f"Rozwiązanie zadania 3. Liczba unikalnych imion męskich: {unique_male_names_count}, żeńskich: {unique_female_names_count}")
        projekt1.df = projekt1.frekwencja_imion(projekt1.df)
        projekt1.liczba_urodzin_wykres()
        projekt1.male_1000_names_descending, projekt1.female_1000_names_descending = projekt1.najpopularniejsze_imiona(projekt1.df, number=1000)
        projekt1.najpopularniejsze_imiona_wykres()
        projekt1.zmiana_roznorodnosci_imion_wykres()
        projekt1.hipoteza()
        projekt1.konotacje_imion()

        # Wywołanie poszczególnych metod w celu wykonania zadań związanych z danymi z Polski
        projekt1.wczytaj_dane_pl()
        projekt1.ranking_imion_pl()