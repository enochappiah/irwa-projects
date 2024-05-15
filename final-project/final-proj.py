import logging
import re
import sys
from bs4 import BeautifulSoup
from queue import PriorityQueue, Queue
from urllib import parse, request
from urllib.parse import urlparse
import requests as res
import requests
import os
import datetime
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
import selenium.webdriver.common.alert as Alert
import time
import random #random.randrange(5, 15)
import vendorDict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec, KeyedVectors
from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from itertools import chain




logging.basicConfig(level=logging.DEBUG, filename='output.log', filemode='w')
visitlog = logging.getLogger('visited')
extractlog = logging.getLogger('extracted')

    

def parse_links(links, html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub(r'\s+', ' ', text).strip()
            yield (parse.urljoin(links, link.get('href')), text)

def parse_bobs_for_products(web, website):
    product_dict = {}
    product_grid = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['product-grid'])
    product_cards = product_grid.find_elements(By.TAG_NAME, vendorDict.vendors_dict[website]['product-cards-tag'])
    
    
    for product in product_cards:
        
        product_id = product.find_element(By.CLASS_NAME,vendorDict.vendors_dict[website]['product-id-class']).get_attribute('id')

        try:

            product_name = product.find_element(By.XPATH, f'//*[@id="{product_id}"]/div/bobs-generic-link/div/a/div').text

            product_price = product.find_element(By.XPATH, f'//*[@id="{product_id}"]/div/div[4]/div[2]/div').text
            
            product_link = product.find_element(By.XPATH, f'//*[@id="{product_id}"]/div/bobs-generic-link/div/a').get_attribute('href')

            #remove words from price
            product_price = re.sub(r'[a-zA-Z]+', '', product_price)
            
            #remove whitespace from price
            product_price = re.sub(r'\s+', '', product_price)
            
            #remove commas from price
            product_price = re.sub(r',', '', product_price)
            
            #remove dollar sign from price
            product_price = re.sub(r'\$', '', product_price)
            
            #convert price to float
            product_price = float(product_price)
            
            #trim price to 2 decimal places
            product_price = round(product_price, 2)
            
            #product_dict[website] = {product_name:{}} #initialize dictionary with website as key
            #product_dict[website][product_name] = {'Price': product_price, 'Link': product_link, 'Description': ''}
            #print("BOBS FUNCTION- DICT: ", product_dict)
            #print("BOBS FUNCTION- WEB INDEX: ", product_dict[website])
            #product_dict[product_name] = {'Price': product_price, 'Link': product_link, 'Description': ''}

            '''product_dict[website] = {product_name:{}}
            
            product_dict[website][product_name] = {'Price': product_price, 'Link': product_link, 'Description': ''}
            print("BOBS FUNCTION- DICT: ", product_dict)
            print("BOBS FUNCTION- WEB INDEX: ", product_dict[website])
            '''

            product_dict[product_name] = {'Price': product_price, 'Link': product_link, 'Description': ''}

        except Exception as e:
            break
    return product_dict


def parse_ashley_for_products(web, website):

    product_dict = {}
    product_grid = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['product-grid'])
    product_cards = product_grid.find_elements(By.CLASS_NAME, vendorDict.vendors_dict[website]['product-cards-tag'])
    
    for product in product_cards:
        
        '''product_card_parent = product.parent
        product_price = product_card_parent.get_attribute(By.CLASS_NAME, vendorDict.vendors_dict[website]['product-price-attribute'])

        id = product.get_attribute('id')
        link_element = web.find_element(By.XPATH, f'//*[@id="{id}"]/div[3]/div[1]/a') 
        product_name = link_element.text
        product_link = link_element.get_attribute('href')'''

        try:

            '''detail_section = product_card_parent.get_attribute(vendorDict.vendors_dict[website]['product-name-attribute'])
      
            

            link_section = product.find_element(By.CLASS_NAME, "wide-middle")
            second_link_section = link_section.find_element(By.CLASS_NAME, "product-title")
            product_link = second_link_section.find_element(By.CLASS_NAME, "name-link").get_attribute('href')
            product_name = second_link_section.find_element(By.CLASS_NAME, "name-link").text'''
            product_card_parent = product.parent
            product_price = product_card_parent.get_attribute(By.CLASS_NAME, vendorDict.vendors_dict[website]['product-price-attribute'])

            id = product.get_attribute('id')
            link_element = web.find_element(By.XPATH, f'//*[@id="{id}"]/div[3]/div[1]/a') 
            product_name = link_element.text
            product_link = link_element.get_attribute('href')

            '''#remove words from price
            product_price = re.sub(r'[a-zA-Z]+', '', product_price)
            
            #remove whitespace from price
            product_price = re.sub(r'\s+', '', product_price)
            
            #remove commas from price
            product_price = re.sub(r',', '', product_price)
            
            #remove dollar sign from price
            product_price = re.sub(r'\$', '', product_price)

            #trim price to 2 decimal places
            product_price = round(product_price, 2)'''
            
            #convert price to float
            product_price = float(product_price)
 
            product_dict[product_name] = {'Price': product_price, 'Link': product_link, 'Description': ''}

        except Exception as e:
            break
       
    return product_dict

