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
        if(tag == 'p' and len(attrs) > 1): # we 'break' on p tags because statutes are separtaed into <p> tags, then len check cuts out white space of the output.
            self.alldata += '\n'

    def handle_data(self, data):
        self.alldata += data 

# Web request
def web_query(source : str, statute : str) -> str:
    """
    Given inputs, performs https request to return statute and effective date in html
    """

    section = statute.split('.')[0]
    url_base_string = f'https://statutes.capitol.texas.gov/Docs/{source}/htm/{source}.{section}.htm#{statute}'

    re_statute_pattern = f'name="{statute}"'

    r = requests.get(url_base_string)
    r_html = r.text.split('\r') # gives statute followed by effective date, buffered by '\r\n' line between each statute

    for index, line in enumerate(r_html):
        statute_paragraph = re.search(re_statute_pattern,line)

        if(statute_paragraph):
            statute_html = r_html[index]
            statute_effective_date_html = r_html[index + 1]

            return statute_html, statute_effective_date_html 

    else: return None, None
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

def cache_query_zip(source : str, statute : str) -> str:
    """
    Given inputs, performs local lookup in zip files to return statute and effective date in html
    """

    section = statute.split('.')[0]

    re_statute_pattern = f'name="{statute}"'

    subdirectory = './statute_cache'

    cached_html_file = ''
    statute_html = ''
    statute_effective_date_html = ''

    # check if we even have this yet, if not, ask to create!
    if not os.path.isdir(subdirectory):
        print('Existing statute cache folder not found')
        s = input('Do you want to create it now? ~38MB [Y/n] ')
        if(s == 'Y' or s == 'y'):
            print('Creating cache, then continuing with searching for statute.')
            make_cache()
        else:
            print('No cache created, exiting')
            sys.exit(0)

    try: 
        cachezipsourcefile = os.path.join(subdirectory, (source.upper() + '.htm.zip'))
        searchzipfile = source.lower() + '.' + section + '.htm'
        with ZipFile(cachezipsourcefile, mode="r") as zfile:
            with zfile.open(searchzipfile) as f:
                    html_cache_page = str(f.read()).replace('\\n', '') # im getting extra \n not sure why here.
        cached_html_file = html_cache_page.split('\\r')
    except ValueError:
        print('ERROR: STATUTE NOT FOUND IN CACHE.')

    for index, line in enumerate(cached_html_file):
        statute_paragraph = re.search(re_statute_pattern,line)

        if(statute_paragraph):
            statute_html = cached_html_file[index]
            statute_effective_date_html = cached_html_file[index + 1]

            return statute_html, statute_effective_date_html 

    else: return None, None


def cache_query_dir(source : str, statute : str) -> str:
    """
    Given inputs, performs local lookup in expanded files to return statute and effective date in html
    """

    subdirectory = './statute_cache_extracted'

    html_cache_file = ''
    section = statute.split('.')[0]
    re_statute_pattern = f'name="{statute}"'

    # check if we even have this yet, if not, ask to create!
    if not os.path.isdir(subdirectory):

        print('Existing zip-expanded statute folder {} not found'.format(subdirectory))
        s = input('Do you want to create the zip-expanded directory {} with statute zip files now? ~199MB [Y/n] '.format(subdirectory))

        if(s == 'Y' or s == 'y'):
            print('Creating cache, then continuing with searching for statute.')
            extract_cache()

        else:
            print('No cache created, exiting')
            sys.exit(0)

    try: 
        searchzipfile = os.path.join(subdirectory, (source.lower() + '.' + section + '.htm'))

        with open(searchzipfile) as f:
                html_cache_file = f.read()
        cached_html_file = html_cache_file.split('\n')
    except ValueError:
        print('ERROR: STATUTE NOT FOUND IN dir CACHE.')

    for index, line in enumerate(cached_html_file):
        statute_paragraph = re.search(re_statute_pattern,line)

        if(statute_paragraph):
            statute_html = cached_html_file[index]
            statute_effective_date_html = cached_html_file[index + 1]

            return statute_html, statute_effective_date_html 

    else: return None, None

def make_cache():
    #use 'https://statutes.capitol.texas.gov/Docs/Zips/SD.htm.zip' for reference
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

    subdirectory = './statute_cache'
    subdirectory_extracted = './statute_cache_extracted'

    if not os.path.isdir(subdirectory):
        print(f'Existing statute cache folder {subdirectory} not found')
        s = input('Do you want to create it now? ~38MB [Y/n] ')
        if(s == 'Y' or s == 'y'):
            print(f'Creating cache, then continuing with extracting statute htm pages to {subdirectory_extracted}.')
            make_cache()
        else:
            print('No cache created, exiting')
            sys.exit(0)

    if os.path.isdir(subdirectory_extracted):
        print(f'Already have existing directory {subdirectory_extracted}, exiting!')
        sys.exit(0)

    # get files in folder
    zip_filenames = os.listdir(subdirectory)
    zip_filenames_wdir = []
    for i in zip_filenames: 
        zip_filenames_wdir.append(os.path.join(subdirectory, i))

    for index, file in enumerate(zip_filenames_wdir):
        print(f'Extracting {index + 1}/{len(zip_filenames)} - {file} to {subdirectory_extracted}')
        with ZipFile(file, mode="r") as zfile:
            zfile.extractall(path=subdirectory_extracted)

