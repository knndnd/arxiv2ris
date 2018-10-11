# arxiv2ris

This script runs using Python 3.

First, install the required packages. This script only requires ``nltk`.

```bash
$ pip3 install -r requirements.txt
```

If you run the error that the package ``punkt`` doesn't exist, download it by going into your Python environment and running:

```bash
$ python3

>>> import nltk
>>> nltk.download('punkt')
```

In MacOS, you can get the SSL error

```
[nltk_data] Error loading punkt: <urlopen error [SSL:
[nltk_data]     CERTIFICATE_VERIFY_FAILED] certificate verify failed:
[nltk_data]     unable to get local issuer certificate (_ssl.c:1045)>
```

this will be fixed by reinstalling certificates
```shell
$ /Applications/Python\ 3.x/Install\ Certificates.command
```


To query for a certain keyword, run:

Usage: arxiv2ris {-h} {-n number} {-t dateoption} {-f fieldoption} {-m months} -k "keywords1 keywords2 " 

	-h  help
	
	-n  number of references
	
	-f  fields to be searched, the fields can be:
	
		a         :   all
		
		t         :   title
		
		b         :   abstract
		
		i         :   paper_id
		
		u         :   author   
		
	-t  date range   
	
		a         :     'all_dates'
		
		p         :     'past_12',    past 12 months
		
		y         :     'specific_year'

	-y  2018, or other year
	
	-m  months, can be float value
	
	-k  "keywords"

The result will be written to a local file "tmp.ris", with the following format:

TY  - Preprint

T1  - title of the paper

A1  - author1

A1  - author2

JO  - ArXiv e-prints

Y1  - date

UR  - https://arxiv.org/abs/xxxx.xxxx

N2  - abstracts

ER  -

Users can double click the file tmp.ris to import it to Endnote.
