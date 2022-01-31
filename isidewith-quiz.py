from selenium import webdriver
import numpy as np
import random
import time 
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# question ids 
# subjected to change, depend on the update on the target website
q1 = ['s4366038825','s4366038827']
q2 = ['s4583042058','s4583042060']
q3 = ['s2273341264','s2273341265']
q4 = ['s721298053','s721298054']
q5 = ['s4528843472','s4528843474']
q6 = ['s3691152101','s3691152102']
q7 = ['s3256128620','s3256128621']
q8 = ['s3021337056','s3021337057']
q9 = ['s1577235798','s1577235799']
q10 = ['s965628','s965631']
q11 = ['s2782694','s2782700']
q12 = ['s2996070514','s2996070515']
q13 = ['s2982424111','s2982424112']
q14 = ['s1311508936','s1311508937']
q15 = ['s3290645810','s3290645811']
q16 = ['s2407038831','s2407038862']
q17 = ['s2441882896','s2441882897']
q18 = ['s2407083932','s2407083933']
q19 = ['s965571','s965573']
q20 = ['s894292240','s894292241']
q21 = ['s3244269086','s3244269087']
q22 = ['s2905607544','s2905607545']
q23 = ['s965621','s965623']
q24 = ['s383922661','s383922732']
q25 = ['s283756700','s283756702']
q26 = ['s965648','s965650']
q27 = ['s3244267936','s3244267937']
q28 = ['s734977937','s734977938']
q29 = ['s3273264644','s3273264645']
q30 = ['s3023120161','s3023120162']
q31 = ['s3507557','s3507559']
q32 = ['s3410414602','s3410414603']
q33 = ['s1732340010','s1732340011']
q34 = ['s1549397792','s1549397794']
q35 = ['s1328487666','s1328487667']
q36 = ['s965614','s965617']
#q36 = ['s46493328','s46493441']


# convert the question id to binary answer
def answer_transformer(answer):
    # all ids for the positive choices
    ans_y = ['s4366038825','s4583042058','s2273341264','s721298053','s4528843472','s3691152101',
             's3256128620','s3021337056','s1577235798','s965628','s2782694','s2996070514',
             's2982424111','s1311508936','s3290645810','s2407038831','s2441882896','s2407083932',
             's965571','s894292240','s3244269086','s2905607544','s965621','s383922661','s283756700',
             's965648','s3244267936','s734977937','s3273264644','s3023120161','s3507557','s3410414602',
             's1732340010','s1549397792','s1328487666','s965614']
    # checking and returning the corresponding string
    if answer in ans_y:
        return 'Yes'
    else:
        return 'No'


# take the quiz for once, obtaining the url of the result page
def one_trial():
    # open the webpage
    driver = webdriver.Firefox(executable_path=r'C:\Users\WatchDog\geckodriver.exe')
    driver.get('https://www.isidewith.com/')
    
    # start the quiz
    take_quiz_button = '/html/body/div/div[2]/div[2]/div/a'
    agree_button = '/html/body/div[3]/div/div/p[4]/a'
    driver.find_element_by_xpath(take_quiz_button).click()
    driver.find_element_by_xpath(agree_button).click()
    time.sleep(5)
    
    # autofill randomly
    questions = [q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15,q16,q17,q18,q19,
                 q20,q21,q22,q23,q24,q25,q26,q27,q28,q29,q30,q31,q32,q33,q34,q35,q36]
    answers = []
    for q in questions:
        answer = random.choice(q)
        answers.append(answer_transformer(answer))
        driver.find_element_by_id(answer).click()
       
    # show results
    show_results_button = '//*[@id="submit_button"]'
    driver.find_element_by_xpath(show_results_button).click()
    time.sleep(58)
    #no_thanks_button = '/html/body/div[7]/div[2]/div/div[2]/p[3]/a'
    #driver.find_element_by_xpath(no_thanks_button).click()
    url = driver.current_url
    driver.quit()
    
    return {'url':url, 'answers':answers}


# sample n times and get the urls
def sampling_and_get_urls(n):
    urls = []
    all_answers = []
    for i in range(n):
        print(i)
        output = one_trial()
        url = output['url']
        urls.append(url)
        answers = output['answers']
        all_answers.append(answers)
        time.sleep(3)
    return urls, all_answers


# get result dictionary for each candiates in one trial
def get_score(url):
    # obtain the content from the result page
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text)
    
    # obtain the user id and the election id
    info = soup.find_all('span', class_="tag_c")[0].find('a')
    s = info.get('onclick')
    id_lst = re.findall(r'[0-9]+',s)
    user_id,ele_id = id_lst[0], id_lst[1]
    
    # obtain the content from the score scripts
    url = 'https://www.isidewith.com/_scripts/ajax/get_user_election_results/?user_id={}&election_id={}'.format(user_id,ele_id)
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text)
    
    # create a dictionary for candidates and their scores 
    names_raw = soup.find_all('span',class_='ra list_username')
    names = [s.text for s in names_raw]
    pcts_raw = soup.find_all('span', class_ = 'match_perc')
    pcts = [int(p.text.strip('%')) for p in pcts_raw]
    
    return dict(zip(names, pcts))


# get all result dictionaries from n urls
def get_ds(urls):
    ds = []
    for url in urls:
        ds.append(get_score(url))
        time.sleep(1)
    print(len(ds))
    return ds


# combine the data into a dataframe
def combine_data(ds):
    d = {}
    for k in ds[0].keys():
        d[k] = list(d[k] for d in ds)
    return pd.DataFrame(d)



if __name__ == "__main__":
	n = input("How many times:")
	urls,answers = sampling_and_get_urls(n)
	ds = get_ds(urls)
	df = combine_data(ds)
	df.to_csv('data_isidewith_n{}_{}.csv'.format(n,datetime.now().strftime("%m-%d-%Y-%H-%M")))

	df_ans = pd.DataFrame(answers)
	df_ans.columns = ['q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','q11','q12','q13','q14','q15',
                  'q16','q17','q18','q19','q20','q21','q22','q23','q24','q25','q26','q27','q28','q29',
                  'q30','q31','q32','q33','q34','q35','q36']
    df_ans.to_csv('data_ans_isidewith_n{}_{}.csv'.format(n,datetime.now().strftime("%m-%d-%Y-%H-%M")))