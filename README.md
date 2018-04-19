# Pyparazzi CLI

## Overview

This tool scan webpages for links relative to a database. It also can scan web pages from a sitemap, from a list of domains, or from a list of sitemaps.

## Usage

```
usage: pyparazzi.py [-h] [-d str] [-s] [-o str] [--database str] [--log] [-f str]

Pyparazzi CLI

optional arguments:
  -h, --help            show this help message and exit
  -d str, --domain str  Domain to start the search.
  -s, --sitemap         Search through sitemap. Specify sitemap with
                        -d/--domain.
  -o str, --output str  Name of output file.
  --database str        Name of non-standard database.
  --log                 Enable logging.
  -f str, --file str    Import url from file to scan
```

## Examples

```
pyparazzi.py -d example.com -o coconut
```

Pyparazzi will scan all the links in the webpage "example.com" relative to the standard database and output the results to coconut.txt.

```
pyparazzi.py -f linkstoscan.txt -o papaya
```

Pyparazzi will scan all the links in the file "linkstoscan.txt" relative to the standard database and output the results to papaya.txt.

```
pyparazzi.py -f linkstoscan.txt --database nonstandarddb.txt -o nashi
```

Pyparazzi will scan all the links in the file "linkstoscan.txt" relative to the supplied database with the name "nonstandarddb.txt" and output the results to nashi.txt.

```
pyparazzi.py -f linkstoscan.txt --sitemap -o banana --log
```

Pyparazzi will use the file "linkstoscan.txt" to scan for sitemap which it will scan for urls. Those urls will be scanned for content relative to the standard database. The file will be output as banana.txt and a logfile will be produced with the same name.

```
pyparazzi.py --log --file linkstoscan.txt -o banana
```

Pyparazzi will use the file "linkstoscan.txt" to scan for sitemap which it will scan for urls. Those urls will be scanned for content relative to the standard database. The file will be output as banana.txt and a logfile will be produced with the same name.

> If you do more than one scan with the same name, the output file will be different (random integer added to the name), but the logfile will just have the new content appended.

## FAQ

Does this have legal implication if I use this tool?

> No, everything you can find with this tool, you can find manually; just slower.

It often outputs weird "links" that aren't really links, but buttons etc.

> We are aware. It does not do any post processing or sanitation of links.

Some short short-links give results that are unexpected or wrong.

> That is expected and something we hope can be improved upon.

Pyparazzi is super slow!

> Agreed. We might do an update with async/threading, or you can do a PR right now.