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
        if not parse.urlparse(link).netloc == domain_name:
            filtered.append((link, title))

        #if link.startswith(url):
         #   continue


    return filtered


def crawl(root, wanted_content=[], within_domain=True):
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

    while not queue.empty():
        url = queue.get()
        #skip urls that are visited
        if url in visited:
            continue
        try:
            req = request.urlopen(url)
            html = req.read()

            
           #grab current domain name
            domain_name_curr = urlparse(url).netloc

            #grab content type from url
            content_type = req.headers['Content-Type']
            if content_type not in wanted_content and url != root:
                continue

            #don't visit self-referenceing urls
            if domain_name_curr.startswith(domain_name) and url != root:
                continue
            
            #only visit urls within the domain
            if within_domain:
                if not domain_name_curr.startswith(domain_name) and url != root:
                    continue
        
            

            visited.append(url)
            visitlog.debug(url)

            for ex in extract_information(url, html):
                extracted.append(ex)
                extractlog.debug(ex)

            for link, title in parse_links(url, html):
                queue.put(link)

        except Exception as e:
            print(e, url)

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

    visited, extracted = crawl(site, within_domain=False)
    writelines('visited.txt', visited)
    writelines('extracted.txt', extracted)


if __name__ == '__main__':
    main()