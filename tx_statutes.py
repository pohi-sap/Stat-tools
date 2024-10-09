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
        if(tag == 'p'): # we 'break' on p tags because statutes are separtaed into <p> tags
            self.alldata += '\n'
        if(tag == 'tr'): # we format on table tags because of TX 11.22, see issues #6
            self.alldata += '\n'

    # include <br> for formatting.
    def handle_startendtag(self, tag, attrs):
        if(tag == 'br'): 
            self.alldata += '\n'

    # Mostly for tables at the moment.
    def handle_endtag(self, tag):
        if(tag == 'td'): # we format on table tags because of TX 11.22, see issue #6
            self.alldata += '\t'
        if(tag == 'table'):
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

    print('Source \'{}\' and statute \'{}\' did not yield any results'.format(source,statute))
    sys.exit(1)


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
            # allfiles -> dict map lower() to actual file name
            file_name_lower_to_actual_mapping = dict()
            for file in zfile.namelist():
                file_name_lower_to_actual_mapping[file.lower()] = file

            with zfile.open(file_name_lower_to_actual_mapping[searchzipfile]) as f:
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
    print('Source \'{}\' and statute \'{}\' did not yield any results'.format(source,statute))
    sys.exit(1)

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
        flatdir_file_lower = (source.lower() + '.' + section + '.htm')

        # allfiles -> dict map lower() to actual file name
        file_name_lower_to_actual_mapping = dict()
        for file in os.listdir(subdirectory):
            file_name_lower_to_actual_mapping[file.lower()] = file

        # use dict mapping to avoid case sensitive search
        actual_file_name = os.path.join(subdirectory, file_name_lower_to_actual_mapping[flatdir_file_lower])

        with open(actual_file_name) as f:
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

    else: 
        print('Source \'{}\' and statute \'{}\' did not yield any results'.format(source,statute))
        sys.exit(1)

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

    #sqlite_obj = dict()
    #sqlite_obj['title'] = ''
    #sqlite_obj['line_count'] = int(0)
    #sqlite_obj['subsections_cvs'] = []
    #sqlite_obj['lines_formatted'] = {}

    # Split the text into lines
    lines = [line.strip() for line in statute_text.split('\n') if line]
    statute_title = ''
    subsection_text = []

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
            subsection_text.append(line[(match.end()+1):])

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
                                            ([A-Z0-9 -;:]+) # This is title of statute, has spaces and sometimes hyphens!
                                            \.""", re.X)

    for ln in lines:
        match = statute_title_re.search(ln)
        if match:
            statute_title = match.group(1)
            break
    if(len(lines) == 1):
        match = statute_title_re.search(lines[0])
        print('Positions Start: {} end: {} '.format(match.start(),match.end()))
        if match:
            lines[0] = lines[0][match.end():]


    return lines, len(lines), statute_title, subsections, subsection_text

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
                            metavar='text', type=str, nargs=1, default=['text'],
                        help='Choose output format, [-f html], [-f text] text(Default).')
    arg_parser.add_argument('-q','--query',
                            metavar='cache-zip', type=str, nargs=1, default=['cache-zip'],
                        help='Choose data source, [-q web] web request or [-q cache-zip] cache zip directory(Default), [-q cache-flatdir] cache unzipped directory.')

    args = arg_parser.parse_args()


# Control for flags
    if (not len(sys.argv) > 1):
        arg_parser.print_help()
        sys.exit(1)

    if(args.list_sources):
        for s in source:
            print(f'{source[s]} - {s}')
        sys.exit(0)
    if(args.create_cache):
        print('Creating some cache now!')
        make_cache()

    if(args.extract_cache):
        extract_cache()
        sys.exit(0)

# min validation

    if args.source[0].upper() not in source.values():
        print("{} was not found in Statute sources list, please try 'python tx_statutes -l".format(args.source[0]))
        sys.exit(1)

    query_types = ['web','cache-zip','cache-flatdir']

    if args.query[0] not in query_types:
        print("\'{}\' is an invalid query type, please try \'--query cache-flatdir\'".format(args.query[0]))
        sys.exit(1)

    format_types = ['text','html']

    if args.format[0] not in format_types:
        print("\'{}\' is an invalid output format, please try \'--format text\' or \'--format html\'".format(args.format[0]))
        sys.exit(1)




    match (args.query[0]):
        case 'web':
            statute_html, eff_date_html = web_query(args.source[0], args.statute[0])
            print(output_conversion(statute_html,args.format[0]))
            print()
            print(output_conversion(eff_date_html,args.format[0]))

        case 'cache-zip':
            statute_html, eff_date_html = cache_query_zip(args.source[0], args.statute[0])

            lines, line_len, stat_title, subsections_csv_format, subsection_text = convert_text_to_sql(output_conversion(statute_html,'text'))
            eff_date = output_conversion(eff_date_html,'text')
            #for _ in lines:
                #print(_)
            print('Statute Title: {}'.format(stat_title))

            if(len(lines) == 1):
                print('Statute text:{}'.format(lines[0]))
            elif (len(subsections_csv_format) < 1):
                for _ in range(0,len(lines)):
                    print('{}'.format(lines[_]))
            else:
                for _ in range(0,len(subsections_csv_format)):
                    print('{}:{}'.format(subsections_csv_format[_], subsection_text[_]))

            print('lines length: {}'.format(line_len),'Subsections: {} Subsec count:len({})'.format(subsections_csv_format,len(subsections_csv_format)), sep='\n')

        case 'cache-flatdir':
            statute_html, eff_date_html = cache_query_dir(args.source[0], args.statute[0])
            print(output_conversion(statute_html,args.format[0]))
            print()
            print(output_conversion(eff_date_html,args.format[0]))

if __name__ == '__main__':
    main()
