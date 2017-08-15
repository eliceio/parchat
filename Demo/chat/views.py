from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from scipy.spatial.distance import cosine
import gensim
import numpy as np
import json
from konlpy.tag import Twitter
import jpype
import requests


""" ALL + METADATA """
with open('chat/static/models/all_meta_A.json', 'r') as fp:
    all_meta_answer = json.load(fp)
with open('chat/static/models/all_meta_Avec.json', 'r') as fp:
    all_meta_answer_vectors = json.load(fp)
with open('chat/static/models/all_meta_LSTSQ.json', 'r') as fp:
    A_estimate_all_meta = json.load(fp)


""" Progressive """
with open('chat/static/models/pro_A.json', 'r') as fp:
    progressive_answer = json.load(fp)
with open('chat/static/models/pro_Avec.json', 'r') as fp:
    progressive_answer_vectors = json.load(fp)
with open('chat/static/models/pro_LSTSQ.json', 'r') as fp:
    A_estimate_pro = json.load(fp)


""" Conservative """
with open('chat/static/models/con_A.json', 'r') as fp:
    conservative_answer = json.load(fp)
with open('chat/static/models/con_Avec.json', 'r') as fp:
    conservative_answer_vectors = json.load(fp)
with open('chat/static/models/con_LSTSQ.json', 'r') as fp:
    A_estimate_con = json.load(fp)


""" LDA, W2V, KoNLPy.Twitter """
with open('chat/static/models/sh_all_nouns.json', "r") as fp:
    sh_all_nouns = json.load(fp)
sh_dictionary = gensim.corpora.Dictionary(sh_all_nouns)
sh_wor2vec_model = gensim.models.Word2Vec.load('chat/static/models/sh_W2V.model')
sh_lda_model = gensim.models.ldamodel.LdaModel.load('chat/static/models/sh_LDA.model')

with open('chat/static/models/gm_all_nouns.json', "r") as fp:
    gm_all_nouns = json.load(fp)
gm_dictionary = gensim.corpora.Dictionary(list(gm_all_nouns.values()))
gm_wor2vec_model = gensim.models.Word2Vec.load('chat/static/models/gm_W2V.model')
gm_lda_model = gensim.models.ldamodel.LdaModel.load('chat/static/models/gm_LDA.model')
Tw = Twitter()


@ensure_csrf_cookie
def chat_all(request):
    return render(request, "chat_all.html")


@ensure_csrf_cookie
def chat_all_meta(request):
    return render(request, "chat_all_meta.html")


@ensure_csrf_cookie
def chat_progressive(request):
    return render(request, "chat_progressive.html")


@ensure_csrf_cookie
def chat_conservative(request):
    return render(request, "chat_conservative.html")


@ensure_csrf_cookie
def echo_user(request):
    response_type = "user"
    args = {
        "user_type": response_type,
        "content": request.POST["message"]
    }
    return render(request, "message.html", args)


@ensure_csrf_cookie
def response_progressive(request):
    response_type = grab_response_type(request.POST["request_from"])
    message = request.POST["message"]
    metrics = request.POST.getlist("metrics[]")

    response = get_progressive_response(message)
    content = res2html(response, metrics)

    args = {
        "user_type": response_type,
        "content": content,
    }
    return render(request, "message.html", args)


def get_progressive_response(message):
    response_vector = np.dot(vectorize_230(message), A_estimate_pro)

    # L2 norm
    l2_distances = np.linalg.norm(progressive_answer_vectors - response_vector, axis=1)
    l2_closest_idx = np.argmin(l2_distances)
    l2_response = progressive_answer[l2_closest_idx][0]

    # Cosine distance
    cosine_distances = [cosine(a, response_vector) for a in progressive_answer_vectors]
    cosine_closest_idx = np.argmin(cosine_distances)
    cosine_response = progressive_answer[cosine_closest_idx][0]

    response = {
        "modelScore": 0.1,
        "result": {
            "l2": {
                "sentence": l2_response,
                "score": 0.2,
            },
            "cosine": {
                "sentence": cosine_response,
                "score": 0.3,
            }
        }
    }

    return response


@ensure_csrf_cookie
def response_conservative(request):
    response_type = grab_response_type(request.POST["request_from"])
    message = request.POST["message"]
    metrics = request.POST.getlist("metrics[]")

    response = get_conservative_response(message)
    content = res2html(response, metrics)

    args = {
        "user_type": response_type,
        "content": content,
    }
    return render(request, "message.html", args)


def get_conservative_response(message):
    response_vector = np.dot(vectorize_230(message), A_estimate_con)

    # L2 distance
    l2_distances = np.linalg.norm(conservative_answer_vectors - response_vector, axis=1)
    l2_closest_idx = np.argmin(l2_distances)
    l2_response = conservative_answer[l2_closest_idx][0]

    # Cosine distance
    cosine_distances = [cosine(a, response_vector) for a in conservative_answer_vectors]
    cosine_closest_idx = np.argmin(cosine_distances)
    cosine_response = conservative_answer[cosine_closest_idx][0]

    response = {
        "modelScore": 0.1,
        "result": {
            "l2": {
                "sentence": l2_response,
                "score": 0.2,
            },
            "cosine": {
                "sentence": cosine_response,
                "score": 0.3,
            }
        }
    }

    return response


