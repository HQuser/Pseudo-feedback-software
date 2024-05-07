# from main import summarize_text_lsa
import re

from preprocessor import normalize_encoded_chars, get_words_from_url

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


# Function to summarize text using LSA
def summarize_text_lsa(text, sentences_count=2):
    # Initialize the LSA summarizer
    summarizer = LsaSummarizer()

    # Parse the text
    parser = PlaintextParser.from_string(text, Tokenizer("english"))

    # Summarize the text
    summary = summarizer(parser.document, sentences_count)

    # Combine the summarized sentences into a single string
    summarized_text = ' '.join([str(sentence) for sentence in summary])

    return summarized_text


def retrieve_all_verticals(query='mcdonalds', api_key='default'):
    dict = {}
    if not api_key == 'default':
        web_json = fetch_results_json(query=query, type='web', api_key=api_key)
        images_json = fetch_results_json(query=query, type='images', api_key=api_key)
        news_json = fetch_results_json(query=query, type='news', api_key=api_key)
        videos_json = fetch_results_json(query=query, type='videos', api_key=api_key)

        # Aggregate all into a datastructure
        dict = {
            'web': web_json,
            'images': images_json,
            'news': news_json,
            'videos': videos_json
        }

    return dict


'''
    This function is the main entry point for calling APIs with paramteres
'''


# TODO make UI to embed all the filters in the query before submittnig here
def fetch_results_json(query='mcdonalds', type='web', api_key='default'):
    vertical_codes = {'images': ('tbm', 'isch'),
                      'news': ('tbm', 'nws'),
                      'videos': ('tbm', 'vid')}

    # from serpapi.google_search_results import GoogleSearchResults
    from serpapi import GoogleSearch as GoogleSearchResults

    params = {
        "engine": "google",
        "q": query,
        'num': 100,
        "api_key": api_key,
        "google_domain": "google.com",
        "hl": "en",
        "api_key": api_key
    }

    if type != 'web':  # if not web then specify vertical code
        params.update({vertical_codes[type][0]: vertical_codes[type][1]})  # take key as vertical : value as code

    client = GoogleSearchResults(params)
    results = client.get_dict()
    return results


def process_web(api_response, index=0):
    dict = {}
    offset = 0

    for number, result in enumerate(api_response['organic_results'], start=index):
        if 'title' not in result:
            offset = offset - 1
            continue

        if 'snippet' not in result:
            snip = ""
        else:
            snip = normalize_encoded_chars(result['snippet'])

        
        dict[number + offset] = {'title': normalize_encoded_chars(result['title']),
                                 'snippet': snip,
                                 'url': result['link'],
                                 'type': 'web'}

    return dict


def process_images(api_response, index=1):
    dict = {}

    offset = 0
    for number, result in enumerate(api_response['images_results'], start=index):
        
        if 'thumbnail' not in result or 'title' not in result:
            
            offset = offset - 1
            continue
        dict[number + offset] = {'title': normalize_encoded_chars(result['title']),
                                 'url': result['link'],
                                 'thumbnail': result['thumbnail'],
                                 'type': 'image'}

    return dict


def process_news(api_response, index=1):
    dict = {}

    for number, result in enumerate(api_response['news_results'], start=index):
        
        if result['title'] == "":
            title = get_words_from_url(result['link'])
        else:
            title = result['title']
            title = normalize_encoded_chars(title)

        if 'thumbnail' not in result:
            thumbnail = ""
        else:
            thumbnail = result['thumbnail']
        dict[number] = {'title': title,
                        'snippet': result['snippet'],
                        'uploaded': result['date'],
                        'url': result['link'],
                        'thumbnail': thumbnail,
                        'type': 'news'}
    return dict


def process_videos(api_response, index=1):
    dict = {}

    for number, result in enumerate(api_response['video_results'], start=index):
        if 'thumbnail' not in result:
            thumbnail = ""
        else:
            thumbnail = result['thumbnail']

        # if result['snippet'] is None:
        #     result['snippet'] = ""

        uploaded = ""
        if 'rich_snippet' in result:
            if 'top' in result['rich_snippet']:
                if 'extensions' in result['rich_snippet']:
                    uploaded = " - ".join(result['rich_snippet']['top']['extensions'])

        dict[number] = {'title': normalize_encoded_chars(result['title']),
                        'snippet': '',
                        'uploaded': uploaded,
                        'thumbnail': thumbnail,
                        'url': result['link'],
                        'type': 'video'}
    return dict


def get_all_verticals(query='mcdonalds', api_key = "default"):
    import pickle

    dbfile = open('examplePickle', 'rb')
    db = pickle.load(dbfile)
    
    api = dict()
    if not api_key == 'default':
        api = retrieve_all_verticals(query=query, api_key=api_key)
    else:
        print("hello")
        api = db 
    web = process_web(api['web'])
    images = process_images(api['images'], len(web))
    news = process_news(api['news'], len(images) + len(web))
    videos = process_videos(api['videos'], len(news) + len(images) + len(web))

    dicts = {**web, **images, **news, **videos}
    return dicts


# res = get_all_vertical_results()

def extract_text(results):
    text_res = list()
    text = ""
    for k, v in results.items():
        if 'snippet' in v:
            text = v['title'] + ' ' + v['snippet']
        else:
            text = text_res.append(v['title'])

        if text == None or text == "":
            continue

        text_res.append(re.sub("[^A-Z\s]", "", text,0,re.IGNORECASE))
        text = ""
    return text_res


# text_data = extract_text(res)
# text_data

def generate_summary(text):
    summary_list = list()
    for t in text:
        summary_list.append(summarize_text_lsa(t))
    return summary_list
