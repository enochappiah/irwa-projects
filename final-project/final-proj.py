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
import random #random.randrange(5.0, 15.0)

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

def parse_website_for_price(url):
    soup = BeautifulSoup(request.urlopen(url).read(), 'html.parser')
    price = soup.find('span', {'class': 'price'}).text
    return price

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
    book_websites = get_seller_info()
    book_matches = {}
    product_links = {}
    for i in range(len(book_websites)):
        
        web.get(book_websites[i])
        time.sleep(random.randrange(1, 5))
        
        # wait for an alert to appear and then dismiss it
        try:
            alert = web.switch_to.alert
            alert.dismiss()
        except:
            pass
        
        # get all forms on the page and iterate through the forms to find a form with the class name that contains 'search'
        input_divs = web.find_elements(By.TAG_NAME, 'input')
        for input in input_divs:
            if 'search' in input.get_attribute('class').lower() or 'search' in input.get_attribute('placeholder').lower():
                search_input = input
                break

        search_input.send_keys('memory foam mattress')
        time.sleep(random.randrange(1, 10))
        search_input.submit()
        time.sleep(10)
        '''forms = web.find_elements(By.TAG_NAME, 'input')
        for form in forms:
            if 'search' in form.get_attribute('class'):
                search_input = form
                break
        
        search_input.find_element(By.TAG_NAME, 'input').send_keys('memory foam mattress')
        time.sleep(random.randrange(1, 10))
        search_input.find_element(By.TAG_NAME, 'button').click()
        time.sleep(random.randrange(1, 10))'''

        links = web.find_elements(By.TAG_NAME, 'a')
        j = 0
        for link in links:
            if j < 11 and ('product' in link.get_attribute('class').lower() or 'product-link' in link.get_attribute('class').lower()):
                if book_websites[i] not in product_links:
                    product_links[book_websites[i]] = []
                if link.get_attribute('href') not in product_links[book_websites[i]]:
                    product_links[book_websites[i]].append(link.get_attribute('href'))
                    j += 1
                #TODO later create a dictionary for each product link with classifications(keywords description, color, type) as key and product details as value 
                book_matches[book_websites[i]] = extract_price(link.get_attribute('href'), web.page_source)
    print(book_matches)     
    '''for key in product_links:
        web.get(product_links[key])
        time.sleep(random.randrange(1, 10))
        
        add_to_cart = web.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/section/div[2]/div/div[3]/div[2]/div[2]/ul[1]/li[1]/div[2]/div/div/form/input[5]')
        add_to_cart.submit()
        time.sleep(10)
        checkout = web.find_element(By.XPATH, '/html/body/div[32]/div/div/div[2]/div[3]/div/div[5]/div[1]/a')
        web.get(checkout)
        time.sleep(9)'''
    results = []
    visited = []
    for website in product_links:

        for link in product_links[website]:
            
            print("LINK:", link)
            time.sleep(random.randrange(1, 10))
            web.get(link)
            visited = crawl_website(product_links[website], True, ['text/html'])
            #print(web.get(link).page_source)
            #results = extract_price(link, web.page_source)
            
            
    writelines('extracted.txt', results) 
   
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