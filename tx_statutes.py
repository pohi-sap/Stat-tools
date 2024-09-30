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
        #if(tag == 'p' and len(attrs) > 1): # we 'break' on p tags because statutes are separtaed into <p> tags, then len check cuts out white space of the output.
        if(tag == 'p'): # we 'break' on p tags because statutes are separtaed into <p> tags
            self.alldata += '\n'

    # include <br> for formatting.
    def handle_startendtag(self, tag, attrs):
        if(tag == 'br'): # we 'break' on p tags because statutes are separtaed into <p> tags, then len check cuts out white space of the output.
            self.alldata += '\n'

    #try to structure tables correctly.
    #def handle_endtag(self, tag):
    #    if(tag == 'th'): # we format on table tags because of TX 11.22
    #        self.alldata += '\t'

    # This has no effect, missing attrs so it doesnt actually perform action of appending \t to the html.
    #def handle_endtag(self, tag):
    #    if(tag == 'td'): # we format on table tags because of TX 11.22
    #        self.alldata += '\t'
    

    # this doesnt work, i dont know why and it makes me sad :(
    # starttag,     +attrs formats the table, ish, but ruins the rest of the output, 
    # starttag,     -attrs Type error here, says the thing is expecting 3 args.
    # endttag,      +attrs does not format the table, but rest of the output is NOT ruined.
    # endttag,      -attrs no tabs added to table.

    #include table formatting.
    def handle_endtag(self, tag, attrs):
        if(tag == 'tr'): # we format on table tags because of TX 11.22
            self.alldata += '\n'

    def handle_endtag(self, tag):
        if(tag == 'td'): # we format on table tags because of TX 11.22
            self.alldata += '\t'

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
                html_cache_page = str(f.read()).replace('\\n', '').replace(r"\'","'") # im getting extra \n not sure why here. # replace \' also messing things up for me, personally >:|
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

    # Split the text into lines
    lines = [line.strip() for line in statute_text.split('\n') if line]
    statute_title = ''

    # regex, explained
    subsections_re = re.compile(r"""\(                      # find first open parenthesis
                                            (               # start group
                                            [^)]+           # include anything that is not a closing parenthesis
                                            )               # close group :)
                                            \)""", re.X)    # end on closed parenthesis

    # Find subsections
    subsections = []
    for line in lines:
        match = subsections_re.search(line)
        if match:
            subsections.append(match.group(1))

    # Join subsections into a CSV-formatted string
    csv_subsections = ','.join(subsections)

    # Find Statute title using regex

    # regex, explained
    statute_title_re = re.compile(r"""Sec.*     # Look for 'Sec'
                                            \d+ # Check for first part of statute number
                                            \.  # statute number separated by '.'
                                            \d+ # End part of statute number
                                            \.  # Statute is followed by a '.'
                                            \s+ # Fly through any spaces
                                            ([A-Z -]+) # This is title of statute, has spaces and sometimes hyphens!
                                            \.""", re.X)

    for ln in lines:
        match = statute_title_re.search(ln)
        if match:
            statute_title = match.group(1)
            break


    return lines, len(lines), statute_title, csv_subsections

def output_conversion(input_html : str, _format : str) -> str:
    match (_format):
        case 'text':
            html_parser = MyHTMLParser()
            html_parser.feed(input_html)
            text = html_parser.alldata
            return text
        case 'html':
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
                        help='Shows a list of Texas Statute Sources to use.')
    arg_parser.add_argument('-c','--create-cache',
                            action='store_true',
                        help='Create cache file dir \'statute_cache\' in this directory for use with local statute search')
    arg_parser.add_argument('-e','--extract-cache',
                            action='store_true',
                        help='Extract ZIPS from cache folder dir \'statute_cache\' and outputs to statute_cache_extracted')

    arg_parser.add_argument('-s','--source',
                            metavar='TN', type=str, nargs=1,
                        help='Set statute source.')

    arg_parser.add_argument('-t','--statute',
                            metavar='544.007', type=str, nargs=1, 
                        help='Set statute number.')
    arg_parser.add_argument('-f','--format',
                            metavar='t', type=str, nargs=1, default='t',
                        help='Choose output format, [-f html], [-f t] text(Default).')
    arg_parser.add_argument('-q','--query',
                            metavar='czip', type=str, nargs=1, default=['czip'],
                        help='Choose data source, [-q w] web request or [-q czip] cache zip directory(Default), [-q cdir] cache unzipped directory.')

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
        case 'web':
            statute, eff_date = web_query(args.source[0], args.statute[0])
            print(output_conversion(statute,'text'))
            print()
            print(output_conversion(eff_date,'text'))
            

        case 'cache-zip':
            statute, eff_date = cache_query_zip(args.source[0], args.statute[0])
            print(output_conversion(statute,'text'))
            print()
            print(output_conversion(eff_date,'text'))


        case 'cache-flatdir':
            statute, eff_date = cache_query_dir(args.source[0], args.statute[0])
            print(output_conversion(statute,'text'))
            print()
            print(output_conversion(eff_date,'text'))

if __name__ == '__main__':
    main()
