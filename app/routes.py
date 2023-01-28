from flask import Flask, render_template, flash, redirect, url_for, request, Response
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import json
from flask_paginate import Pagination, get_page_args
import pandas as pd
import os

import webvtt

import nltk
#no need to the following 2 commands since we use nltk.txt with heroku and locating it in root folder
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')


from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer

#from flask_mobility.decorators import mobile_template
from flask_mobility import Mobility
from bs4 import BeautifulSoup
import re
import random
#from vimeo import VimeoClient, client


from mixpanel import Mixpanel
mp = Mixpanel("131b74a0c04e35473761889abde6d7b0")
#mp.track(user_id, 'Sent Message')
mp.track("#nav a", "click nav link")

#basedir = os.path.abspath(os.path.dirname(__file__))

TIME_OFFSET = 12150
LEVEL_TALKS = 170
USER_LANG = 'ar'

TPL = 'web' + '/'
STATIC_URL = '/static/' + TPL
STATIC_TED = 'app/static/ted/' 
STATIC_VTT = '/static/' 

CDN = True

if CDN:
    STATIC_URL = 'https://cdn.connectedenglish.net' + '/static/' + TPL
else:
    STATIC_URL = '/static/' + TPL

#@app.after_request
#def add_header(response):
#    response.cache_control.max_age = 31536000
#    return response



#@app.route('/')
#def index_redirect():
#    return redirect(url_for('index'))

bootstrap = Bootstrap(app)
moment = Moment(app)
Mobility(app)

with app.open_resource('static/ted/csv/links_rank.csv', 'r') as f:
    df_talks  = pd.read_csv(f)

with app.open_resource ('static/ted/json/talk_rank.json', 'r') as f:
    talk_rank = json.load(f)

with app.open_resource('static/ted/csv/common_words.csv', 'r') as f:
    common_words = pd.read_csv(f)

with app.open_resource('static/ted/json/trans_dic.json', 'r') as f:
    trans_dic = json.load(f)

with app.open_resource('static/ted/json/talk_info.json', 'r') as f:
    talk_info = json.load(f)

#with app.open_resource('static/ted/json/talk_words.json', 'r') as f:
    #talk_words = json.load(f)


@app.errorhandler(404)
def page_not_found(e):
    template = TPL + USER_LANG +  '/' + '404.html'
    return render_template(template,  STATIC_URL=STATIC_URL), 404

@app.errorhandler(500)
def internal_server_error(e):
    template = TPL + USER_LANG +  '/' + '500.html'
    return render_template(template, STATIC_URL=STATIC_URL), 500

#@app.route('/')
#def index_redirect():
#    return redirect(url_for('index'))

def get_Device():
    global TPL
    global CDN
    global STATIC_URL
    global STATIC_TED
    global STATIC_VTT

    if TPL == '':
        TPL = 'web' + '/'

        if request.MOBILE:
            TPL = 'mobile' + '/'

        if CDN:
            STATIC_URL = 'https://cdn.connectedenglish.net' + '/static/' + TPL
        else:
            STATIC_URL = '/static/' + TPL

    
    return  TPL   

@app.route('/')
@app.route('/index.html')
@app.route("/" + USER_LANG + "/")
@app.route('/' + USER_LANG +'/index.html')
#@mobile_template('/{mobile/}' + USER_LANG + '_index.html')
def index():
    get_Device()
    title='Home'
    template = TPL + USER_LANG +  '/' + 'index.html'
    return render_template(template, title=title, STATIC_URL=STATIC_URL)





