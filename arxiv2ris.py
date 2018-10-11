import re
import sys
import time
import getopt
import urllib.error
import urllib.request
#import enchant
from nltk.tokenize import word_tokenize
from six.moves.html_parser import HTMLParser

h = HTMLParser()

AUTHOR_TAG = '<a href="/search/?searchtype=author'
TITLE_TAG = '<p class="title is-5 mathjax">'
ABSTRACT_TAG = '<span class="abstract-full has-text-grey-dark mathjax"'
DATE_TAG = '<p class="is-size-7"><span class="has-text-black-bis has-text-weight-semibold">Submitted</span>'


def get_authors(lines, i):
    authors = []
    while True:
        if not lines[i].startswith(AUTHOR_TAG):
            break
        idx = lines[i].find('>')
        if lines[i].endswith(','):
            authors.append(lines[i][idx + 1: -5])
        else:
            authors.append(lines[i][idx + 1: -4])
        i += 1
    return authors, i


def get_next_result(lines, start):
    """
    Extract paper from the xml file obtained from arxiv search.
    
    Each paper is a dict that contains:
    + 'title': str
    + 'pdf_link': str
    + 'main_page': str
    + 'authors': []
    + 'abstract': str
    """

    result = {}
    idx = lines[start + 3][10:].find('"')
    result['main_page'] = lines[start + 3][9:10 + idx]
    idx = lines[start + 4][23:].find('"')
    result['pdf'] = lines[start + 4][22: 23 + idx] + '.pdf'

    start += 4

    while lines[start].strip() != TITLE_TAG:
        start += 1

    title = lines[start + 1].strip()
    title = title.replace('<span class="search-hit mathjax">', '')
    title = title.replace('</span>', '')
    result['title'] = title

    authors, start = get_authors(lines, start + 5)  # orig: add 8

    while not lines[start].strip().startswith(ABSTRACT_TAG):
        start += 1
    abstract = lines[start + 1]
    abstract = abstract.replace('<span class="search-hit mathjax">', '')
    abstract = abstract.replace('</span>', '')
    result['abstract'] = abstract

    result['authors'] = authors

    while not lines[start].strip().startswith(DATE_TAG):
        start += 1

    idx = lines[start].find('</span> ')
    end = lines[start][idx:].find(';')

    result['date'] = lines[start][idx + 8: idx + end]

    result_ = 'TY  - Preprint\n'
    result_ += 'T1  - {}\n'.format(result['title'])
    for au in authors:
        result_ += 'A1  - {}\n'.format(au)
    result_ += 'JO  - ArXiv e-prints\n'
    result_ += 'Y1  - {}\n'.format(result['date'])
    result_ += 'UR  - {}\n'.format(result['main_page'])
    result_ += 'N2  - {}\n'.format(result['abstract'])
    result_ += 'ER  -\n\n\n'

    return result_, start


def clean_empty_lines(lines):
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)
    return cleaned


def is_float(token):
    return re.match("^\d+?\.\d+?$", token) is not None


def is_citation_year(tokens, i):
    if len(tokens[i]) != 4:
        return False
    if re.match(r'[12][0-9]{3}', tokens[i]) is None:
        return False
    if i == 0 or i == len(tokens) - 1:
        return False
    if (tokens[i - 1] == ',' or tokens[i - 1] == '(') and tokens[i + 1] == ')':
        return True
    return False


def is_list_numer(tokens, i, value):
    if value < 1 or value > 4:
        return False
    if i == len(tokens) - 1:
        return False

    if (i == 0 or tokens[i - 1] in set(['(', '.', ':'])) and tokens[i + 1] == ')':
        return True
    return False


def has_number(sent):
    tokens = word_tokenize(sent)
    for i, token in enumerate(tokens):
        if token.endswith('\\'):
            token = token[:-2]
        if token.endswith('x'):  # sometimes people write numbers as 1.7x
            token = token[:-1]
        if token.startswith('x'):  # sometimes people write numbers as x1.7
            token = token[1:]
        if token.startswith('$') and token.endswith('$'):
            token = token[1:-1]
        if is_float(token):
            return True
        try:
            value = int(token)
        except:
            continue
        if (not is_citation_year(tokens, i)) and (not is_list_numer(tokens, i, value)):
            return True

    return False


def contains_sota(sent):
    return 'state-of-the-art' in sent or 'state of the art' in sent or 'SOTA' in sent


