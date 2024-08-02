import logging
import re
import os
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random #random.randrange(5, 15)
import vendorDict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import sqlite3 



logging.basicConfig(level=logging.DEBUG, filename='output.log', filemode='w')
visitlog = logging.getLogger('visited')
extractlog = logging.getLogger('extracted')





def dataframe_to_nested_dict(df):
    # Initialize an empty dictionary
    nested_dict = {}
    
    # Iterate over the DataFrame rows
    for index, row in df.iterrows():
        website = row['Website']
        product_name = row['Product Name']
        product_details = {
            'Link': row['Link'],
            'Price': row['Price'],
            'Description': row['Description']
        }
        
        # Check if the website key already exists in the outer dictionary
        if website not in nested_dict:
            nested_dict[website] = {}
        
        
        # Add the product details to the inner dictionary
        nested_dict[website][product_name] = product_details
    
    return nested_dict

def process_product_data(website_dict, query):
    # Open a text file to write the table

    with open('product_data.txt', 'w') as file:
        # Write the header of the table
        file.write('Query\tWebsite\tProduct Name\tLink\tPrice\tDescription\n')
        
        # Prepare a list to hold data for DataFrame creation
        rows = []
        
        # Iterate over the dictionary

        for website in website_dict:
            for product in website_dict[website]:
                product_name = product
                details = website_dict[website][product]
                link = details['Link']
                price = details['Price']
                description = details['Description']
                
                # Write the row to the text file
                file.write(f'{query}\t{website}\t{product_name}\t{link}\t{price}\t{description}\n')
                
                # Append the row to the list for DataFrame
                rows.append({
                    'Query': query,
                    'Website': website,
                    'Product Name': product_name,
                    'Link': link,
                    'Price': price,
                    'Description': description
                })
    
    # Create a pandas DataFrame from the list of rows
    df = pd.DataFrame(rows, columns=['Query', 'Website', 'Product Name', 'Link', 'Price', 'Description'], )
    
    return df

def process_product_data_append(website_dict, query):
    # Open a text file to write the table
    
    with open('product_data.txt', 'a') as file:
        
        # Prepare a list to hold data for DataFrame creation
        rows = []
        
        # Iterate over the dictionary

        for website in website_dict:
            for product in website_dict[website]:
                product_name = product
                details = website_dict[website][product]
                link = details['Link']
                price = details['Price']
                description = details['Description']
                
                # Write the row to the text file
                file.write(f'{query}\t{website}\t{product_name}\t{link}\t{price}\t{description}\n')
                
                # Append the row to the list for DataFrame
                rows.append({
                    'Query': query,
                    'Website': website,
                    'Product Name': product_name,
                    'Link': link,
                    'Price': price,
                    'Description': description
                })
    
    # Create a pandas DataFrame from the list of rows
    df = pd.DataFrame(rows, columns=['Query', 'Website', 'Product Name', 'Link', 'Price', 'Description'], )
    
    return df



def scrape_descriptions(product_dict, web, website):
    for product in product_dict:
        link = product_dict[product]['Link']
        web.get(link)
        time.sleep(random.randrange(5, 15))

        description_div = WebDriverWait(web, 10).until(EC.presence_of_element_located((By.XPATH, vendorDict.vendors_dict[website]['description-div'])))
        if description_div.text == '':
            description_text = description_div.find_element(By.TAG_NAME, 'p').text
        else:
            description_text = description_div.text
        description_text = description_text.strip()
        product_dict[product]['Description'] = description_text
    return product_dict



'''def parse_bobs_for_products(web, website, cursor):

    product_dict = {}
    product_grid = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['product-grid'])
    product_cards = product_grid.find_elements(By.CLASS_NAME, vendorDict.vendors_dict[website]['product-id-class'])
    time.sleep(2)
    for product in product_cards:
        
        product_id = product.get_attribute('id')
        ActionChains(web).move_to_element(product).perform()
        
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
        
        except Exception as e:
            continue
        
        cursor.execute('INSERT INTO product_data VALUES (?, ?, ?, ?, ?, ?)', (query, website, product_name, product_link, product_price, ''))
        product_dict[product_name] = {'Price': product_price, 'Link': product_link, 'Description': ''}

    product_dict = scrape_descriptions(product_dict, web, website)
    
    return product_dict'''