@app.route('/login', methods=['GET', 'POST'])
@app.route('/' + USER_LANG + '/login', methods=['GET', 'POST'])
def login(lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'login.html'
    TPL = get_Device()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template(template, title='Sign In', form=form, STATIC_URL=STATIC_URL)


@app.route('/logout')
@app.route('/' + USER_LANG + '/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@app.route('/' + USER_LANG + '/register', methods=['GET', 'POST'])
def register():
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'register.html'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template(template, title='Register', form=form, STATIC_URL=STATIC_URL)


@app.route('/faq.html')
@app.route('/' + USER_LANG +'/faq.html')
def faq(lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'faq.html'
    title='FAQ'
    
    return render_template(template,  title=title, STATIC_URL=STATIC_URL)

@app.route('/sitemap.xml')
#@app.route('/' + USER_LANG +'/sitemap.html')
def sitemap():
	title='Sitemap'
	return render_template('sitemap.xml',  title=title, STATIC_URL=STATIC_URL)


@app.route('/profile.html')
@app.route('/' + USER_LANG +'/profile.html')
@login_required
def profile(lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'profile.html'
    title='My Profile'
    return render_template(template,  title=title, STATIC_URL=STATIC_URL)

@app.route('/aboutus.html')
@app.route('/' + USER_LANG +'/aboutus.html')
def aboutus(lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'aboutus.html'
    title='About Us'
    return render_template(template,  title=title, STATIC_URL=STATIC_URL)

@app.route('/contactus.html')
@app.route('/' + USER_LANG + '/contactus.html')
def contactus(lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'contactus.html'
    title='Contact Us'
    return render_template(template,  title=title, STATIC_URL=STATIC_URL)

@app.route('/levels/<name>.html')
@app.route('/levels/index.html')
@app.route('/' + USER_LANG +'/levels/<name>.html')
@app.route('/' + USER_LANG +'/levels/index.html')
#@mobile_template('/{mobile/}' + USER_LANG + '_level.html')
#@login_required
def level(name=1, lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'level.html'
    title='Level ' + name
    myrank = {}
       
    level = int(name) 
    
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    total_talks = LEVEL_TALKS #len(level_links[int(name)])
    pagination_talks = get_talks(level=level, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total_talks, css_framework='bootstrap4') #, css_framework='bootstrap4'
    #css_links = css_Paginate(pagination.links)
    info_id = {}
    for talk in pagination_talks.iloc():
        mytalk = str( int(talk['talk_id']) )
        info_id[mytalk] = talk_info[mytalk]
        myrank[mytalk] =  talk_rank[mytalk]

   
    return render_template(template, name=name, title=title, talks=pagination_talks, page=page, per_page=per_page, pagination=pagination, info_id=info_id, talk_rank=myrank, STATIC_URL=STATIC_URL )
    
def get_talks(level, offset, per_page=10):
	return df_talks[(level-1) * LEVEL_TALKS + offset: (level-1) * LEVEL_TALKS + offset + per_page]


@app.route('/words/<name>.html')
@app.route('/' + USER_LANG +'/words/<name>.html')
#@mobile_template('/{mobile/}' + USER_LANG + '_word.html')
#@login_required
def word(name, lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG + '/' + 'word.html'
    title="Definition of '" + name +"'"
    
    with app.open_resource('static/ted/lemmas/' + name +'.json', 'r') as f:
        myword = json.load(f)

    results = myword['results']

   
    return render_template(template, results=results, title=title,  word=name, STATIC_URL=STATIC_URL )


@app.route('/commonwords/')
@app.route('/commonwords/<name>.html')
@app.route('/' + USER_LANG + '/commonwords/')
@app.route('/' + USER_LANG + '/commonwords/<name>.html')
#@mobile_template('/{mobile/}' + USER_LANG + '_commonwords.html')
#@login_required
def commonwords(name='1k', lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG + '/' + 'commonwords.html'
    title= 'List of Common ' + name + ' Words'
    trans = {}
    level_start = 0

    if name == '1k':
        pagination_words = common_words[0:1000]
        total_words = 1000
        level_start = 0
    elif name == '3k':
        pagination_words = common_words[1000:3000]
        total_words = 2000
        level_start = 1000
    elif name == '5k':
        pagination_words = common_words[3000:5000]
        total_words = 2000
        level_start = 3000
    elif name == '10k':
        pagination_words = common_words[5000:10000]
        total_words = 5000
        level_start = 5000
    elif name == '50k':
        pagination_words = common_words[10000:]
        total_words = 26700 
        level_start = 10000 

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    
    per_page = 20
 
    pagination_words = get_commonwords(page=page, level=level_start, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total_words, css_framework='bootstrap4')
    
    
    strart_from = level_start + (page-1) * 20 +1
    for word in pagination_words.iloc():
        myword = word['word']
        if  myword in trans_dic.keys():
            trans[myword] =   ', '.join( trans_dic[myword]['trans'] )
   
    
    return render_template(template, name=name, title=title, words=pagination_words, trans=trans, page=page, per_page=per_page, pagination=pagination, STATIC_URL=STATIC_URL )

def get_commonwords(page, level, offset=0, per_page=30):
    offset = ((page-1) * 20) -1
    if offset == -1:
        offset = 0
        
    return common_words[level+offset: level + offset + per_page]    

   
#app.jinja_env.globals.update(trans_word=trans_word) 


@app.route('/quizes/')
@app.route('/quizes/<name>.html')
@app.route('/' + USER_LANG + '/quizes/')
@app.route('/' + USER_LANG + '/quizes/<name>.html')
#@mobile_template('/{mobile/}' + USER_LANG + '_exercise.html')
#@login_required
def quiz(name='1', lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' +  'quiz.html'

    words = []
    en_file =  STATIC_TED + 'subtitles/webvtt/en/' + name + '.vtt'
        
    lem = WordNetLemmatizer()
    for cap in webvtt.read(en_file):
        if cap.text != '':
            tokenized_word=word_tokenize(cap.text.lower())
            for word in tokenized_word:
                word = lem.lemmatize(word,"v")
                if  word in trans_dic.keys():
                    if trans_dic[word]['rank'] > 300:
                        words.append(word)
       
    ln = len(words)
    quest  =[] 
    wvt = webvtt.read(en_file)
 
    for x in range(10):

        mainrnd = random.randint(0,ln-1)
        mainword = words[mainrnd]
     

        item = {}
        item['question'] = mainword
        item['answers'] = []

        shuffle = random.randint(0, 4-1)

        for y in range(4):
       
            if y == shuffle:
                word = mainword
                trans =  ', '.join( trans_dic[mainword]['trans'])
                ans = {}
                ans['answer'] = trans
                ans['correct'] = 1
                item['answers'].append(ans)

            else:

                rnd = mainrnd
                while rnd == mainrnd:
                    rnd = random.randint(0,ln-1)

                word = words[rnd]
                trans =  ', '.join( trans_dic[word]['trans'] )
                ans = {}
                ans['answer'] = trans
                ans['correct'] = 0
                item['answers'].append(ans)


        sents = []
        for cap in  wvt:
            if mainword in cap.text:
                sents.append(cap.text)

        rnd = random.randint(0,len(sents)-1)
        item['sents'] = sents[rnd]       
        quest.append(item)
     
    return render_template(template,  quest=quest, STATIC_URL=STATIC_URL)


@app.route('/search/')
@app.route('/search/<name>.html')
@app.route('/' + USER_LANG + '/search/')
@app.route('/' + USER_LANG + '/search/<name>.html')
#@mobile_template('/{mobile/}' + USER_LANG + '_exercise.html')
#@login_required
def search(name='1', lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' +  'quiz.html'
    return render_template(template,  STATIC_URL=STATIC_URL)




@app.route('/talks/')
@app.route('/talks/<name>.html')
@app.route('/' + USER_LANG + '/talks/')
@app.route('/' + USER_LANG + '/talks/<name>.html')
#@mobile_template('/{mobile/}' + USER_LANG + '_talk.html')
#@login_required
def talk(name='1', lang=USER_LANG):
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'talk.html'
    res = {}
    sentences = []
    trans ={}

    def get_sent(offset=0, per_page=1):
        return  sentences[offset: offset + per_page]

    myfile =  'static/ted/talk-info/' + name + '.json'
    with app.open_resource(myfile, 'r') as f:
        res = json.load(f)
        title = res['title']
        img_url = res['talk_url'] + '.jpg'
        
    en_file =  STATIC_TED + 'subtitles/webvtt/en/' + name + '.vtt'
    en_sync =  STATIC_TED + 'subtitles/sync/en/' + name + '.vtt'

    #if not os.path.isfile(en_sync):
    x=0
    vtt = webvtt.read(en_file)
    for cap in vtt:
        if cap.text != '':
            cap.start = add_Offset(convert_Time(cap.start, True ))
            cap.end = add_Offset(convert_Time(cap.end, True ))
        else:
            del vtt.captions[x]  
        x+=1
        
    with open(en_sync, 'w') as f:
        vtt.write(f)

    x =0
    #lem = WordNetLemmatizer()
    for cap in webvtt.read(en_sync):
        #cap.text = cap.text.replace('"', "&ldquo;")
        if cap.text != '':
            cap.text = cap.text.replace('\n', " ")
            val = [x+1, cap.text, convert_Time(cap.start)/1000, convert_Time(cap.end)/1000, '', 0, 0]
            sentences.append(val)
            tokenized_word=word_tokenize(cap.text.lower())
            trans[x+1] = []
            for word in tokenized_word:
                #word = lem.lemmatize(word,"v")
                if  word in trans_dic.keys():
                    val = [ trans_dic[word]['rank'], word, (', '.join( trans_dic[word]['trans']) )]
                    trans[x+1].append(val)
            x+=1
           

    ar_file =  STATIC_TED + 'subtitles/webvtt/ar/' + name + '.vtt'
    ar_sync =  STATIC_TED + 'subtitles/sync/ar/' + name + '.vtt'
    
    if not os.path.isfile(ar_sync):
        vtt = webvtt.read(ar_file)
        for cap in vtt:
            cap.start = add_Offset(convert_Time(cap.start, True ))
            cap.end = add_Offset(convert_Time(cap.end, True ))
          
        with open(ar_sync, 'w') as f:
            vtt.write(f)
    
    y=0        
    for cap in webvtt.read(ar_sync):
        if y <= x:
            #cap.text = cap.text.replace('"', "&ldquo;")
            cap.text = cap.text.replace('\n', " ")
            sentences[y][4]= cap.text
            y+=1 # x should be after loop in the arabic vtt



    total_sent = len(sentences)    

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    
    per_page = 10
    
    pagination_sent = get_sent(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total_sent, css_framework='bootstrap4') #

    return render_template(template, name=name, title=title, img_url=img_url,trans=trans, results=res, sentences=pagination_sent, page=page, per_page=per_page, pagination=pagination, STATIC_URL=STATIC_URL, STATIC_VTT=STATIC_VTT)

def convert_Time(str_time, offset=False):
    if offset:
        offset = TIME_OFFSET
    else:
        offset =0
        
    int_time = (offset + int(str_time[9:12]) + int(str_time[6:8])*1000  + int(str_time[3:5])*60000  +  int(str_time[0:2])*3600000 )
    
    return int_time

def add_Offset(int_time):

    seconds = int_time/1000
    min = int(seconds/60)
    _sec = (seconds- (min*60))
    milsec = _sec %1
    sec = int(_sec - milsec)
    milsec= int(round(milsec,3)*1000)
    str_time = "00:" + str(min).zfill(2) + ":" + str(sec).zfill(2) + "." + str(milsec).zfill(3)
    
    return str_time
    
    
#================================================================================================
@app.route('/vimeo.html')
@app.route('/' + USER_LANG +'/vimeo.html')
def vimeo():
    get_Device()
    title='Home'
    template = TPL + USER_LANG +  '/' + 'vimeo.html'

    v = VimeoClient(
    token='701398f91f49252faea2d1443ea05243',
    key='1f9f596903d531e60a79d528b4b18b05dc0827e0',
    secret='cBmzODfl3lomOMLO4QDe20hk1N+qtZVDFgqElvGmB8H0bru96bMM7mB8xHfxNG20qruejYBxCsw6JlBMLnGd+mcC568GSxuWitjeOsHxi5Y6wcJAE4RayYHC3SScfskq'
    )

    # Make the request to the server for the "/me" endpoint.
    #about_me = v.get('/me')

    video_id = '416770043'
    #url = "https://vimeo.com/api/v2/video/" + video_id + '.json'
    v.upload_picture('/videos/' + video_id, 'videos/picture.png', activate=True)
    #response = v.get(url)
    test = 'Uploaded'
    
    # Make sure we got back a successful response.
    #assert about_me.status_code == 200

    # Load the body's JSON data.
    #test = about_me.json()
    #test = os.path.dirname(__file__)
    #video_uri = v.upload('videos/english.mp4')


    #test = v.get('/me', params={"fields": "uri,name"})

    return render_template(template, test=test, title=title, STATIC_URL=STATIC_URL)    

    

    file_name = 'videos/english.mp4'
    uri = v.upload(file_name, data={  'name': 'fast mp4', 'description': 'The fast mp4 first uploading.' })

    response = v.get(uri + '?fields=transcode.status').json()
    if response['transcode']['status'] == 'complete':
        test =  'Your video finished transcoding.'
    elif response['transcode']['status'] == 'in_progress':
        test =  'Your video is still transcoding.'
    else:
        test ='Your video encountered an error during transcoding.'

    response = v.get(uri + '?fields=link').json()
    print ("Your video link is: " + response['link']  )  


    
    #uri = '153631609'
    #response = v.get(uri)
    #test =  response.json()


    return render_template(template, test=test, title=title, STATIC_URL=STATIC_URL)    
    


@app.route('/test.html')
@app.route('/' + USER_LANG +'/test.html')
def test():
    title='Home'
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'index.html'
    #with open('myfile.html', 'w') as f:
    #    f.write(render_template(template, title=title, STATIC_URL=STATIC_URL))
    return app.send_static_file('test.html')  

@app.route('/testalk.html')
def testalk():
    title='Home'
    TPL = get_Device()
    template = TPL + USER_LANG +  '/' + 'index.html'
    #with open('myfile.html', 'w') as f:
    #    f.write(render_template(template, title=title, STATIC_URL=STATIC_URL))
    return app.send_static_file('testalk.html')    