def convert_text_to_sql(statute_text: str) -> tuple[list[str], int, str]:
    """
    Transforms text to a list of SQL inserted as rows.

    Args:
        statute_text (str): The text to be transformed.

    Returns:
        tuple[list[str], int, str]: A tuple containing the formatted statute,
            the row count, and the CSV-formatted subsections.
    """

    # Define patterns for matching parentheses
    subsections_pattern = r'\(([^)]+)\)'
    # Split the text into lines
    lines = [line.strip() for line in statute_text.split('\n') if line]
    statute_title = ''

    # Find subsections
    subsections = []
    for line in lines:
        match = re.search(subsections_pattern, line)
        if match:
            subsections.append(match.group(1))

    # Join subsections into a CSV-formatted string
    csv_subsections = ','.join(subsections)

    # Find Statute title using regex

    #raw string format                              r
    #Match sec follow by stat digits and period     'Sec.*\d+\.\d+\.
    #match min spaces                               \s+
    #match uppercase words, spaces and hyphen       ([A-Z -]+)
    #end match on period                            \.'

    statute_title_pattern = r'Sec.*\d+\.\d+\.\s+([A-Z -]+)\.'

    for ln in lines[:3]:
        match = re.search(statute_title_pattern, ln)
        if match:
            statute_title = match.group(1)


    return lines, len(lines), statute_title, csv_subsections

def output_conversion(input_html : str, _format : str) -> str:
    match (_format):
        case 'text':
            html_parser = MyHTMLParser()
            html_parser.feed(input_html)
            text = html_parser.alldata
            return text
        case 'h':
            return input_html
        case 'sqlite':
            # best would be list or dict that has statute title and subsections divided out the correct way.
            return "sqlite formatting here :)"


# cli stuff here
def main():



    source = { 'The Texas Constitution': 'CN', 'Agriculture Code': 'AG', 'Alcoholic Beverage Code': 'AL', 'Auxillary Water Laws': 'AL', 'Business Organizations Code': 'BO', 'Business and Commerce Code': 'BC', 'Civil practice and Remedies Code': 'CP', 'Code of Criminal Procedure': 'CR', 'Education Code': 'ED', 'Election Code': 'EL', 'Estates Code': 'ES', 'Family Code': 'FA', 'Finance Code': 'FI', 'Government Code': 'GV', 'Health and Safety Code': 'HS', 'Human Resources Code': 'HR', 'Insurance Code - Not Codified': 'I1', 'Insurance Code': 'IN', 'Labor Code': 'LA', 'Local Government Code': 'LG', 'Natural Resources Code': 'NR', 'Occupations Code': 'OC', 'Parks and Wildlife Code': 'PW', 'Penal Code': 'PE', 'Property Code': 'PR', 'Special District Local Laws Code': 'SD', 'Tax Code': 'TX', 'Transportation Code': 'TN', 'Utilities Code': 'UT', 'Water Code': 'WA', 'Vernons Civil Laws': 'CV', }

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
                            metavar='czip', type=str, nargs=1, default=['czip'],
                        help='Choose data source web or cache [-w] web request, [-czip] cache zip directory(Default) [-cdir] cache unzipped directory.')

    args = arg_parser.parse_args()

# Control for flags

    if (not len(sys.argv) > 1):
        arg_parser.print_help()
        sys.exit(0)

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
            statute, eff_date = web_query(args.source[0], args.statute[0])
            #print(output_conversion(statute,'text'))
            #print()
            #print(output_conversion(eff_date,'text'))
            
            l, sl, subsec = convert_text_to_sql(output_conversion(statute,'text'))
            print(sl)
            for i, _ in enumerate(l):
                print('{}:{}'.format(i,_))
            print(subsec)

        case 'czip':
            statute, eff_date = cache_query_zip(args.source[0], args.statute[0])
            #print(output_conversion(statute,'text'))
            #print()
            #print(output_conversion(eff_date,'text'))

            l, sl, statute_title, subsec = convert_text_to_sql(output_conversion(statute,'text'))
            print(sl)
            for i, _ in enumerate(l):
                print('{}:{}'.format(i,_))
            print(f'Statute Title: {statute_title}')
            print(f'Statute Subsections: {subsec}')


        case 'cdir':
            statute, eff_date = cache_query_dir(args.source[0], args.statute[0])
            print(output_conversion(statute,'text'))
            print()
            print(output_conversion(eff_date,'text'))

if __name__ == '__main__':
    main()
