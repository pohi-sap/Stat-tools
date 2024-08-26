from html.parser import HTMLParser # ref https://docs.python.org/3/library/html.parser.html#htmlparser-methods
from concurrent.futures import ThreadPoolExecutor # parallel download
from zipfile import ZipFile # handle zip downloads.
import argparse
import requests
import sys
import re
import os

class MyHTMLParser(HTMLParser):
    alldata = ''
    def handle_starttag(self, tag, attrs):
        if(tag == 'p' and len(attrs) > 1):
            self.alldata += '\n'

    def handle_data(self, data):
        self.alldata += data 
source = {
        'The Texas Constitution': 'CN',
        'Agriculture Code': 'AG',
        'Alcoholic Beverage Code': 'AL',
        'Auxillary Water Laws': 'AL',
        'Business Organizations Code': 'BO',
        'Business and Commerce Code': 'BC',
        'Civil practice and Remedies Code': 'CP',
        'Code of Criminal Procedure': 'CR',
        'Education Code': 'ED',
        'Election Code': 'EL',
        'Estates Code': 'ES',
        'Family Code': 'FA',
        'Finance Code': 'FI',
        'Government Code': 'GV',
        'Health and Safety Code': 'HS',
        'Human Resources Code': 'HR',
        'Insurance Code - Not Codified': 'I1',
        'Insurance Code': 'IN',
        'Labor Code': 'LA',
        'Local Government Code': 'LG',
        'Natural Resources Code': 'NR',
        'Occupations Code': 'OC',
        'Parks and Wildlife Code': 'PW',
        'Penal Code': 'PE',
        'Property Code': 'PR',
        'Special District Local Laws Code': 'SD',
        'Tax Code': 'TX',
        'Transportation Code': 'TN',
        'Utilities Code': 'UT',
        'Water Code': 'WA',
        'Vernons Civil Laws': 'CV',
        }
arg_parser = argparse.ArgumentParser(
                    prog='tx_statutes',
                    description='Gets Texas Statute information for source and statute provided',
                    epilog='')

arg_parser.add_argument('-l','--list-sources',
                        action='store_true',
                    help='Shows a list of Sources to choose from.')
arg_parser.add_argument('-c','--create-cache',
                        action='store_true',
                    help='Create cache file dir \'statute_cache\' in this directory for use with local statute search')
arg_parser.add_argument('-e','--extract-cache',
                        action='store_true',
                    help='Extract ZIPS from cache folder dir \'statute_cache\' output to statute_cache_extracted')

arg_parser.add_argument('-s','--source',
                        metavar='TN', type=str, nargs=1,
                    help='Set statute source.')

arg_parser.add_argument('-t','--statute',
                        metavar='544.007', type=str, nargs=1, 
                    help='Set statute number.')
arg_parser.add_argument('-f','--format',
                        metavar='t', type=str, nargs=1, default='t',
                    help='Choose output format. [-h] html, [-t] text(Default).')
arg_parser.add_argument('-q','--query',
                        metavar='c', type=str, nargs=1, default='c',
                    help='Choose data source web or cache [-w] web request, [-c] cache(Default).')

args = arg_parser.parse_args()
html_parser = MyHTMLParser()

# Web request
def web_query():

    source = args.source[0]
    statute = args.statute[0]
    section = statute.split('.')[0]
    url_base_string = f'https://statutes.capitol.texas.gov/Docs/{source}/htm/{source}.{section}.htm#{statute}'

    re_statute_pattern = f'name="{statute}"'

    r = requests.get(url_base_string)
    r_html = r.text.split('\r') # gives statute followed by effective date, buffered by '\r\n' line between each statute

    next_row = 0
    for index, line in enumerate(r_html):
        statute_paragraph = re.search(re_statute_pattern,line)
        # ugly way to get effective date, check r_html for req get format below
        if(next_row == 1):
            if(args.format[0] == 'h'):# do this if html is requested
                print(line)
            else:
                html_parser.feed(line)
                html_parser.close()
                print(html_parser.alldata.strip())
            next_row -=1
            break
        # ^ ugly way to get effective date, check r_html for req get format above

        if(statute_paragraph): # here we used regex and found the statute.
            if(args.format[0] == 'h'): # do this if html is requested
                print(line)
            else:
                html_parser.feed(line)
                html_parser.close()
            next_row +=1 # dumb way to also get the effective date/amend info for the statute

def download_files(url):
    response = requests.get(url)
    subdirectory = './statute_cache'

    # good place to check if its already there!
    if not os.path.isdir(subdirectory):
        os.mkdir(subdirectory)

    filename = os.path.join(subdirectory,url.split("/")[-1])
    with open(filename, mode="wb") as file:
        file.write(response.content)
    print(f"Downloaded file {filename}")

