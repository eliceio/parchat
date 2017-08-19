from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from scipy.spatial.distance import cosine
import gensim
import numpy as np
import json
from konlpy.tag import Twitter
import jpype
import requests


""" Progressive """
with open('chat/static/models/pro_A_part.json', 'r') as fp:
    pro_answers = json.load(fp)
with open('chat/static/models/pro_A_part_vec.json', 'r') as fp:
    pro_answer_vectors = json.load(fp)
with open('chat/static/models/A_estimate_pro.json', 'r') as fp:
    pro_A_estimate = json.load(fp)


""" Conservative """
with open('chat/static/models/con_A_part.json', 'r') as fp:
    con_answers = json.load(fp)
with open('chat/static/models/con_A_part_vec.json', 'r') as fp:
    con_answer_vectors = json.load(fp)
with open('chat/static/models/A_estimate_con.json', 'r') as fp:
    con_A_estimate = json.load(fp)


""" Neutral1 + METADATA """
with open('chat/static/models/neutral1_A_part.json', 'r') as fp:
    neu1_answers = json.load(fp)
with open('chat/static/models/neutral1_A_part_vec.json', 'r') as fp:
    neu1_answer_vectors = json.load(fp)
with open('chat/static/models/A_estimate_neutral1.json', 'r') as fp:
    neu1_A_estimate = json.load(fp)


""" Neutral2 + METADATA """
with open('chat/static/models/neutral2_meta_A.json', 'r') as fp:
    neu2_meta_answers = json.load(fp)
with open('chat/static/models/neutral2_meta_A_vec.json', 'r') as fp:
    neu2_meta_answer_vectors = json.load(fp)
with open('chat/static/models/neutral2_meta_A_estimate.json', 'r') as fp:
    neu2_meta_A_estimate = json.load(fp)


""" LDA, W2V, KoNLPy.Twitter """
sh_dictionary = gensim.corpora.Dictionary.load("chat/static/models/sh_LDA.model.id2word")
sh_wor2vec_model = gensim.models.Word2Vec.load('chat/static/models/sh_W2V.model')
sh_lda_model = gensim.models.ldamodel.LdaModel.load('chat/static/models/sh_LDA.model')

gm_dictionary = gensim.corpora.Dictionary.load("chat/static/models/gm_LDA.model.id2word")
gm_wor2vec_model = gensim.models.Word2Vec.load('chat/static/models/gm_W2V.model')
gm_lda_model = gensim.models.ldamodel.LdaModel.load('chat/static/models/gm_LDA.model')

Tw = Twitter()


boilerplate = {
    '안녕':'반말하지 마십시오.',
    '안녕?':'반말하지 마십시오',
    '안녕하세요': '안녕하세요.',
    '안녕 하세요':'안녕하세요',
    '안녕하세요 위원님': '안녕하세요 위원님.',
    '안녕하세요 의원님':'안녕하세요 의원님.',
    '안녕하세요위원님':'안녕하세요위원님.',
    '안녕하세요의원님': '안녕하세요의원님',
    '안녕히계세요': '아직 회의 안 끝났습니다.',
    '안녕히 계세요': '아직 회의 안 끝났습니다.'
}


@ensure_csrf_cookie
def chat(request):
    return render(request, "chat/chatting_room.html")


@ensure_csrf_cookie
def echo_user(request):
    model_name = "user"
    args = {
        "model_name": model_name,
        "content": request.POST["message"]
    }
    return render(request, "chat/message.html", args)


@ensure_csrf_cookie
def response(request):
    message = request.POST["message"]
    metrics = request.POST.getlist("metrics[]")
    model_name, model_args = grab_model_args(request.POST["request_from"], message)

    response = get_response(message, **model_args)
    content = res2html(response, metrics)

    args = {
        "model_name": model_name,
        "content": content,
    }
    return render(request, "chat/message.html", args)


def grab_model_args(request_url, message):
    model_name = grab_model_name(request_url)

    if model_name == "progressive":
        topic = sh_get_topic(message)
        args = {
            "use_api": False,
            "A_estimate": pro_A_estimate[topic],
            "answers": pro_answers[topic],
            "answer_vectors": pro_answer_vectors[topic],
            "vectorize_func": vectorize_230,
        }
    elif model_name == "conservative":
        topic = sh_get_topic(message)
        args = {
            "use_api": False,
            "A_estimate": con_A_estimate[topic],
            "answers": con_answers[topic],
            "answer_vectors": con_answer_vectors[topic],
            "vectorize_func": vectorize_230,
        }
    elif model_name == "neutral1":
        topic = sh_get_topic(message)
        args = {
            "use_api": False,
            "A_estimate": neu1_A_estimate[topic],
            "answers": neu1_answers[topic],
            "answer_vectors": neu1_answer_vectors[topic],
            "vectorize_func": vectorize_230,
        }
    elif model_name == "neutral2":
        args = {
            "use_api": True,
            "url": "http://elice-guest-ds-01.koreasouth.cloudapp.azure.com:5000",
        }
    elif model_name == "neutral2_meta":
        args = {
            "use_api": False,
            "A_estimate": neu2_meta_A_estimate,
            "answers": neu2_meta_answers,
            "answer_vectors": neu2_meta_answer_vectors,
            "vectorize_func": vectorize_255,
        }

    return model_name, args


def get_response(message, use_api, A_estimate=None, answers=None, answer_vectors=None, vectorize_func=None, url=None):
    if message in boilerplate:
        l2_response = boilerplate[message]
        cosine_response = boilerplate[message]
    elif use_api:
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
        "neutral2_meta",
        "neutral2",
        "neutral1",
    ]

    for response_type in response_types:
        if response_type in string:
            return response_type
    return "neutral1"


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
    w2v_vector = np.mean(w2v_vector_list, axis=0) if w2v_vector_list else np.zeros(200)

    doc2bow = [gm_dictionary.doc2bow(nouns)]
    lda_topic_list = gm_lda_model.get_document_topics(doc2bow)[0]
    lda_vector = np.zeros(30)
    for topic_ix, possibility in lda_topic_list:
        lda_vector[topic_ix] = possibility

    party_vector = np.full(24, 1/24)
    word_len_vector = [len(nouns) / 153]

    sentence_vector = np.concatenate([w2v_vector, lda_vector, party_vector, word_len_vector])
    assert len(sentence_vector) == 255

    return sentence_vector


def sh_get_topic(message):
    jpype.attachThreadToJVM()
    nouns = Tw.nouns(message)

    topics = sh_lda_model.get_document_topics(sh_dictionary.doc2bow(nouns))

    max_prob = round(topics[0][1], 5)
    temp_prob = round(topics[0][1], 5)
    max_part = topics[0][0]

    check = 0

    for i in range(1, len(topics)):
        if round(topics[i][1], 5) != temp_prob:
            check = 1
            break

    if check == 0:
        return (str(30))

    if check == 1:
        for part, prob in topics:
            if round(prob, 5) > max_prob:
                max_prob = round(prob, 5)
                max_part = part

        return str(max_part)
