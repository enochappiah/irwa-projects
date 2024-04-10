import logging
import re
import sys
from bs4 import BeautifulSoup
from queue import Queue
from urllib import parse, request
from urllib.parse import urlparse
import requests as res
import requests
import os
import time

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

def last_modified(url,):
    try:
        response = requests.head(url)  # Send a HEAD request to fetch only the headers
        last_modified = response.headers.get('Last-Modified')
        if last_modified:
            return last_modified
        else:
            return "Last-Modified header not found"
    except requests.RequestException as e:
        return f"Error: {e}"
    #he mentioned pagerank, which i also saw can work to sort the links so i can ask about the implementation of that


def parse_links_sorted(root, html):
    # TODO: implement 
    #return a sorted list of (link, title) pairs
    sorted_links = []
    #APPARENTLY OUR SELF-REFERENCES PART MIGHT BE WRONG

    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub(r'\s+', ' ', text).strip()
            last_modified_date = last_modified(parse.urljoin(root, link.get('href')))
    
            sorted_links.append(parse.urljoin(root, link.get('href')), text, last_modified_date)
    
    return sorted_links.sort(key=lambda a: a[2])



def get_links(url):
    res = request.urlopen(url)
    return list(parse_links(url, res.read()))


def get_nonlocal_links(url):
    '''Get a list of links on the page specificed by the url,
    but only keep non-local links and non self-references.
    Return a list of (link, title) pairs, just like get_links()'''

    # TODO: implement
    links = get_links(url)
    filtered = []

    #grab the domain of the url
    domain_name = urlparse(url).netloc
    
    

    for link, title in links:
        if not parse.urlparse(link).netloc == domain_name:
            filtered.append((link, title))

        #if link.startswith(url):
         #   continue
            


    return filtered


def crawl(root, within_domain, wanted_content):
    '''Crawl the url specified by `root`.
    `wanted_content` is a list of content types to crawl
    `within_domain` specifies whether the crawler should limit itself to the domain of `root`
    '''
    # TODO: implement


    queue = Queue()
    queue.put(root)

    visited = []
    extracted = []

    #grab the domain of the url
    domain_name = urlparse(root).netloc
    i = 0
    
    while not queue.empty() and i < 50:
        url = queue.get()
        i += 1
        #skip urls that are visited
        if url in visited:
            continue 
        try:
            req = request.urlopen(url)
            html = req.read()
        except Exception as e:
            print(e, url)
            continue

        content_type = req.headers['Content-Type']
        if wanted_content and url != root and content_type not in wanted_content:
            continue

        for link, title in parse_links(url, html):    
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
            visited.append(url) #If this comes before exception, it will be added to visited even if exception is raised
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
    
    # TODO: implement
    results = []
    #extracting phone numbers and appending them to results
    for match in re.findall(r'\d\d\d-\d\d\d-\d\d\d\d', str(html)):
        results.append((address, 'PHONE', match))

    #extracting email addresses and appending them to results
    for match in re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', str(html)):
        results.append((address, 'EMAIL', match))
    
    #extracting addresses and appending them to results
    for match in re.findall(r'[a-zA-Z]+, [a-zA-Z]+ \d{5}', str(html)): 
        results.append((address, 'ADDRESS', match))

    return results


def writelines(filename, data):
    with open(filename, 'w') as fout:
        for d in data:
            print(d, file=fout)


def main():
    site = sys.argv[1]

    links = get_links(site)
    writelines('links.txt', links)

    nonlocal_links = get_nonlocal_links(site)
    writelines('nonlocal.txt', nonlocal_links)

    wanted_content = [] #'text/html', 'application/pdf', 'application/zip'
    
    visited, extracted = crawl(site, False, wanted_content)
    writelines('visited.txt', visited)
    writelines('extracted.txt', extracted)


if __name__ == '__main__':
    main()