@ensure_csrf_cookie
def response_all(request):
    response_type = grab_response_type(request.POST["request_from"])
    message = request.POST["message"]
    metrics = request.POST.getlist("metrics[]")

    response = get_all_response(message)
    content = res2html(response, metrics)

    args = {
        "user_type": response_type,
        "content": content,
    }
    return render(request, "message.html", args)


def get_all_response(message):
    res = requests.post(
        "http://elice-guest-ds-01.koreasouth.cloudapp.azure.com:5000",
        data=json.dumps({
            "msg": message
        }),
        headers={
            "Content-Type": "application/json; charset=utf-8"
        }
    )
    answer = res.text

    response = {
        "modelScore": 0.1,
        "result": {
            "l2": {
                "sentence": answer,
                "score": 0.2,
            },
            "cosine": {
                "sentence": answer,
                "score": 0.3,
            }
        }
    }

    return response


@ensure_csrf_cookie
def response_all_meta(request):
    response_type = grab_response_type(request.POST["request_from"])
    message = request.POST["message"]
    metrics = request.POST.getlist("metrics[]")

    response = get_all_meta_response(message)
    content = res2html(response, metrics)

    args = {
        "user_type": response_type,
        "content": content,
    }
    return render(request, "message.html", args)


def get_all_meta_response(message):
    response_vector = np.dot(vectorize_255(message), A_estimate_all_meta)

    # L2 distance
    l2_distances = np.linalg.norm(all_meta_answer_vectors - response_vector, axis=1)
    l2_closest_idx = np.argmin(l2_distances)
    l2_response = all_meta_answer[l2_closest_idx]

    # Cosine distance
    cosine_distances = [cosine(a, response_vector) for a in all_meta_answer_vectors]
    cosine_closest_idx = np.argmin(cosine_distances)
    cosine_response = all_meta_answer[cosine_closest_idx]

    response = {
        "modelScore": 0.1,
        "result": {
            "l2": {
                "sentence": l2_response,
                "score": 0.2,
            },
            "cosine": {
                "sentence": cosine_response,
                "score": 0.3,
            }
        }
    }

    return response


def res2html(response, metrics):
    if len(metrics) == 1:
        metric = metrics[0]
        html = response["result"][metric]["sentence"]
    else:
        l2 = response["result"]["l2"]["sentence"]
        cosine = response["result"]["cosine"]["sentence"]
        html = '''
            <strong>[L2 norm]</strong><br>
            %s
            <br>
            <strong>[Cosine distance]</strong><br>
            %s
        ''' % (l2, cosine)

    return html


def grab_response_type(string):
    response_type_dict = {
        "progressive": "Progressive Congressman",
        "conservative": "Conservative Congressman",
        "all": "Congressman",
        "all_meta": "Congressman+",
    }

    for type in response_type_dict:
        if type in string:
            return response_type_dict[type]
    return "Congressman"


def vectorize_230(sentence):
    jpype.attachThreadToJVM()
    morphs = Tw.morphs(sentence)

    wv = sh_wor2vec_model.wv
    w2v_vector_list = [wv[word] if word in wv else np.zeros(200) for word in morphs]
    w2v_vector = np.mean(w2v_vector_list, axis=0)

    doc2bow = [sh_dictionary.doc2bow(morphs)]
    lda_topic_list = sh_lda_model.get_document_topics(doc2bow)[0]
    lda_vector = np.zeros(30)
    for topic_ix, possibility in lda_topic_list:
        lda_vector[topic_ix] = possibility

    sentence_vector = np.concatenate([w2v_vector, lda_vector])
    assert len(sentence_vector) == 230

    return sentence_vector


def vectorize_255(sentence):
    jpype.attachThreadToJVM()
    nouns = Tw.nouns(sentence)

    wv = gm_wor2vec_model.wv
    w2v_vector_list = [wv[word] if word in wv else np.zeros(200) for word in nouns]
    w2v_vector = np.mean(w2v_vector_list, axis=0)

    doc2bow = [gm_dictionary.doc2bow(nouns)]
    lda_topic_list = gm_lda_model.get_document_topics(doc2bow)[0]
    lda_vector = np.zeros(30)
    for topic_ix, possibility in lda_topic_list:
        lda_vector[topic_ix] = possibility

    party_vector = np.full(24, 0)
    word_len_vector = [len(nouns) / 153]

    sentence_vector = np.concatenate([w2v_vector, lda_vector, party_vector, word_len_vector])
    assert len(sentence_vector) == 255

    return sentence_vector
