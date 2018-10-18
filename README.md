# Pyparazzi CLI

## Overview

Pyparazzi scans webpages for links, either using the standard database or your own. It also can scan web pages from a sitemap, from a list of domains, or from a list of sitemaps.

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

An example output, from https://vagn.es/ :

```text
github.com/deepfakes/faceswap
github.com/gkbrk/slowloris
github.com/spf13/cobra
github.com/tj/slowloris
github.com/urfave/cli
github.com/vagnes
github.com/vagnes/ergodox-layout
github.com/vagnes/go-cli-tutorial
github.com/valyala/goloris
linkedin.com/in/vagnes
reddit.com/r/ErgoDoxEZ/comments/7v3vzh/notes_from_a_firsttime_ergodox_ez_user/
reddit.com/r/deepfakes/
reddit.com/r/deepfakes/comments/7sycbf/a_message_to_everyone_who_opposes_deepfakes_as/
reddit.com/u/ezuk
reddit.com/user/Gravity_Horse
twitter.com/vagn_es
youtube.com/watch?v=XiFkyR35v2Y
```

## FAQ

Are there any legal implication if I use this tool?

> Everything you can find with this tool, you can find manually; just slower. So probably no.

It often outputs weird "links" that aren't really links, but buttons etc.

> I'm are aware. It does not do any post processing or sanitation of links.

Some short short-links give results that are unexpected or wrong.

> That is expected and something I hope can be improved upon.

Pyparazzi is slow!

> Agreed. There is some rudamentary async, but it can be improved greatly upon.