def parse_bobs_for_products(web, website, cursor):

    product_dict = {}
    product_grid = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['product-grid'])
    product_cards = product_grid.find_elements(By.CLASS_NAME, vendorDict.vendors_dict[website]['product-id-class'])
    time.sleep(2)
    for product in product_cards:
        
        product_id = product.get_attribute('id')
        ActionChains(web).move_to_element(product).perform()
        
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
        
        except Exception as e:
            continue
        
        product_dict[product_name] = {'Price': product_price, 'Link': product_link, 'Description': ''}

    product_dict = scrape_descriptions(product_dict, web, website)
    
    return product_dict




def parse_bbb_for_products(web, website):

    product_dict = {}
    product_grid = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['product-grid'])
    
    product_cards = product_grid.find_elements(By.CLASS_NAME, vendorDict.vendors_dict[website]['product-cards-class'])

    product_links = []
    for product in product_cards:
        ActionChains(web).move_to_element(product).perform()
        try:
            product_link_tag = product.find_element(By.CLASS_NAME, 'productTile_link__zHGHe')
            product_link = product_link_tag.get_attribute('href')
            product_links.append(product_link)
        except Exception as e:
            continue 
          
        
    for link in product_links:
        web.get(link)
        time.sleep(5)
        product_name = WebDriverWait(web, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-wrap"]/main/div/div/div[2]/section[1]/h1'))).text
        
        try: 
            product_price = WebDriverWait(web, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="page-wrap"]/main/div/div/div[2]/section[2]/div[1]/div[2]/div[3]'))).text
            
            product_price = re.sub(r'[a-zA-Z]+', '', product_price)
            product_price = re.sub(r'\s+', '', product_price)
            product_price = re.sub(r'\$', '', product_price)
            product_price = re.sub(r',', '', product_price)
            product_price = float(product_price)

            description_div = WebDriverWait(web, 10).until(EC.presence_of_element_located((By.XPATH, vendorDict.vendors_dict[website]['description-div'])))
            if description_div.text == '':
                description_text = description_div.find_element(By.TAG_NAME, 'p').text
            else:
                description_text = description_div.text
            description_text = description_text.strip()

            product_dict[product_name] = {'Price': product_price, 'Link': link, 'Description': description_text}
        except Exception as e:
            continue
                                                                        
       
    return product_dict

def parse_ashley_for_products(web, website):

    product_dict = {}
    product_grid = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['product-grid'])
    product_cards = product_grid.find_elements(By.CLASS_NAME, vendorDict.vendors_dict[website]['product-cards-tag'])
    
    for product in product_cards:
        if len(product_dict) == 3:
            break
        try:

            product_card_parent = product.parent
            product_price = product_card_parent.get_attribute(By.CLASS_NAME, vendorDict.vendors_dict[website]['product-price-attribute'])

            id = product.get_attribute('id')
            link_element = web.find_element(By.XPATH, f'//*[@id="{id}"]/div[3]/div[1]/a') 
            product_name = link_element.text
            product_link = link_element.get_attribute('href')

            #convert price to float
            product_price = float(product_price)
 
            product_dict[product_name] = {'Price': product_price, 'Link': product_link, 'Description': ''}

        except Exception as e:
            break
       
    return product_dict

def parse_wayfair_for_products(web, website):

    product_dict = {}
    time.sleep(10)
    product_grid = web.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[2]/div[4]/div/section')
    
    #product_cards = product_grid.find_elements(By.CLASS_NAME, '_6o3atz4v _6o3atz5h _6o3atzl drvwgb7 drvwgb8 drvwgbb drvwgbe drvwgbd drvwgbh drvwgbk drvwgb1')
    product_cards = product_grid.find_elements(By.TAG_NAME, 'div')
    product_cards =[product for product in product_cards if product.get_attribute('data-hb-id') == 'Card']


  
    product_links = []
    for product in product_cards:
        ActionChains(web).move_to_element(product).perform()
        if len(product_links) == 3:
            break
        try:
            product_link_tag = product.find_element(By.TAG_NAME, 'a')
            product_link = product_link_tag.get_attribute('href')
            product_links.append(product_link)
        except Exception as e:
            continue 
          
        
    for link in product_links:
        web.get(link)
        time.sleep(5)
        product_name = WebDriverWait(web, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="bd"]/div[1]/div[2]/div/div[1]/div[1]/header/h1'))).text
        
        try: 
            product_price = WebDriverWait(web, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="bd"]/div[1]/div[2]/div/div[2]/div/div[1]/div[2]/div[1]/div/span[1]'))).text
            
            product_price = re.sub(r'[a-zA-Z]+', '', product_price)
            product_price = re.sub(r'\s+', '', product_price)
            product_price = re.sub(r'\$', '', product_price)
            product_price = re.sub(r',', '', product_price)
            product_price = float(product_price)

            description_div = WebDriverWait(web, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="CollapsePanel-0"]/div/div/div/div[1]/div/div/div')))
            if description_div.text == '':
                description_text = description_div.find_element(By.TAG_NAME, 'p').text
            else:
                description_text = description_div.text

            product_dict[product_name] = {'Price': product_price, 'Link': link, 'Description': description_text}
        except Exception as e:
            continue
                                                                        

    return product_dict

