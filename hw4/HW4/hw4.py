import logging
import re
import sys
from bs4 import BeautifulSoup
from queue import Queue
from urllib import parse, request
from urllib.parse import urlparse
import requests as res

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


def parse_links_sorted(root, html):
    # TODO: implement 
    #return a sorted list of (link, title) pairs

    return []


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
        #print("DOMAIN NAME:",domain_name)
        #print("PARSE OBJECT: ",parse.urlparse(link).netloc)
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
    
        visited.append(url)
        visitlog.debug(url)
        try:
            req = request.urlopen(url)
            html = req.read()
        except Exception as e:
            print(e, url)
            continue

        for link, title in parse_links(url, html):
                
            if link in visited: 
                continue
                
            domain_name_curr = parse.urlparse(link).netloc
            content_type = req.headers['Content-Type']
            if wanted_content and url != root and content_type not in wanted_content:
                continue
                    #don't visit self-referenceing urls
                    #print(domain_name_curr, domain_name)
            '''if domain_name_curr == domain_name and url != root:
                continue'''

            if within_domain:
                if url != root and not domain_name_curr == domain_name:
                    continue
                                             
            for ex in extract_information(url, html):
                extracted.append(ex)
                extractlog.debug(ex)   
            
            

            queue.put(link)

        

        '''except Exception as e:
            print(e, url)
            continue'''

        
        


    return visited, extracted


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
    for match in re.findall(r'[a-zA-Z][a-zA-Z]\d{5}', str(html)):
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

    wanted_content = []
    
    visited, extracted = crawl(site, False, wanted_content)
    writelines('visited.txt', visited)
    writelines('extracted.txt', extracted)


if __name__ == '__main__':
    main()