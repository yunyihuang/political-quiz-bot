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


q_base = '#question{} > ul:nth-child(2) > li:nth-child({}) > label:nth-child(1) > span:nth-child(2)'
submit_button = '#quiz-wrapper > div:nth-child(2) > a:nth-child(1) > span:nth-child(1)'

def one_trial():
    driver = webdriver.Firefox(executable_path=r'C:\Users\WatchDog\geckodriver.exe')
    driver.get('https://www.politicalpersonality.org/test/')
    time.sleep(2.5)
    
    one_row = []
    for i in range(15):
        rand_answer = np.random.choice([1,2,3,4,5])
        one_row.append(rand_answer)
        driver.find_element_by_css_selector(q_base.format(i,rand_answer)).click()

    driver.find_element_by_css_selector(submit_button).click()
    url = driver.current_url
    driver.quit()
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text)
    allDivs = soup.findAll('h2')
    percent = allDivs[0].text.split()[0]
    one_row.append(percent)
    result = allDivs[0].text.split()[1]
    one_row.append(result)
    
    return one_row


def sample(n):
    results = []
    for i in tqdm(range(n)):
        results.append(one_trial())
        print(i+1)
        time.sleep(0.5)
    q_names = ['q' + str(num) for num in np.arange(1,16).tolist()]
    cols = q_names + ['Percentage','Party']
    df = pd.DataFrame(results,columns=cols)
    csv_title = 'data_politicalpersonality_'+'n'+str(n)+'_'+datetime.now().strftime("%m-%d-%Y-%H-%M") + '.csv'
    df.to_csv(csv_title)
    display(df)
    
    s = df.Party
    counts = s.value_counts()
    percent = s.value_counts(normalize=True).mul(100).round(1).astype(str) + '%'
    report = pd.DataFrame({'counts': counts, 'per': percent})
    return report


if __name__ == "__main__":
    n = input("How many times:")
    sample(n)