def pre_process_description(description):
    description.strip()
    description = description.lower()
    description = word_tokenize(description)
    description = [word for word in description if word not in stopwords.words('english')]
    #description = [word for word in description if word.isalpha()]
    return description

    
def get_seller_info():
    with open('vendors.txt', 'r') as f:
        return [line.strip() for line in f]


def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)

def parse_vendor(website, web, query, cursor):
    web.get(website)
    if website == 'https://www.ashleyfurniture.com/': #random popups
        time.sleep(12)
    else:
        time.sleep(random.randrange(5, 15))
    
    search_input = web.find_element(By.XPATH, vendorDict.vendors_dict[website]['search'])
    search_input.send_keys(query)
    time.sleep(random.randrange(1, 10))
    search_input.submit()

    if website == 'https://www.mybobs.com/':
        return parse_bobs_for_products(web, website, cursor)
    elif website == 'https://www.bedbathandbeyond.com/':
        return parse_bbb_for_products(web, website)
    elif website == 'https://www.wayfair.com/':
        return parse_wayfair_for_products(web, website)
    
def stem_words(tokens):
    stemmer = SnowballStemmer('english')
    return [stemmer.stem(word) for word in tokens]

def stop_words(tokens):
    from nltk.corpus import stopwords 

    stopwords = set(stopwords.words('english'))
    return [word for word in tokens if word not in stopwords]

def pre_process(tokens):
    tokens = tokens.lower() #[word.lower() for word in tokens]
    tokens = word_tokenize(tokens)
    tokens = stop_words(tokens)
    tokens = stem_words(tokens)
    return tokens

def preprocess_descriptions(website_dict): #PARAM: 
    
    from nltk.corpus import stopwords
    dict_copy = website_dict.copy()

    stopwords = set(stopwords.words('english'))
    stemmer = SnowballStemmer('english')  
    for website in dict_copy:
        for product in dict_copy[website]:
            description = dict_copy[website][product]['Description']
            description = description.lower()
            tokens = word_tokenize(description)
            tokens = [word for word in tokens if word not in stopwords]
            #tokens = [stemmer.stem(word) for word in tokens] TODO uncomment to stem words
            tokens = [word for word in tokens if word.isalpha()]
            dict_copy[website][product]['Description'] = tokens
    return dict_copy




def gather_descriptions(query,df):
    descrip_arr = []
    filtered_df = df[df['Query'] == query]
    descrip_arr = filtered_df['Description'].tolist()
   
    return descrip_arr

def expand_query(query, df):
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words('english'))
    stemmer = SnowballStemmer('english')
    #dict_copy = preprocess_descriptions(website_dict)
    filtered_df = df[df['Query'] == query]
    list = filtered_df['Description'].tolist()
    description_list = [s.split() for s in list]
    model = Word2Vec(
        sentences=description_list,
        vector_size=100,
        window=5,
        min_count=1,
        workers=4,
    )

   
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
            #print(similar_words)
        else:
            expanded_query.append(term)
    return ' '.join(expanded_query)


def pad_data(data):
    tokenized_data = [sentence.split() for sentence in data]
    all_tokens = [token for sentence in tokenized_data for token in sentence]
    encoder = LabelEncoder()
    encoder.fit(all_tokens)
    encoded_data = [encoder.transform(sentence) for sentence in tokenized_data]

    max_length = max([len(sentence) for sentence in encoded_data])
    padded_data = np.array([np.pad(sentence, (0, max_length - len(sentence)), mode='constant') for sentence in encoded_data])
    return padded_data

def get_matrix_features(data):

    tfidf_vectorizer = TfidfVectorizer()

    # Fit and transform the descriptions
    tfidf_matrix = tfidf_vectorizer.fit_transform(data)

    # Get feature names (terms)
    feature_names = tfidf_vectorizer.get_feature_names_out()

    return tfidf_matrix, feature_names, tfidf_vectorizer

 

#  Function to get TF-IDF vector representation for each term in a single document
def get_tfidf_vector_for_document(tfidf_matrix, document_index, feature_names):
    # Get the TF-IDF vector for the document
    tfidf_vector = tfidf_matrix[document_index]
    
    # Convert the TF-IDF vector to a dense array
    tfidf_array = tfidf_vector.toarray().flatten()
    
    # Create a dictionary of term: tf-idf value
    tfidf_dict = {term: tfidf_array[idx] for idx, term in enumerate(feature_names) if tfidf_array[idx] > 0}
    
    return tfidf_dict   

