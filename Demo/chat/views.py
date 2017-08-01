from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
import gensim
import numpy as np
import json
from konlpy.tag import Twitter
import pickle


with open('chat/static/models/A.pickle','rb') as fp:
    A = pickle.load(fp)
with open('chat/static/models/vector_A.json', 'r') as fp:
    vector_A = json.load(fp)
with open('chat/static/models/LSTQ.json', 'r') as fp:
    A_estimate = json.load(fp)
with open('chat/static/models/all_nouns.json', "r") as fp:
    all_nouns = json.load(fp)
dictionary = gensim.corpora.Dictionary(all_nouns)
wor2vec_model = gensim.models.Word2Vec.load('chat/static/models/word2vecmodel')
lda_model = gensim.models.ldamodel.LdaModel.load('chat/static/models/ldamodel')
Tw = Twitter()


@ensure_csrf_cookie
def progressive(request):
    return render(request, "chat.html")


@ensure_csrf_cookie
def conservative(request):
    return render(request, "chat.html")


@ensure_csrf_cookie
def echo(request):
    response_type = grab_response_type(request.POST["request_from"])
    message = request.POST["message"]

    print(message)

    answer = return_A(message)

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
        "progressive",
        "conservative"
    ]
    for type in response_types:
        if type in string:
            return type


def vector(q):
    morphs = Tw.morphs(q)
    print("pass")

    ldalist = np.zeros(30)

    doc2bow = [dictionary.doc2bow(morphs)]

    for pair in lda_model.get_document_topics(doc2bow)[0]:
        ldalist[pair[0]] = pair[1]

    k = []

    for word in morphs:
        try:
            k.append(wor2vec_model.wv[word])
        except:
            k.append(np.zeros(200))

    k = np.array(k)

    word2vec = np.zeros(200)

    for i in range(len(word2vec)):
        word2vec[i] = (np.mean(k[:, i]))

    return (np.append(word2vec, ldalist).tolist())


def return_A(message):
    ex_A = np.dot(vector(message), A_estimate)

    min_dis = 1000
    index = 0
    for j in range(len(vector_A)):
        dis = np.linalg.norm((vector_A[j] - ex_A))
        if dis <= min_dis:
            min_dis = dis
            index = j

    print('Q:', message)
    print('Predict A:', A[index][0])

    return A[index][0]