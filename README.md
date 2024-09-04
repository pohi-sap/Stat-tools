# Stat-tools
tx_statutes.py - Tools for getting text or html of Texas Statutes.
Planned features: jq output (involved for my skills at the moment.)
Example use:
```bash
usage: tx_statutes [-h] [-l] [-c] [-e] [-s TN] [-t 544.007] [-f t] [-q c]

Gets Texas Statute information for source and statute provided

options:
  -h, --help            show this help message and exit
  -l, --list-sources    Shows a list of Sources to choose from.
  -c, --create-cache    Create cache file dir 'statute_cache' in this
                        directory for use with local statute search
  -e, --extract-cache   Extract ZIPS from cache folder dir 'statute_cache'
                        output to statute_cache_extracted
  -s TN, --source TN    Set statute source.
  -t 544.007, --statute 544.007
                        Set statute number.
  -f t, --format t      Choose output format. [-h] html, [-t] text(Default).
  -q c, --query c       Choose data source web or cache [-w] web request,
                        [-czip] cache(Default) [-cdir].
```