def parse_bbb_for_products(web, website):

    product_dict = {}
    product_grid = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['product-grid'])
    
    product_cards = product_grid.find_elements(By.CLASS_NAME, vendorDict.vendors_dict[website]['product-cards-class'])


    i = 0
    product_links = []
    for product in product_cards:
        if i == 5:
            break
        
        #product_id = product.find_element(By.CLASS_NAME,vendorDict.vendors_dict[website]['product-id-class']).get_attribute('id')

        #try:

        product_link_tag = product.find_element(By.CLASS_NAME, 'productTile_link__zHGHe')
        product_link = product_link_tag.get_attribute('href')
        product_links.append(product_link) 
        
        print(product_link)
        i += 1
     
            
            #product_name = product.find_element(By.TAG_NAME, 'p').text
            

        
        
            #product_name = outer_detail_div.find_element(By.TAG_NAME, 'p').text
        '''product_name = web.find_element(By.XPATH, '//*[@id="page-wrap"]/main/div/div/div[2]/section[1]/h1').text
        product_price = web.find_element(By.XPATH, '//*[@id="page-wrap"]/main/div/div/div[2]/section[2]/div[1]/div[2]/div[3]').text
        '''
        

        #except Exception as e:
            #break
        
    for link in product_links:
        web.get(link)
        time.sleep(5)
        product_name = web.find_element(By.XPATH, '//*[@id="page-wrap"]/main/div/div/div[2]/section[1]/h1').text
        print(product_name)
        product_price = web.find_element(By.XPATH, '//*[@id="page-wrap"]/main/div/div/div[2]/section[2]/div[1]/div[2]/div[3]').text
        print(product_price)
        

        product_price = re.sub(r'[a-zA-Z]+', '', product_price)
        product_price = re.sub(r'\s+', '', product_price)
        product_price = re.sub(r'\$', '', product_price)
        product_price = re.sub(r',', '', product_price)
        product_price = float(product_price)
        product_dict[product_name] = {'Price': product_price, 'Link': link, 'Description': ''}
    
    
    print(product_dict)
       
    return product_dict

def get_links(url):
    res = request.urlopen(url)
    return list(parse_links(url, res.read()))

def get_nonlocal_links(url):
    '''Get a list of links on the page specificed by the url,
    but only keep non-local links and non self-references.
    Return a list of (link, title) pairs, just like get_links()'''

    links = get_links(url)
    filtered = []


    domain_name = urlparse(url).netloc

    for link, title in links:
        if not parse.urlparse(link).netloc == domain_name:
            filtered.append((link, title))

    return filtered

