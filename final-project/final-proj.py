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
import html5lib


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

def parse_website_for_price(web):
    price_dict = {}
    '''soup = BeautifulSoup(request.urlopen(url).read(), 'html.parser') #html.parser
    print(soup.prettify())
    for links in soup.find_all(vendorDict.bobs_dict['price-container-tag'], limit=10):
        print(links)
        price = links.find(vendorDict.bobs_dict['price-container_tag']).text
        price_dict[links] = links.find('_ngcontent-serverapp-c411').text                           #links.find('span', class_='price').text
        print(price)'''
    product_grid = web.find_element(By.XPATH, vendorDict.bobs_dict['product-grid'])
    product_cards = product_grid.find_elements(By.TAG_NAME, vendorDict.bobs_dict['product-cards-tag'])
    
    
    for product in product_cards:
        
        product_id = product.find_element(By.CLASS_NAME,'bobs-product-card-dynamic-load').get_attribute('id')

        try:
            #print("Product Name: ", product.find_element(By.XPATH, f'//*[@id="{product_id}"]/div/bobs-generic-link/div/a/div').text)
            product_name = product.find_element(By.XPATH, f'//*[@id="{product_id}"]/div/bobs-generic-link/div/a/div').text
            #price_dict[product_name] = {}
            

            #print("Product Price: ", product.find_element(By.XPATH, f'//*[@id="{product_id}"]/div/div[4]/div[2]/div').text)
            product_price = product.find_element(By.XPATH, f'//*[@id="{product_id}"]/div/div[4]/div[2]/div').text
            
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
            #price_dict[product_name] = {'Price': product_price}

            
            #print("Product link: ", product.find_element(By.XPATH, f'//*[@id="{product_id}"]/div/bobs-generic-link/div/a').get_attribute('href')) # product.find_element(By.CLASS_NAME, vendorDict.bobs_dict['product-link-class']).get_attribute('href')
            product_link = product.find_element(By.XPATH, f'//*[@id="{product_id}"]/div/bobs-generic-link/div/a').get_attribute('href')
            price_dict[product_name] = {'Price': product_price, 'Link': product_link, 'Description': ''}
            #print(price_dict)
        except Exception as e:
            break


    '''for i in range(1, 11):
        
        product_id = product_cards[i].find_element(By.CLASS_NAME,'bobs-product-card-dynamic-load').get_attribute('id')

        try:
            print("Product Name: ", product_cards[i].find_element(By.XPATH, f'//*[@id="{product_id}"]/div/bobs-generic-link/div/a/div').text)
            print("Product Price: ", product_cards[i].find_element(By.XPATH, f'//*[@id="{product_id}"]/div/div[4]/div[2]/div').text)
            print("Product link: ", product_cards[i].find_element(By.XPATH, f'//*[@id="{product_id}"]/div/bobs-generic-link/div/a').get_attribute('href')) # product.find_element(By.CLASS_NAME, vendorDict.bobs_dict['product-link-class']).get_attribute('href')

        except Exception as e:
            continue'''
        
      
    
       
    return price_dict

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
    with open('book-sellers.txt', 'r') as f:
        return [line.strip() for line in f]


def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)


def main():
    web = wd.Chrome()
    web.implicitly_wait(10)
    websites = get_seller_info()
    results = {}
    

    for link in websites:
        web.get(link)
        time.sleep(random.randrange(5, 15))
        search_input = web.find_element(By.XPATH, vendorDict.bobs_dict['search'])
        search_input.send_keys('memory foam mattress')
        time.sleep(random.randrange(1, 10))
        search_input.submit()
        time.sleep(10)
        results[link] = parse_website_for_price(web)
        
        for products_key in results[link]:
            web.get(results[link][products_key]['Link'])
            time.sleep(random.randrange(5, 15))

            #description_div = web.find_element(By.CLASS_NAME, 'description-summary bobs-text-small')
            description_div = web.find_element(By.XPATH, '//*[@id="bobs-product-details-tabs"]/bobs-tabs/bobs-tab[1]/div/bobs-product-details-tab-content/div[1]/div[1]/span[2]')
            if description_div.text == '':
                description_text = description_div.find_element(By.TAG_NAME, 'p').text
            else:
                description_text = description_div.text
         
                
            #description_div = web.find_element(By.CLASS_NAME, 'description-summary bobs-text-small')
            #description_text = description_div.find_element(By.TAG_NAME, 'p').text
            
            results[link][products_key]['Description'] = description_text
            
        print(results)
    
   
    '''site = sys.argv[1]

    links = get_links(site)
    writelines('links.txt', links)

    nonlocal_links = get_nonlocal_links(site)
    writelines('nonlocal.txt', nonlocal_links)

    wanted_content = [] #'text/html', 'application/pdf', 'application/zip'
    
    visited, extracted = crawl(site, False, wanted_content)
    writelines('visited.txt', visited)
    writelines('extracted.txt', extracted)'''


if __name__ == '__main__':
    main()