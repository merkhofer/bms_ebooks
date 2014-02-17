# in Twitter API:
#get #1 hashtag
#get tweets 
#collect n, splitting

#built_tweet = ''
#while len(built_tweet) > 140:

#find top word (first may be stopword, prob will be)
#build string
#collect n more that include that word, get top collocation
#

#
import twitter
import code
import re
from pprint import pprint
from itertools import groupby
from nltk.tokenize.punkt import PunktWordTokenizer
from nltk import tokenize

def get_hashtag(list_of_trends):
    for trend in list_of_trends:
        if "#" in trend['name']:
            yield trend['name']

def get_word(status):
    #pt = PunktWordTokenizer()
    #for word in pt.tokenize(status):
    #for word in tokenize.word_tokenize(status):
    for word in status.split():
        yield word

def get_first_good_word(status):
    for word in get_word(status):
        if not bad_word(word):
            return word

def most_common(L):
  return max(groupby(sorted(L)), key=lambda(x, v):(len(list(v)),-L.index(x)))[0]

def bad_word(word):
    """defines words that I don't want to include,
    currently @-mentions and RT tags"""
    if "@" in word:
        return True
    if re.search(r"\b[rR][tT]\b", word): #if this is a RT
        return True
    else:
        return False

#####MAIN            

with open('cred_file.txt', 'r') as credentials:
    CONSUMER_KEY = credentials.readline().strip()
    CONSUMER_SECRET = credentials.readline().strip()
    OAUTH_TOKEN = credentials.readline().strip()
    OAUTH_TOKEN_SECRET = credentials.readline().strip()

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)
twitter_api = twitter.Twitter(auth=auth)

US_WOE_ID = 23424977

us_trends = twitter_api.trends.place(_id=US_WOE_ID)

get_top_hash = get_hashtag(us_trends[0]['trends'])

top_hash = get_top_hash.next()
count = 100

search_results = twitter_api.search.tweets(q=top_hash, count=count)
statuses = search_results['statuses']

texts = [status.get('text') for status in statuses]
#pprint(texts)

firsts2 = [get_first_good_word(text.lower()) for text in texts]
print most_common(firsts2)

first_word = most_common(firsts2)

tweet_builder = first_word
last_word = first_word

dead_end = False

while len(tweet_builder) <= 140 and not dead_end:
    next_words = []
    next_round = twitter_api.search.tweets(q=top_hash, count=count)
    next_texts = [status.get('text') for status in next_round['statuses']]
    for tweet in next_texts:
        next_word = re.search(last_word+r"\W(.*?)\W", tweet, flags=re.IGNORECASE)
        if next_word:
            if next_word.group(1):
                #print first_word + " " + next_word.group(1)
                next_words.append(next_word.group(1).lower())
    if next_words:
        tweet_builder += " " + most_common(next_words)           
        last_word = most_common(next_words)
    else:
        dead_end = True

print tweet_builder        