def cache_query(source, statute):

    source = args.source[0]
    statute = args.statute[0]
    section = statute.split('.')[0]

    re_statute_pattern = f'name="{statute}"'

    subdirectory = './statute_cache'

    # check if we even have this yet, if not, ask to create!
    if not os.path.isdir(subdirectory):
        print('Existing statute folder not found')
        s = input('Do you want to create it now? [Y/n] ')
        if(s == 'Y' or s == 'y'):
            print('Creating cache, then continuing with searching for statute.')
            make_cache()
        else:
            print('No cache created, exiting')
            sys.exit()

    html_cache_file = ''
    # open zip first ##.htm.zip
    # open statute file next ##.###.htm
    try: 
        cachezipsourcefile = os.path.join(subdirectory, (source.upper() + '.htm.zip'))
        searchzipfile = source.lower() + '.' + section + '.htm'
        with ZipFile(cachezipsourcefile, mode="r") as zfile:
            with zfile.open(searchzipfile) as f:
                    html_cache_file = str(f.read()) 
        cached_html_file = html_cache_file.split('\\r')
    except ValueError:
        print('ERROR: STATUTE NOT FOUND IN CACHE.')

    next_row = 0
    for index, line in enumerate(cached_html_file):
        statute_paragraph = re.search(re_statute_pattern,line)
        # ugly way to get effective date, check r_html for req get format
        if(next_row == 1):
            if(args.format[0] == 'h'):
                print(line)
            else:
                html_parser.feed(line)
                html_parser.close()
                print(html_parser.alldata.strip())
            next_row -=1
            break
        if(statute_paragraph):
            if(args.format[0] == 'h'):
                print(line)
            else:
                html_parser.feed(line)
                html_parser.close()
            next_row +=1

def make_cache():
    #use https://statutes.capitol.texas.gov/Docs/Zips/SD.htm.zip
    subdirectory = './statute_cache'
    if os.path.isdir(subdirectory):
        print(f'Cache exists at {subdirectory} already, Exiting...')
        sys.exit(0)
    urls = []
    source = {
            'The Texas Constitution': 'CN',
            'Agriculture Code': 'AG',
            'Alcoholic Beverage Code': 'AL',
            'Auxillary Water Laws': 'AL',
            'Business Organizations Code': 'BO',
            'Business and Commerce Code': 'BC',
            'Civil practice and Remedies Code': 'CP',
            'Code of Criminal Procedure': 'CR',
            'Education Code': 'ED',
            'Election Code': 'EL',
            'Estates Code': 'ES',
            'Family Code': 'FA',
            'Finance Code': 'FI',
            'Government Code': 'GV',
            'Health and Safety Code': 'HS',
            'Human Resources Code': 'HR',
            'Insurance Code - Not Codified': 'I1',
            'Insurance Code': 'IN',
            'Labor Code': 'LA',
            'Local Government Code': 'LG',
            'Natural Resources Code': 'NR',
            'Occupations Code': 'OC',
            'Parks and Wildlife Code': 'PW',
            'Penal Code': 'PE',
            'Property Code': 'PR',
            'Special District Local Laws Code': 'SD',
            'Tax Code': 'TX',
            'Transportation Code': 'TN',
            'Utilities Code': 'UT',
            'Water Code': 'WA',
            'Vernons Civil Laws': 'CV',
            }
    for key, value in source.items():
        urls.append(f'https://statutes.capitol.texas.gov/Docs/Zips/{value}.htm.zip')

    with ThreadPoolExecutor() as executor:
        executor.map(download_files, urls)

    #TODO verify integrity of zip files with ZipFile.testzip() -- returns None if everything is good.

def extract_cache():
    make_cache() # ensure we even have the first download setup already.
    # make list of memebers in statute_cache
    # here would be create ZipFile.construct

    subdirectory = './statute_cache'
    subdirectory_extracted = './statute_cache_extracted'

    # good place to check if its already there!
    if os.path.isdir(subdirectory_extracted):
        print("Already have files extracted to ./statute_cache_extracted")
        sys.exit(0)

    # get files in folder
    zip_filenames = os.listdir(subdirectory)
    zip_filenames_wdir = []
    for i in zip_filenames: 
        zip_filenames_wdir.append(os.path.join(subdirectory, i))

    for index, file in enumerate(zip_filenames_wdir):
        print(f'Extracting {index}/{len(zip_filenames)} - {file} to {subdirectory_extracted}')
        with ZipFile(file, mode="r") as zfile:
            zfile.extractall(path=subdirectory_extracted)

# cli stuff here
if(args.list_sources):
    for s in source:
        print(f'{source[s]} - {s}')
    sys.exit(0)
if(args.create_cache):
    print('Creating some cache now!')
    make_cache()

if(args.extract_cache):
    extract_cache()
    sys.exit()

match (args.query[0]):
    case 'w':
        web_query()
    case 'c':
        cache_query(args.source[0], args.statute[0])