def crawl(links, within_domain, wanted_content):
    '''Crawl the url specified by `links`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `links`
    '''

    queue = Queue()
    queue.put(links)


    visited = set()
    extracted = []

    #grab the domain of the url
    domain_name = urlparse(links).netloc
    i = 0
    
    while not queue.empty() and i < 20:
        url = queue.get()
        i += 1
        #skip urls that are visited
        if url in visited:
            continue 
        try:
            req = request.urlopen(url)
            html = req.read()
        except Exception as e:
            #print(e, url)
            continue

        content_type = req.headers['Content-Type']
        if wanted_content and url != links and content_type not in wanted_content:
            continue
        

        for link, title in parse_links(url):    
            if link in visited: 
                continue   
            if within_domain and url != links and parse.urlparse(url).netloc != domain_name: #dont visit urls outside of domain if within_domain is True
                continue
            for ex in extract_information(url, html): # Is extracted supposed to follow within_domain restriction? YES If SO, uncomment the previous if statement
                if ex in extracted:
                    continue 
                extracted.append(ex)
                extractlog.debug(ex)  
         
            
            queue.put(link)

        if url != links and check_self_reference(url, links): #dont visit self referencing urls #TODO lookup hostname lookup urlparse
            continue
        if within_domain and url != links and parse.urlparse(url).netloc != domain_name: #dont visit urls outside of domain if within_domain is True
            continue
        else:
            visited.add(url) #If this comes before exception, it will be added to visited even if exception is raised
            visitlog.debug(url)


    return visited, extracted

def crawl_website(links:list, within_domain, wanted_content):
    '''Crawl the url specified by `links`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `links`
    '''

    queue = Queue()
    for link in links:
        queue.put(link)

    visited = set()
    extracted = []

    #grab the domain of the url
    #domain_name = urlparse(links[0]).netloc
    i = 0
    
    while not queue.empty() and i < 10:
        url = queue.get()
        i += 1
        #skip urls that are visited
        if url in visited:
            continue 
        try:
            req = request.urlopen(url)
            html = req.read()
        except Exception as e:
            #print(e, url)
            continue

        content_type = req.headers['Content-Type']
        '''if wanted_content and content_type not in wanted_content:
            continue'''
        
        '''for ex in extract_price(url, html): # Is extracted supposed to follow within_domain restriction? YES If SO, uncomment the previous if statement
            if ex in extracted:
                continue 
            extracted.append(ex)
            extractlog.debug(ex)'''  
        
        visited.add(url)
        visitlog.debug(url)

    return visited, extracted

def check_self_reference(url, links):
    links_domain = urlparse(links).netloc
    url_domain = urlparse(url).netloc

    links_path = urlparse(links).path
    url_path = urlparse(url).path
    
    url_fragment = urlparse(url).fragment

    if (links_domain == url_domain and links_path == url_path) and url_fragment:
        return True
    if (links_path == url_path) and url_fragment:
        return True
    if (links_domain == url_domain and links_path == url_path):
        return True
    
    if (links_path == url_path):
        return True
    
    return False

def extract_information(address, html):
    '''Extract contact information from html, returning a list of (url, category, content) pairs,
    where category is one of PHONE, ADDRESS, EMAIL'''
    
    results = []
    #extracting phone numbers and appending them to results
    for match in re.findall(r'\d\d\d-\d\d\d-\d\d\d\d', str(html)):
        results.append((address, 'PHONE', match))

    #extracting email addresses and appending them to results
    for match in re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}\b', str(html)): #r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        results.append((address, 'EMAIL', match))
    
    #extracting addresses and appending them to results
    for match in re.findall(r'(\b[A-Za-z]+(?: [A-Za-z]+)?),?\s+([A-Za-z]{2}|Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming)\s+([1-9]\d{4})(?:-\d{4})?',
                             str(html)): # #r'[a-zA-Z]+, [a-zA-Z]+ ((?!(0))[0-9]{5})'
        results.append((address, 'ADDRESS', match))

    return results

def extract_price(address, html):
    '''Extract price information from html, returning a list of (url, category, content) pairs,
    where category is one of PRICE'''

    

    results = []
    #extracting price and appending them to results
    for match in re.findall(r'\$\d+\.\d+', str(html)):
        results.append((address, 'PRICE', match))

    return results

def get_customer_info():
    with open('buy-info.txt', 'r') as f:
        return dict([line.strip().split(':') for line in f])
    
def get_seller_info():
    with open('vendors.txt', 'r') as f:
        return [line.strip() for line in f]


def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)

