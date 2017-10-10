from __future__ import absolute_import, unicode_literals
from flask.helpers import get_debug_flag

from analyzerapp.settings import DevConfig, ProdConfig
from analyzerapp.celery import create_celery
from analyzerapp.app import create_app

import re
import operator
import requests
import nltk
from nltk.corpus import stopwords
from collections import Counter
from bs4 import BeautifulSoup

CONFIG = DevConfig if get_debug_flag() else ProdConfig
celery = create_celery(create_app(CONFIG))

@celery.task(name="tasks.count_words")
def count_words(url,ret_words = 20):
    # count = 1
    # for i in range(10000):
    #     count += 1
    # return {"results":len(url)}
    errors = []

    try:
        r = requests.get(url)
    except:
        errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
        return {"error": errors}

    # text processing
    raw = BeautifulSoup(r.text).get_text()
    nltk.data.path.append('./nltk_data/')  # set the path
    tokens = nltk.word_tokenize(raw)
    text = nltk.Text(tokens)

    # remove punctuation, count raw words
    non_punc_re = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in text if non_punc_re.match(w)]
    raw_word_count = Counter(raw_words)

    # stop words
    no_stop_words = [w for w in raw_words if w.lower() not in stopwords.words()]
    no_stop_words_count = Counter(no_stop_words)

    # save the results
    results = sorted(
        no_stop_words_count.items(),
        key=operator.itemgetter(1),
        reverse=True
    )

    return {"results": results[:ret_words]}
