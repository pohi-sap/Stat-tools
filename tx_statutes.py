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
        #print(f'|| start tag:{tag} attr: {attrs} ||')
        #print(f'|| type start tag:{tag} attr: {type(attrs)} ||')
        if(tag == 'p' and len(attrs) > 1):
            self.alldata += '\n'

#    def handle_endtag(self, tag):
#        print(f'|| end tag:{tag} ||')
#        print("\n")

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
#Show list of sources cli
if(args.list_sources):
    for s in source:
        print(f'{source[s]} - {s}')
    sys.exit(0)

html_parser = MyHTMLParser()
source = args.source[0]
statute = args.statute[0]
section = statute.split('.')[0]
url_base_string = f'https://statutes.capitol.texas.gov/Docs/{source}/htm/{source}.{section}.htm#{statute}'

re_statute_pattern = f'name="{statute}"'

# Web request
def web_query():
    r = requests.get(url_base_string)
    r_html = r.text.split('\r') # gives statute followed by effective date, buffered by '\r\n' line between each statute

    next_row = 0
    for index, line in enumerate(r_html):
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

def download_files(url):
    response = requests.get(url)
    subdirectory = './statute_cache'

    if not os.path.isdir(subdirectory):
        os.mkdir(subdirectory)

    filename = os.path.join(subdirectory,url.split("/")[-1])
    with open(filename, mode="wb") as file:
        file.write(response.content)
    print(f"Downloaded file {filename}")

def cache_query(zipfoldername, source, statute):
    subdirectory = './statute_cache'
    filesInZip = []
    html_cache_file = ''
    # open zip first ##.htm.zip
    # open statute file next ##.###.htm
    try: 
        cachezipsourcefile = source + '.htm.zip'
        searchzipfile = source + '.' + statute.split('.')[0] + '.htm'
        with ZipFile(cachezipsourcefile, mode="r") as zfile:
            with zfile.open(searchzipfile, mode='r') as f:
                    html_cache_file = f.read() #TODO check what zfile.open gives, fix for loop.
        html_file = html_cache_file.split("\r")
        print('STATUTE FOUND IN CACHE!')
    except ValueError:
        print('ERROR: STATUTE NOT FOUND IN CACHE.')

    next_row = 0
    for index, line in enumerate(html_file):
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

make_cache()