def parse_vendor(website, web, query):
    web.get(website)
    if website == 'https://www.ashleyfurniture.com/': #random popups
        time.sleep(12)
    else:
        time.sleep(random.randrange(5, 15))
    if website == 'https://www.ashleyfurniture.com/':
        search_shadow_root = web.find_element(By.XPATH, '//*[@id="search-container"]/wc-search').shadow_root  
        print(search_shadow_root)
        
        input = web.execute_script('''return document.querySelector('wc-search').shadowRoot.querySelector('input[role="combobox"]''')
        #search_div = search_shadow_root.find_element(By.XPATH, '//*[@id="search-container"]/wc-search//search') 
        
        #form = search_div.find_element(By.XPATH, '//*[@id="search-form"]')
        #button = form.find_element(By.XPATH, '//*[@id="search-form"]/button')
        #input = form.find_element(By.XPATH, '//*[@id="search-form"]/input')
        input.send_keys('memory foam mattress')
        time.sleep(random.randrange(1, 10))
        input.submit()
    else:
        #search_input = search_shadow_root.find_element(By.XPATH, '//*[@id="search-form"]/input')
        search_input = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['search'])
        search_input.send_keys(query)
        time.sleep(random.randrange(1, 10))
        search_input.submit()

    if website == 'https://www.mybobs.com/':
        time.sleep(10)
    
    if website == 'https://www.mybobs.com/':
        return parse_bobs_for_products(web, website)
    elif website == 'https://www.ashleyfurniture.com/':
        return parse_ashley_for_products(web, website)
    else:
        #website == 'https://www.bedbathandbeyond.com/':
        return parse_bbb_for_products(web, website)
    
def stem_words(tokens):
    stemmer = SnowballStemmer('english')
    return [stemmer.stem(word) for word in tokens]

def stop_words(tokens):
    import nltk
    from nltk.corpus import stopwords
    nltk.download('stopwords')

    stopwords = set(stopwords.words('english'))
    return [word for word in tokens if word not in stopwords]

def pre_process(tokens):
    tokens = tokens.lower() #[word.lower() for word in tokens]
    tokens = word_tokenize(tokens)
    tokens = stop_words(tokens)
    tokens = stem_words(tokens)
    return tokens

def preprocess_descriptions(website_dict): #PARAM: website_dict[website]
    import nltk
    from nltk.corpus import stopwords
    nltk.download('stopwords')

    stopwords = set(stopwords.words('english'))
    stemmer = SnowballStemmer('english')  
    for website in website_dict:
        for product in website_dict[website]:
            description = website_dict[website][product]['Description']
            description = description.lower()
            tokens = word_tokenize(description)
            tokens = [word for word in tokens if word not in stopwords]
            #tokens = [stemmer.stem(word) for word in tokens] TODO uncomment to stem words
            tokens = [word for word in tokens if word.isalpha()]
            website_dict[website][product]['Description'] = tokens
    return website_dict
        




def compute_tfidf(X_train, X_test): #PARAM: train_descriptions, test_descriptions
    vectorizer = TfidfVectorizer(max_features=75000)
    X_train = vectorizer.fit_transform(X_train).toarray()
    X_test = vectorizer.transform(X_test).toarray()
    return X_train, X_test

def query_compute_tfidf(query):
    vectorizer = TfidfVectorizer()
    query = vectorizer.fit_transform(query)
    return query


def gather_descriptions(website_dict):
    descrip_arr = []
    for website in website_dict:
        for product in website_dict[website]:
            descrip_arr.append(website_dict[website][product]['Description'])
    return list(chain.from_iterable(descrip_arr))

def gather_product_names(website_dict):
    product_arr = []
    for website in website_dict:
        for product in website_dict[website].keys():
            product_arr.append(product)
    return product_arr

def expand_query(query, description_list):
    import nltk
    from nltk.corpus import stopwords
    nltk.download('stopwords')

    stopwords = set(stopwords.words('english'))
    stemmer = SnowballStemmer('english')
    model = Word2Vec(
        sentences=description_list,
        vector_size=100,
        window=5,
        min_count=1,
        workers=4,
        epochs=10
    )
    #model.save('my_model.bin')
    #model_path = '/Users/enochappiah/school-tings/JHU/jhu-repos/irwa/irwa-hw4/final-project/trunk/vectors.bin'
    
    #model = KeyedVectors.load_word2vec_format(model_path, binary=True)
    query = query.lower()
    tokens = word_tokenize(query)
    tokens = [word for word in tokens if word not in stopwords]
    #tokens = [stemmer.stem(word) for word in tokens]
    query = tokens

    expanded_query = []
    for term in query:
        if term in model.wv:
            similar_words = model.wv.most_similar(term, topn=5)
            expanded_query.append(term)
            expanded_query.extend([word for word, _ in similar_words])
        else:
            expanded_query.append(term)
    return ' '.join(expanded_query)


