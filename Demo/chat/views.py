from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from scipy.spatial.distance import cosine
import gensim
import numpy as np
import json
from konlpy.tag import Twitter
import jpype
import requests


with open('chat/static/models/pro_A.json', 'r') as fp:
    progressive_answer = json.load(fp)
with open('chat/static/models/pro_Avec.json', 'r') as fp:
    progressive_answer_vectors = json.load(fp)
with open('chat/static/models/LSTQ_pro.json', 'r') as fp:
    A_estimate_pro = json.load(fp)
with open('chat/static/models/con_A.json', 'r') as fp:
    conservative_answer = json.load(fp)
with open('chat/static/models/con_Avec.json', 'r') as fp:
    conservative_answer_vectors = json.load(fp)
with open('chat/static/models/LSTQ_con.json', 'r') as fp:
    A_estimate_con = json.load(fp)
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
def chat_sh_pro(request):
    return render(request, "chat_sh_pro.html")


@ensure_csrf_cookie
def chat_sh_con(request):
    return render(request, "chat_sh_con.html")


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
def answer_sh_pro(request):
    response_type = grab_response_type(request.POST["request_from"])
    message = request.POST["message"]

    answer = get_progressive_response(message)

    args = {
        "user_type": response_type,
        "content": answer
    }
    return render(request, "message.html", args)


@ensure_csrf_cookie
def answer_sh_con(request):
    response_type = grab_response_type(request.POST["request_from"])
    message = request.POST["message"]

    answer = get_conservative_response(message)

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
    response_type_dict = {
        "gyeongmin": "Gyeongmin",
        "soonho/pro": "Soonho - Progressive",
        "soonho/con": "Soonho - Conservative",
    }

    for type in response_type_dict:
        if type in string:
            return response_type_dict[type]


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


def get_progressive_response(message):
    response_vector = np.dot(vectorize(message), A_estimate_pro)

    # L2 norm
    l2_distances = np.linalg.norm(progressive_answer_vectors - response_vector, axis=1)
    l2_closest_idx = np.argmin(l2_distances)
    l2_response = progressive_answer[l2_closest_idx][0]

    # Cosine distance
    cosine_distances = [cosine(a, response_vector) for a in progressive_answer_vectors]
    cosine_closest_idx = np.argmin(cosine_distances)
    cosine_response = progressive_answer[cosine_closest_idx][0]

    response = '''
        <strong>[L2 norm]</strong><br>
        %s
        <br>
        <strong>[Cosine distance]</strong><br>
        %s
    ''' % (l2_response, cosine_response)

    print('Q:', message)
    print('Predict A:', response)

    return response


def get_conservative_response(message):
    response_vector = np.dot(vectorize(message), A_estimate_con)

    # L2 distance
    l2_distances = np.linalg.norm(conservative_answer_vectors - response_vector, axis=1)
    l2_closest_idx = np.argmin(l2_distances)
    l2_response = conservative_answer[l2_closest_idx][0]

    # Cosine distance
    cosine_distances = [cosine(a, response_vector) for a in conservative_answer_vectors]
    cosine_closest_idx = np.argmin(cosine_distances)
    cosine_response = conservative_answer[cosine_closest_idx][0]

    response = '''
        <strong>[L2 norm]</strong><br>
        %s
        <br>
        <strong>[Cosine distance]</strong><br>
        %s
    ''' % (l2_response, cosine_response)
    print('Q:', message)
    print('Predict A:', response)

    return response