def extract_line(abstract, keyword, limit):
    lines = []
    numbered_lines = []
    kw_mentioned = False
    abstract = abstract.replace("et. al", "et al.")
    sentences = abstract.split('. ')
    kw_sentences = []
    for i, sent in enumerate(sentences):
        if keyword in sent.lower():
            kw_mentioned = True
            if has_number(sent):
                numbered_lines.append(sent)
            elif contains_sota(sent):
                numbered_lines.append(sent)
            else:
                kw_sentences.append(sent)
                lines.append(sent)
            continue

        if kw_mentioned and has_number(sent):
            if not numbered_lines:
                numbered_lines.append(kw_sentences[-1])
            numbered_lines.append(sent)
        if kw_mentioned and contains_sota(sent):
            lines.append(sent)

    if len(numbered_lines) > 0:
        return '. '.join(numbered_lines), True
    return '. '.join(lines[-2:]), False


def get_report(paper, keyword):
    if keyword in paper['abstract'].lower():
        title = h.unescape(paper['title'])
        headline = '{} ({} - {})\n'.format(title, paper['authors'][0], paper['date'])
        abstract = h.unescape(paper['abstract'])
        extract, has_number = extract_line(abstract, keyword, 280 - len(headline))
        if extract:
            report = headline + extract + '\nLink: {}'.format(paper['main_page'])
            return report, has_number
    return '', False


def txt2reports(txt, keyword, num_to_show):
    found = False
    nFound = 0
    txt = ''.join(chr(c) for c in txt)
    lines = txt.split('\n')
    lines = clean_empty_lines(lines)

    for i in range(len(lines)):
        if num_to_show <= 0:
            return unshown, num_to_show, found

        line = lines[i].strip()
        if len(line) == 0:
            continue
        if line == '<li class="arxiv-result">':
            found = True
            paper, i = get_next_result(lines, i)

            with open("tmp.ris", "a",encoding='utf-8') as f:
                f.write(paper)

            nFound += 1
            num_to_show -= 1
        if line == '</ol>':
            break
    return nFound, num_to_show, found


def get_papers(keyword, num_results, field, date, year, from_date, to_date):
    query_temp = 'https://arxiv.org/search/advanced?advanced=&terms-0-operator=AND&terms-0-term={}&terms-0-field={}&classification-computer_science=y&classification-physics_archives=all&date-filter_by={}&date-year={}&date-from_date={}&date-to_date={}&date-date_type=submitted_date&abstracts=show&size={}&order=-announced_date_first&start={}'

    keyword_q = keyword.replace(' ', '+')
    page = 0
    per_page = 200
    num_to_show = num_results
    nFound = 0

    while num_to_show > 0:
        query = query_temp.format(keyword_q, field, date, year, from_date, to_date, str(per_page), str(per_page * page))

        req = urllib.request.Request(query)
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            print('Error {}: problem accessing the server'.format(e.code))
            return

        txt = response.read()

        nn, num_to_show, found = txt2reports(txt, keyword, num_to_show)
        nFound += nn

        if not found or num_to_show == 0:
            print('Found {} references'.format(nFound))
            return

        page += 1

def usage():
    print(''' 
<<<<<<< HEAD
    Usage: arxiv2ris -h {-n number} {-t dateoption} {-m last_months} {-y year}{-f fieldoption} -k "keywords1 keywords2 " 
=======
    Usage: arxiv2ris {-h} {-n number} {-t dateoption} {-f fieldoption} -k "keywords1 keywords2 " 
>>>>>>> 832fe67132d3b57c52f9904dd1533da6f496a493
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
        -m  date range, months
            x        :     past x months
        -y  2018, or other year
        -k  "keywords"
    ''')

def main():
    with open("tmp.ris", "w") as f:
        f.write('\n')

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn:f:t:y:k:m:")
    except getopt.GetoptErroras:
        # print help information and exit:
        usage()
        sys.exit(2)

    num_results = 10000
    keyword = ''
    field = 'all'
    date  = 'all_dates'
    year = ''
    to_date = ''
    from_date = ''

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-n", "--number"):
            num_results = int(a)
        elif o in ("-f", "--field"):
            if a=='a':
                field = 'all'
            elif a=='t':
                field = 'title'
            elif a == 'b':
                field = 'abstract'
            elif a=='i':
                field = 'paper_id'
            elif a == 'u':
                field = 'author'
        elif o in ("-t", "--date"):
            if a == 'a':
                date = 'all_dates'
            elif a == 'p':
                date = 'past_12'
            elif a == 'y':
                date = 'specific_year'
                year = '2018' # by default
        elif o in ("-y"):
            date = 'specific_year'
            year = a
        elif o in ("-m"):
            date = 'date_range'
            to_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
            from_date = time.strftime('%Y-%m-%d',time.localtime(time.time()-int(a)*2592000))
        elif o in ("-k"):
            keyword = a

    if keyword =='':
        usage()
        sys.exit()

    get_papers(keyword, num_results, field, date, year, from_date, to_date)


if __name__ == '__main__':
    main()