def main():
    web = wd.Chrome()
    web.implicitly_wait(10)
    websites = get_seller_info()
    website_dict = {} #dictionary of websites and their product dictionary
    query = 'memory foam mattress'

    for website in websites:
        if website == 'https://www.ashleyfurniture.com/':
            break
        website_dict[website] = parse_vendor(website, web, query)
       
        for product in website_dict[website]:
            web.get(website_dict[website][product]['Link'])
            time.sleep(random.randrange(5, 15))

            description_div = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['description-div'])
            if description_div.text == '':
                description_text = description_div.find_element(By.TAG_NAME, 'p').text
            else:
                description_text = description_div.text
        
            website_dict[website][product]['Description'] = description_text
        
    #TODO PREPROCESSING DESCRIPTION DATA
        
    website_dict = preprocess_descriptions(website_dict)  
    train_descriptions = gather_descriptions(website_dict)
    train_product_names = gather_product_names(website_dict)

    #Query expansion
    expanded_query = expand_query(query, train_descriptions)
    expanded_query = ' '.join(list(set(expanded_query.split())))
    print(expanded_query)  

    #tfidf on bed bath and beyond
    #TODO GET TEST DATA (BED BATH AND BEYOND)
    test_website = "https://www.bedbathandbeyond.com/"
    website_dict[test_website] = parse_vendor(test_website, web, query)
    for product in website_dict[test_website]:
        web.get(website_dict[test_website][product]['Link'])
        time.sleep(random.randrange(5, 15))

        description_div = web.find_element(By.XPATH, vendorDict.vendors_dict[test_website]['description-div'])
        if description_div.text == '':
            description_text = description_div.find_element(By.TAG_NAME, 'p').text
        else:
            description_text = description_div.text
    
        website_dict[test_website][product]['Description'] = description_text
    


    #TODO CALL TF-IDF functions
    X_train, X_test = compute_tfidf(train_descriptions, gather_descriptions(website_dict))
    y_train, y_test = compute_tfidf(train_product_names, gather_product_names(website_dict)) #TODO: change to actual target values (product names)
    '''X_train = newsgroups_train.data
    X_test = newsgroups_test.data
    y_train = newsgroups_train.target
    y_test = newsgroups_test.target'''
    print(type(X_train), type(X_test), type(y_train), type(y_test))
    

    #Roccio Algorithm
    text_clf = Pipeline([('vect', CountVectorizer()),
                        ('tfidf', TfidfTransformer()),
                        ('clf', NearestCentroid()),
                        ])

    text_clf.fit(X_train, y_train)

    predicted = text_clf.predict(X_test)

    print(metrics.classification_report(y_test, predicted))
    #compute centroid vectors
    centroid_vectors = {}
    for c in np.unique(y_train):
        X_v = X_train[y_train == c]
        centroid_vectors[c] = np.mean(X_v, axis=0)
    
    #cosine similarity between test docs (words) and centroid vectors
    cos_scores = np.zeros((len(X_test), len(np.unique(y_train))))
    for i, x in enumerate(X_test):
        for j, (c, centroid_vector) in enumerate(centroid_vectors.items()):
            cos_scores[i, j] = cosine_similarity(x.reshape(1, -1), centroid_vector.reshape(1, -1))

    y_pred = np.argmax(cos_scores, axis=1)
    print(metrics.classification_report(y_test, y_pred))
    doc_vectors = []
    query_vectors = []

    #TODO TEST THE MODEL


    #TODO EVALUATE THE MODEL
    #TODO PRINT RESULTS

    '''
    #TODO MUST READ
    our x_train will be the product descriptions from the first two websites, our y_train will be the product name from those websites
    our x_test will be the product descriptions from the third website, our y_test will be the product name from the third website'''

    

    #print(website_dict)
    
   
    '''for 
    preprocess_description(website_dict[])'''
    #TODO START TRAINING MODEL

    
    
    


if __name__ == '__main__':
    main()