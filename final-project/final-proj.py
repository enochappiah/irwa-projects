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

    

def parse_links(root, html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub(r'\s+', ' ', text).strip()
            yield (parse.urljoin(root, link.get('href')), text)

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


def crawl(root, within_domain, wanted_content):
    '''Crawl the url specified by `root`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `root`
    '''

    queue = Queue()
    queue.put(root)


    visited = set()
    extracted = []

    #grab the domain of the url
    domain_name = urlparse(root).netloc
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
        if wanted_content and url != root and content_type not in wanted_content:
            continue
        

        for link, title in parse_links(url):    
            if link in visited: 
                continue   
            if within_domain and url != root and parse.urlparse(url).netloc != domain_name: #dont visit urls outside of domain if within_domain is True
                continue
            for ex in extract_information(url, html): # Is extracted supposed to follow within_domain restriction? YES If SO, uncomment the previous if statement
                if ex in extracted:
                    continue 
                extracted.append(ex)
                extractlog.debug(ex)  
         
            
            queue.put(link)

        if url != root and check_self_reference(url, root): #dont visit self referencing urls #TODO lookup hostname lookup urlparse
            continue
        if within_domain and url != root and parse.urlparse(url).netloc != domain_name: #dont visit urls outside of domain if within_domain is True
            continue
        else:
            visited.add(url) #If this comes before exception, it will be added to visited even if exception is raised
            visitlog.debug(url)


    return visited, extracted

def check_self_reference(url, root):
    root_domain = urlparse(root).netloc
    url_domain = urlparse(url).netloc

    root_path = urlparse(root).path
    url_path = urlparse(url).path
    
    url_fragment = urlparse(url).fragment

    if (root_domain == url_domain and root_path == url_path) and url_fragment:
        return True
    if (root_path == url_path) and url_fragment:
        return True
    if (root_domain == url_domain and root_path == url_path):
        return True
    
    if (root_path == url_path):
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
                
        print(product_links)
        
    '''for key in product_links:
        web.get(product_links[key])
        time.sleep(random.randrange(1, 10))
        
        add_to_cart = web.find_element(By.XPATH, '/html/body/main/div[2]/div[2]/section/div[2]/div/div[3]/div[2]/div[2]/ul[1]/li[1]/div[2]/div/div/form/input[5]')
        add_to_cart.submit()
        time.sleep(10)
        checkout = web.find_element(By.XPATH, '/html/body/div[32]/div/div/div[2]/div[3]/div/div[5]/div[1]/a')
        web.get(checkout)
        time.sleep(9)'''

        
   
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