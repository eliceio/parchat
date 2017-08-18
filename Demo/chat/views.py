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
    all_meta_answers = json.load(fp)
with open('chat/static/models/all_meta_Avec.json', 'r') as fp:
    all_meta_answer_vectors = json.load(fp)
with open('chat/static/models/all_meta_LSTSQ.json', 'r') as fp:
    A_estimate_all_meta = json.load(fp)


""" Progressive """
with open('chat/static/models/pro_A.json', 'r') as fp:
    progressive_answers = json.load(fp)
with open('chat/static/models/pro_Avec.json', 'r') as fp:
    progressive_answer_vectors = json.load(fp)
with open('chat/static/models/pro_LSTSQ.json', 'r') as fp:
    A_estimate_pro = json.load(fp)


""" Conservative """
with open('chat/static/models/con_A.json', 'r') as fp:
    conservative_answers = json.load(fp)
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
    model_name = "user"
    args = {
        "model_name": model_name,
        "content": request.POST["message"]
    }
    return render(request, "message.html", args)


@ensure_csrf_cookie
def response(request):
    model_name, model_args = grab_model_args(request.POST["request_from"])
    message = request.POST["message"]
    metrics = request.POST.getlist("metrics[]")

    response = get_response(message, **model_args)
    # response = get_all_meta_response(message)
    content = res2html(response, metrics)

    args = {
        "model_name": model_name,
        "content": content,
    }
    return render(request, "message.html", args)


def grab_model_args(request_url):
    model_name = grab_model_name(request_url)

    if model_name == "progressive":
        args = {
            "use_api": False,
            "A_estimate": A_estimate_pro,
            "answers": progressive_answers,
            "answer_vectors": progressive_answer_vectors,
            "vectorize_func": vectorize_230,
        }
    elif model_name == "conservative":
        args = {
            "use_api": False,
            "A_estimate": A_estimate_con,
            "answers": conservative_answers,
            "answer_vectors": conservative_answer_vectors,
            "vectorize_func": vectorize_230,
        }
    elif model_name == "all":
        args = {
            "use_api": True,
            "url": "http://elice-guest-ds-01.koreasouth.cloudapp.azure.com:5000",
        }
    elif model_name == "all_meta":
        args = {
            "use_api": False,
            "A_estimate": A_estimate_all_meta,
            "answers": all_meta_answers,
            "answer_vectors": all_meta_answer_vectors,
            "vectorize_func": vectorize_255,
        }

    return model_name, args


def get_response(message, use_api, A_estimate=None, answers=None, answer_vectors=None, vectorize_func=None, url=None):
    if use_api:
        res = requests.post(
            url,
            data=json.dumps({
                "msg": message
            }),
            headers={
                "Content-Type": "application/json; charset=utf-8"
            }
        )

        l2_response = res.text
        cosine_response = res.text
    else:
        response_vector = np.dot(vectorize_func(message), A_estimate)

        # L2 distance
        l2_distances = np.linalg.norm(answer_vectors - response_vector, axis=1)
        l2_closest_idx = np.argmin(l2_distances)
        l2_response = answers[l2_closest_idx]
        if isinstance(l2_response, list):
            l2_response = l2_response[0]

        # Cosine distance
        cosine_distances = [cosine(a, response_vector) for a in answer_vectors]
        cosine_closest_idx = np.argmin(cosine_distances)
        cosine_response = answers[cosine_closest_idx]
        if isinstance(cosine_response, list):
            cosine_response = cosine_response[0]

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


def grab_model_name(string):
    response_types = [
        "progressive",
        "conservative",
        "all_meta",
        "all",
    ]

    for response_type in response_types:
        if response_type in string:
            return response_type
    return "all"


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