# Function to get TF-IDF vector for a query based on the document matrix
def get_query_vector(query, tfidf_vectorizer, feature_names):
    # Transform the query using the fitted vectorizer
    query_vector = tfidf_vectorizer.transform([query])
    
    # Convert the TF-IDF vector to a dense array
    query_array = query_vector.toarray().flatten()
    
    # Create a dictionary of term: tf-idf value
    query_dict = {term: query_array[idx] for idx, term in enumerate(feature_names) if query_array[idx] > 0}
    
    return query_dict


def main():
    conn = sqlite3.connect('product_data.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS product_data(Query TEXT, Website TEXT, Product_Name TEXT, Link TEXT, Price REAL, Description TEXT)')

    
    
    
    
    
    
    
    
    query = input('Enter a query to search for: ').strip().lower()
    websites = get_seller_info()
    website_dict = {} #dictionary of websites and their product dictionary
    if os.path.exists('product_data.txt'):
        df = pd.read_csv('product_data.txt', sep='\t')
        if query not in df['Query'].values:
            #create a new dataframe with the query
            new_dict = {}
            web = wd.Chrome()
            web.implicitly_wait(10)
            for website in websites:
                if website == 'https://www.wayfair.com/': #issue with bot detection
                    break
                new_dict[website] = parse_vendor(website, web, query, cursor)
            new_df = process_product_data_append(new_dict, query)
            df = pd.concat([df, new_df], ignore_index=True)
            web.quit()
                
    else:
        web = wd.Chrome()
        web.implicitly_wait(10)
        for website in websites:
            if website == 'https://www.wayfair.com/': #issue with bot detection
                break
            website_dict[website] = parse_vendor(website, web, query)
        web.quit()
        df = process_product_data(website_dict, query)
        
    df.dropna(inplace=True)
    website_dict = dataframe_to_nested_dict(df)



    
    descriptions_list = df['Description'].tolist()
    #descriptions_list = gather_descriptions(query, df)
    desc_matrix, desc_feature_names, tfidf_vectorizer = get_matrix_features(descriptions_list)
    desc_vectors = [get_tfidf_vector_for_document(desc_matrix, idx, desc_feature_names) for idx in range(len(descriptions_list))]
    
    expanded_query = expand_query(query, df)
    #expanded_query = ' '.join(list(set(expanded_query.split())))

    # add df to sqlite db
    for index, row in df.iterrows():
        cursor.execute('INSERT INTO product_data VALUES (?, ?, ?, ?, ?, ?)', (row['Query'], row['Website'], row['Product Name'], row['Link'], row['Price'], row['Description']))
    conn.commit()
    conn.close()


    #query_vector = get_query_vector(expanded_query, tfidf_vectorizer, desc_feature_names)
    query_vector = tfidf_vectorizer.transform([expanded_query])
 
    cosine_similarities = cosine_similarity(query_vector, desc_matrix).flatten()
    top_indices = cosine_similarities.argsort()[-10:][::-1]
    # Retrieve the top N rows from the DataFrame based on the top indices
    #top_similar_docs = df.iloc[top_indices]
    
    

    # Format the results in a readable manner
    formatted_results = []
    for idx in top_indices:
        formatted_results.append({
            'Original Query': query,
            'Expanded Query': expanded_query,
            'Website': df.iloc[idx]['Website'],
            'Product Name': df.iloc[idx]['Product Name'],
            'Link': df.iloc[idx]['Link'],
            'Price': df.iloc[idx]['Price'],
            'Description': df.iloc[idx]['Description'],
            'Similarity Score': cosine_similarities[idx]
        })
    if os.path.exists('results.txt'):
        os.remove('results.txt')
        with open('results.txt', 'w') as file:
            for i, result in enumerate(formatted_results, 1):
                file.write(f"Rank {i}:\n")
                file.write(f"Original Query: {result['Original Query']}\n")
                file.write(f"Expanded Query: {result['Expanded Query']}\n")
                file.write(f"Website: {result['Website']}\n")
                file.write(f"Product Name: {result['Product Name']}\n")
                file.write(f"Link: {result['Link']}\n")
                file.write(f"Price: {result['Price']}\n")
                file.write(f"Description: {result['Description']}\n")
            
                file.write(f"Similarity Score: {result['Similarity Score']:.4f}\n")
                file.write("\n")



    

if __name__ == '__main__':
    main()