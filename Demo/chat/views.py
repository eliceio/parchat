from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
import gensim
import numpy as np
import json
from konlpy.tag import Twitter
import pickle
import jpype
import requests

with open('chat/static/models/A.pickle', 'rb') as fp:
    Answers = pickle.load(fp)
with open('chat/static/models/vector_A.json', 'r') as fp:
    Answer_vectors = json.load(fp)
with open('chat/static/models/LSTQ.json', 'r') as fp:
    A_estimate = json.load(fp)
with open('chat/static/models/all_nouns.json', "r") as fp:
    all_nouns = json.load(fp)
dictionary = gensim.corpora.Dictionary(all_nouns)
wor2vec_model = gensim.models.Word2Vec.load('chat/static/models/word2vecmodel')
lda_model = gensim.models.ldamodel.LdaModel.load('chat/static/models/ldamodel')
Tw = Twitter()


@ensure_csrf_cookie
def chat_gm(request):
    return render(request, "chat_gm.html")


@ensure_csrf_cookie
def chat_sh(request):
    return render(request, "chat_sh.html")


@ensure_csrf_cookie
def answer_gm(request):
    response_type = grab_response_type(request.POST["request_from"])
    message = request.POST["message"]

    res = requests.post(
        "http://elice-guest-ds-01.koreasouth.cloudapp.azure.com:5000",
        data = json.dumps({
            "msg": message
        }),
        headers = {
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    answer = res.text

    args = {
        "user_type": response_type,
        "content": answer
    }
    return render(request, "message.html", args)


@ensure_csrf_cookie
def answer_sh(request):
    response_type = grab_response_type(request.POST["request_from"])
    message = request.POST["message"]

    answer = get_response(message)

    args = {
        "user_type": response_type,
        "content": answer
    }
    return render(request, "message.html", args)


@ensure_csrf_cookie
def echo_user(request):
    response_type = "user"
    args = {
        "user_type": response_type,
        "content": request.POST["message"]
    }
    return render(request, "message.html", args)


def grab_response_type(string):
    response_types = [
        "gyeongmin",
        "soonho"
    ]
    for type in response_types:
        if type in string:
            return type


def vectorize(sentence):
    jpype.attachThreadToJVM()
    morphs = Tw.morphs(sentence)

    wv = wor2vec_model.wv
    w2v_vector_list = [wv[word] if word in wv else np.zeros(200) for word in morphs]
    w2v_vector = np.mean(w2v_vector_list, axis=0)

    doc2bow = [dictionary.doc2bow(morphs)]
    lda_topic_list = lda_model.get_document_topics(doc2bow)[0]
    lda_vector = np.zeros(30)
    for topic_ix, possibility in lda_topic_list:
        lda_vector[topic_ix] = possibility

    sentence_vector = np.concatenate([w2v_vector, lda_vector])

    return sentence_vector


def get_response(message):
    response_vector = np.dot(vectorize(message), A_estimate)
    distances = np.linalg.norm(Answer_vectors - response_vector, axis=1)
    closest_idx = np.argmin(distances)
    response = Answers[closest_idx][0]

    print('Q:', message)
    print('Predict A:', response)

    return response