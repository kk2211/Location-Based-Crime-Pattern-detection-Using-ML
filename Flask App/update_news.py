import pandas as pd
import datetime
import dateutil.parser
import os
import csv

import aylien_news_api
from aylien_news_api.rest import ApiException

configuration = aylien_news_api.Configuration()
configuration.api_key['X-AYLIEN-NewsAPI-Application-ID'] = '0d36dcf6'
configuration.api_key['X-AYLIEN-NewsAPI-Application-Key'] = '0e2486cee08208234f39b02e98552184'
api_instance = aylien_news_api.DefaultApi()

import nltk
from nltk.tag.stanford import StanfordNERTagger

jar = './stanford-ner.jar'
model = './english.all.3class.distsim.crf.ser.gz'

def findLocations(sentence):
    locations = []
    ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')
    words = nltk.word_tokenize(sentence)
    lst = ner_tagger.tag(words)

    i = 0
    while i < len(lst):
        if lst[i][1] == 'LOCATION':
            s = lst[i][0]
            i += 1
            if i == len(lst):
                break
            while lst[i][1] == 'LOCATION':
                s = s + ' ' + lst[i][0]
                i += 1
                if i == len(lst):
                    break
            if s.lower() not in locations:
                locations.append(s.lower())
        else:
            i += 1

    return locations


from word2number import w2n
def findAge(content):
    if 'year-old' in content:
        index = content.index('year-old')
        if index - 7 < 0:
            age = content[:index + 8].split()
        else:
            age = content[index - 7:index + 8].split()
        if len(age) != 0:
            if age[-1] == 'year-old':
                if '-' in age[-2]:
                    s = str(age[-2][:-1])
                else:
                    s = str(age[-2])
            else:
                s = age[-1].split('-')[0]
            if s == 'a':
                s = 1
            s = str(s).split('.')[-1]
            return w2n.word_to_num(str(s))
    else:
        return -1

def updateNews():
    df = pd.read_csv('alyien_news_data.csv')
    df['date'] = pd.to_datetime(df.date)
    df = df.sort_values(by='date')

    rows = []

    e = str(datetime.date.today())
    s = str((datetime.datetime.strptime(str(list(df['date'])[-1].date()), "%Y-%m-%d") + datetime.timedelta(days=1)).date())

    from_date = s
    to_date = str((datetime.datetime.strptime(str(from_date), "%Y-%m-%d") + datetime.timedelta(days=1)).date())

    print('Old length of Aylien news :', len(df))
    total_news_count = 0
    content_text = ""
    crimes = {'burglary': 0, 'robbery': 0, 'murder': 0, 'kidnapping': 0, 'rape': 0}
    while dateutil.parser.parse(from_date).date() < dateutil.parser.parse(e).date():
        if dateutil.parser.parse(to_date).date() > dateutil.parser.parse(e).date():
            to_date = e
        print(from_date, 'to', to_date)
        for crime in crimes.keys():
            opts = {
                'title': crime,
                'sort_by': 'social_shares_count.facebook',
                'language': ['en'],
                'published_at_start': from_date + 'T00:00:00Z',
                'published_at_end': to_date + 'T00:00:00Z',
                'per_page': 100,
                'source_locations_country': ['IN'],
                'source_locations_state': ['Delhi'],
                'source_locations_city': ['Delhi'],
            }
            headlines = api_instance.list_stories_with_http_info(**opts)
            for i in headlines[0].stories:
                date = i.published_at.date()
                time = i.published_at.time()
                source = i.source.name
                title = i.title
                desc = i.source.description
                url = i.links.permalink
                content = i.body
                summary = ' '.join(list(i.summary.sentences))
                rows.append([date, time, source, title, desc, crime, url, content, summary])
                content_text += content
        from_date = to_date
        to_date = str((datetime.datetime.strptime(str(from_date), "%Y-%m-%d") + datetime.timedelta(days=1)).date())

    locations = findLocations(content_text)
    f = open('loc.txt', 'r')
    s = f.read()
    loc = s.split('\n')[3:]
    delhi_locs = []
    for i in loc:
        if i != 'LOCALITY':
            delhi_locs.append(i.lower())

    all_locations = list(set(delhi_locs).intersection(locations))

    business = ['businessman', 'jeweller', 'jeweler', 'shop owner', 'property dealer']
    d = {}
    c = 0
    for i in range(len(rows)):
        print(i, c)
        article = rows[i][7]
        locs = findLocations(article)
        date = str(rows[i][0])
        headline = rows[i][3]
        crime_type = rows[i][5]
        businessman = 0
        for j in business:
            if j in article:
                businessman = 1
                break
        age = findAge(article)

        for i in locs:
            if i in all_locations:
                c += 1
                flag = 1
                lst = d.get(i, [[], [], [], [], [], []])  # date, headline, crime_type, article, age, businessman
                lst[0].append(date)
                lst[1].append(headline)
                lst[2].append(crime_type)
                lst[3].append(article)
                lst[4].append(age)
                lst[5].append(businessman)
                d[i] = lst
    df1 = pd.read_csv('news_data.csv')
    locs = list(df1['location'])
    for i in range(len(df1)):
        cur_loc = df1['location'].iloc[i]
        lst = d.get(cur_loc, [[], [], [], [], [], [], []])
        lst[0] = lst[0] + list(df1[df1['location'] == cur_loc]['date'])[0].split('\t')
        lst[1] = lst[1] + list(df1[df1['location'] == cur_loc]['headline'])[0].split('\t')
        lst[2] = lst[2] + list(df1[df1['location'] == cur_loc]['crime_type'])[0].split('\t')
        lst[3] = lst[3] + list(df1[df1['location'] == cur_loc]['article'])[0].split('\t')
        lst[4] = lst[4] + list(df1[df1['location'] == cur_loc]['age'])[0].split('\t')
        lst[5] = lst[5] + list(df1[df1['location'] == cur_loc]['businessman'])[0].split('\t')
        lst[6] = lst[6] + str(list(df1[df1['location'] == cur_loc]['percentile'])[0]).split('\t')
        for k in range(len(lst[4])):
            lst[4][k] = int(lst[4][k])
            lst[5][k] = int(lst[5][k])

        d[cur_loc] = lst

    rows1 = []
    header = ['location', 'date', 'headline', 'crime_type', 'article', 'age', 'businessman', 'percentile']
    rows1.append(header)
    for i in d.keys():
        row = [i]
        lst = d[i]
        row.append('\t'.join(lst[0]))
        row.append('\t'.join(lst[1]))
        row.append('\t'.join(lst[2]))
        row.append('\t'.join(lst[3]))
        row.append('\t'.join(repr(n) for n in lst[4]))
        row.append('\t'.join(repr(n) for n in lst[5]))
        rows1.append(row)


    os.remove('news_data.csv')

    data = open('news_data.csv', 'w')
    writer = csv.writer(data)
    writer.writerows(rows1)
    data.close()

    news_data = open('alyien_news_data.csv', 'a')
    writer = csv.writer(news_data)
    writer.writerows(rows)
    news_data.close()


    df2 = pd.read_csv('alyien_news_data.csv')
    print('new length of aylien news :', len(df2))

