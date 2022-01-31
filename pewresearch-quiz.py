from selenium import webdriver
from collections import Counter
import numpy as np
import random
import time 
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from tqdm import tqdm


def one_trial():
    two = [1,2,4,6,11,15,16]
    three = [3,5,9,14]
    four = [7,12]
    five = [13]
    
    short_base = 'div.wp-block-prc-quiz-answer:nth-child({}) > div:nth-child(1)'
    long_base_a = 'div.wp-block-prc-quiz-question:nth-child({}) > div:nth-child(2) > div:nth-child(1) > button:nth-child({})'
    long_base_b = 'div.wp-block-prc-quiz-question:nth-child({}) > div:nth-child(2) > div:nth-child({}) > div:nth-child(1)'
    
    driver = webdriver.Firefox(executable_path=r'C:\Users\WatchDog\geckodriver.exe')
    driver.get('https://www.pewresearch.org/politics/quiz/political-typology/')
    time.sleep(1)
    driver.find_element_by_css_selector('.start-quiz').click()
    one_row = []
    
    for i in range(1,17):
        if i in two:
            c = random.choice(np.arange(1,3))
            one_row.append(c)
            s = short_base.format(c)
            driver.find_element_by_css_selector(s).click()
        elif i in three:
            c = random.choice(np.arange(1,4))
            one_row.append(c)
            s = short_base.format(c)
            driver.find_element_by_css_selector(s).click()
        elif i in four:
            c = random.choice(np.arange(1,5))
            one_row.append(c)
            s = short_base.format(c)
            driver.find_element_by_css_selector(s).click()
        elif i in five:
            c = random.choice(np.arange(1,6))
            one_row.append(c)
            s = short_base.format(c)
            driver.find_element_by_css_selector(s).click()
        elif i == 8:
            c1 = random.choice(np.arange(1,12))
            s1 = long_base_a.format(3,c1)
            c2 = random.choice(np.arange(1,12))
            s2 = long_base_a.format(4,c2)
            one_row.append([c1,c2])
            driver.find_element_by_css_selector(s1).click()
            driver.find_element_by_css_selector(s2).click()
        else:
            c1 = random.choice(np.arange(1,4))
            s1 = long_base_b.format(3,c1)
            c2 = random.choice(np.arange(1,4))
            s2 = long_base_b.format(4,c2)
            one_row.append([c1,c2])
            driver.find_element_by_css_selector(s1).click()
            driver.find_element_by_css_selector(s2).click()
            
        if i != 16:
            driver.find_element_by_css_selector('.next-question').click()
        else:
            driver.find_element_by_css_selector('.submit').click()
            break
            
    time.sleep(5)
    url = driver.current_url
    driver.quit()
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text)
    allDivs = soup.findAll('h1')
    result = allDivs[1].text
    one_row.append(result)
    return one_row


def sample(n):
    results = []
    for i in tqdm(range(n)):
        results.append(one_trial())
        time.sleep(random.choice(np.arange(10)))
    q_names = ['q' + str(num) for num in np.arange(1,17).tolist()]
    cols = q_names + ['Typology']
    df = pd.DataFrame(results,columns=cols)
    
    def categorize(t):
        if t == 'Stressed Sideliners':
            return 'Moderate'
        elif t in ['Progressive Left','Establishment Liberals','Democratic Mainstays','Outsiders']:
            return 'Left'
        else:
            return 'Right'
    df['Group'] = df.Typology.apply(categorize)
    csv_title = 'data_pewresearch_'+'n'+str(n)+'_'+datetime.now().strftime("%m-%d-%Y-%H-%M") + '.csv'
    df.to_csv(csv_title)
    
    def report(colname):
        s = df[colname]
        counts = s.value_counts()
        percent = s.value_counts(normalize=True).mul(100).round(1).astype(str) + '%'
        report = pd.DataFrame({'counts': counts, 'per': percent})
        display(report)
    
    report('Typology'), report('Group')
    return None


if __name__ == "__main__":
    n = input("How many times:")
    sample(n)