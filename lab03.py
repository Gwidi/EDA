import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import pandasgui

# probability density function for normal distribution
def pdf(x, mean, std_dev): 
     return (1/(std_dev*np.sqrt(np.pi)))*np.exp((-(x-mean)**2)/(2*std_dev**2))

def exercise_1():
    fig, ax = plt.subplots()
    x = np.linspace(-5, 5, 100)
    
    ax.plot(x, pdf(x,0,1), 'or' )
    ax.plot(x, pdf(x,-2,2), ':b' )
    ax.plot(x, pdf(x,3,3), '--g' )
    ax.plot(x, pdf(x,4,4), '-xk' )
    # add graph description
    ax.set_title('Rozkład Gaussa', fontsize=16)
    ax.legend(['mean=0, std=1', 'mean=-2, std=2', 'mean=3, std=3', 'mean=4, std=4'])
    ax.set_ylim(0, 1)
    ax.set_xticks(np.arange(-5, 6, 1))
    ax.set_xticks(np.arange(-5, 5, 0.5), minor=True)

    plt.show()

def exercise_2():
    fig, ax = plt.subplots()
    x = np.linspace(-5, 5, 100)
    
    ax.plot(x, pdf(x,0,1), 'or' )
    ax.plot(x, pdf(x,-2,2), ':b' )
    ax.plot(x, pdf(x,3,3), '--g' )
    ax.plot(x, pdf(x,4,4), 'xk' )
    # add graph description
    ax.set_title('Rozkład Gaussa', fontsize=16)
    ax.legend([r'$\mu=0, \sigma=1$', 
               r'$\mu=-2, \sigma=2$', 
               r'$\mu=3, \sigma=3$', 
               r'$\mu=4, \sigma=4$'], 
              loc='upper left')
    ax.set_ylim(0, 1)
    ax.set_xlim(-5, 5)
    ax.set_xticks(np.arange(-5, 6, 1))
    ax.set_xticks(np.arange(-5, 5, 0.5), minor=True)
    ax.grid()
    ax.set_ylabel('f(x)')
                  
    plt.xticks(rotation=45)
    plt.show()

def exercise_3():
    df = pd.json_normalize(pd.read_json('dataset/cancer_survival_in_us.json')['age_groups'])

    print(df.head())


    fig, ax = plt.subplots()

    x = np.arange(len(df['male_survivors']))
    width = 0.3

    ax.bar(x-width/2, df['male_survivors'], width, label='Man')
    ax.bar(x+width/2, df['female_survivors'], width, label='Woman')

    labels = df['age']

    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.tick_params(axis='x', rotation=90)
    ax.grid(axis='y')
    ax.set_ylim(0, 40)
    yticks = ax.get_yticks()
    ax.set_yticklabels([f'{int(y)}%' for y in yticks])
    ax.set_axisbelow(True)

    ax.legend()

    plt.show()

def exercise_4():
    df = pd.json_normalize(pd.read_json('dataset/cancer_survival_in_us.json')['age_groups'])

    print(df.head())


    fig, ax = plt.subplots()

    x = np.arange(len(df['male_survivors']))
    width = 0.3

    ax.bar(x-width/2, df['male_survivors'], width, label='Man')
    ax.bar(x+width/2, df['female_survivors'], width, label='Woman')

    labels = df['age']

    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.tick_params(axis='x', rotation=90)
    ax.grid(axis='y')
    ax.set_ylim(0, 40)
    yticks = ax.get_yticks()
    ax.set_yticklabels([f'{int(y)}%' for y in yticks])
    ax.set_axisbelow(True)

    ax.legend()

    # errorbars
    errorm = np.random.rand(len(df['male_survivors']))*5
    errorw = np.random.rand(len(df['female_survivors']))*5
    ax.errorbar(x-width/2, df['male_survivors'], yerr=errorm, fmt='.k', capsize=2)
    ax.errorbar(x+width/2, df['female_survivors'], yerr=errorw, fmt='.k', capsize=2)

    plt.show()

def exercise_5():
    df = pd.read_csv('dataset/russia2020_vote.csv')
    df['relative_yes_votes'] = df['yes'] / df['given']
    fig, ax = plt.subplots()
    ax.hist(df['relative_yes_votes'], bins=100)

    plt.show()
    # Anomalie w danych - nieoczekiwane piki 



if __name__ == "__main__":
    exercise_2()
    exercise_4()
    exercise_5()
