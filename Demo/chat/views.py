from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from scipy.spatial.distance import cosine
import gensim
import numpy as np
import json
from konlpy.tag import Twitter
import jpype
import requests
import logging


logger = logging.getLogger(__name__)


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
    def sh_closest_a(message, A_estimate):
        q_vec = vectorize_230(message)
        q_closest_idx = np.argmin(np.linalg.norm(sh_Q_vec - q_vec, axis=-1))
        q_closest_vec = sh_Q_vec[q_closest_idx]
        q_closest_topic = sh_Q_topic[q_closest_idx]
        a_closest_vec = np.dot(q_closest_vec, A_estimate[q_closest_topic])
        return a_closest_vec

    def hb_closest_a(message, A_estimate):
        q_vec = vectorize_255(message)
        q_closest_idx = np.argmin(np.linalg.norm(hb_Q_vec - q_vec, axis=-1))
        q_closest_vec = hb_Q_vec[q_closest_idx]
        a_closest_vec = np.dot(q_closest_vec, A_estimate)
        return a_closest_vec

    model_name = grab_model_name(request_url)

    if model_name == "progressive":
        topic = sh_get_topic(message)
        a_closest_vec = sh_closest_a(message, pro_A_estimate)
        args = {
            "use_api": False,
            "A_estimate": pro_A_estimate[topic],
            "answers": pro_answers[topic],
            "answer_vectors": pro_answer_vectors[topic],
            "vectorize_func": vectorize_230,
            "model_score": pro_model_score,
            "a_closest_vec": a_closest_vec,
        }
    elif model_name == "conservative":
        topic = sh_get_topic(message)
        a_closest_vec = sh_closest_a(message, con_A_estimate)
        args = {
            "use_api": False,
            "A_estimate": con_A_estimate[topic],
            "answers": con_answers[topic],
            "answer_vectors": con_answer_vectors[topic],
            "vectorize_func": vectorize_230,
            "model_score": con_model_score,
            "a_closest_vec": a_closest_vec,
        }
    elif model_name == "neutral1":
        topic = sh_get_topic(message)
        a_closest_vec = sh_closest_a(message, neu1_A_estimate)
        args = {
            "use_api": False,
            "A_estimate": neu1_A_estimate[topic],
            "answers": neu1_answers[topic],
            "answer_vectors": neu1_answer_vectors[topic],
            "vectorize_func": vectorize_230,
            "model_score": neu1_model_score,
            "a_closest_vec": a_closest_vec,
        }
    elif model_name == "neutral2":
        args = {
            "use_api": True,
            "url": "http://143.248.140.218:23457",
        }
    elif model_name == "neutral2_meta":
        a_closest_vec = hb_closest_a(message, neu2_meta_A_estimate)
        args = {
            "use_api": False,
            "A_estimate": neu2_meta_A_estimate,
            "answers": neu2_meta_answers,
            "answer_vectors": neu2_meta_answer_vectors,
            "vectorize_func": vectorize_255,
            "model_score": neu2_meta_model_score,
            "a_closest_vec": a_closest_vec,
        }

    return model_name, args


def get_response(message, use_api, A_estimate=None, answers=None, answer_vectors=None, vectorize_func=None, url=None, model_score=None, a_closest_vec=None):
    if message in boilerplate:
        l2_response = boilerplate[message]
        cosine_response = boilerplate[message]
        l2_score = -1
        cosine_score = -1
        model_score = -1
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

        return json.loads(res.text)
    else:
        response_vector = np.dot(vectorize_func(message), A_estimate)

        # L2 distance
        l2_distances = np.linalg.norm(answer_vectors - response_vector, axis=1)
        l2_closest_idx = np.argmin(l2_distances)
        l2_response = answers[l2_closest_idx]
        if isinstance(l2_response, list):
            l2_response = l2_response[0]

        # L2 score
        l2_response_vec = answer_vectors[l2_closest_idx]
        l2_score = np.linalg.norm(a_closest_vec - l2_response_vec)

        # Cosine distance
        cosine_distances = [cosine(a, response_vector) for a in answer_vectors]
        cosine_closest_idx = np.argmin(cosine_distances)
        cosine_response = answers[cosine_closest_idx]
        if isinstance(cosine_response, list):
            cosine_response = cosine_response[0]

        # Cosine score
        cosine_response_vec = answer_vectors[cosine_closest_idx]
        cosine_score = np.linalg.norm(a_closest_vec - cosine_response_vec)

    response = {
        "modelScore": model_score,
        "result": {
            "l2": {
                "sentence": l2_response,
                "score": l2_score,
            },
            "cosine": {
                "sentence": cosine_response,
                "score": cosine_score,
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
    return "congressperson"


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


""" Progressive """
logger.info("Load progressive model...")
with open('chat/static/models/pro_A_part.json', 'r') as fp:
    pro_answers = json.load(fp)
with open('chat/static/models/pro_A_part_vec.json', 'r') as fp:
    pro_answer_vectors = json.load(fp)
with open('chat/static/models/A_estimate_pro.json', 'r') as fp:
    pro_A_estimate = json.load(fp)


""" Conservative """
logger.info("Load conservative model...")
with open('chat/static/models/con_A_part.json', 'r') as fp:
    con_answers = json.load(fp)
with open('chat/static/models/con_A_part_vec.json', 'r') as fp:
    con_answer_vectors = json.load(fp)
with open('chat/static/models/A_estimate_con.json', 'r') as fp:
    con_A_estimate = json.load(fp)


""" Neutral1 """
logger.info("Load neutral1 model...")
with open('chat/static/models/neutral1_A_part.json', 'r') as fp:
    neu1_answers = json.load(fp)
with open('chat/static/models/neutral1_A_part_vec.json', 'r') as fp:
    neu1_answer_vectors = json.load(fp)
with open('chat/static/models/A_estimate_neutral1.json', 'r') as fp:
    neu1_A_estimate = json.load(fp)


""" Neutral2 + METADATA """
logger.info("Load neutral2+meta model...")
with open('chat/static/models/neutral2_meta_A.json', 'r') as fp:
    neu2_meta_answers = json.load(fp)
with open('chat/static/models/neutral2_meta_A_vec.json', 'r') as fp:
    neu2_meta_answer_vectors = json.load(fp)
with open('chat/static/models/neutral2_meta_A_estimate.json', 'r') as fp:
    neu2_meta_A_estimate = json.load(fp)


""" LDA, W2V, KoNLPy.Twitter """
logger.info("Load LDA, W2V model & Twitter tag...")
sh_dictionary = gensim.corpora.Dictionary.load("chat/static/models/sh_LDA.model.id2word")
sh_wor2vec_model = gensim.models.Word2Vec.load('chat/static/models/sh_W2V.model')
sh_lda_model = gensim.models.ldamodel.LdaModel.load('chat/static/models/sh_LDA.model')

gm_dictionary = gensim.corpora.Dictionary.load("chat/static/models/gm_LDA.model.id2word")
gm_wor2vec_model = gensim.models.Word2Vec.load('chat/static/models/gm_W2V.model')
gm_lda_model = gensim.models.ldamodel.LdaModel.load('chat/static/models/gm_LDA.model')

Tw = Twitter()


""" Model + Sentence Score"""
logger.info("Load files for score...")
with open("chat/static/models/sh_Q_vec.json", "r") as f:
    sh_Q_vec = json.load(f)
with open("chat/static/models/sh_Q_topic.json", "r") as f:
    sh_Q_topic = json.load(f)
with open("chat/static/models/hb_Q_vec.json", "r") as f:
    hb_Q_vec = json.load(f)
with open("chat/static/models/hb_A_vec.json", "r") as f:
    hb_A_vec = json.load(f)
# from tqdm import tqdm
# with open("chat/static/models/qa_sentence_pair.json", "r") as fp:
#     qa_sentence_pair_dict = json.load(fp)
#     qa_sentence_pair_dict = dict(list(qa_sentence_pair_dict.items())[:10000])
#
#     sh_Q_vec = [vectorize_230(sentence).tolist() for sentence in tqdm(qa_sentence_pair_dict.keys())]
#     sh_Q_topic = [sh_get_topic(sentence) for sentence in tqdm(qa_sentence_pair_dict.keys())]
#     sh_A_vec = [vectorize_230(sentence).tolist() for sentence in tqdm(qa_sentence_pair_dict.values())]
#     hb_Q_vec = [vectorize_255(sentence).tolist() for sentence in tqdm(qa_sentence_pair_dict.keys())]
#     hb_A_vec = [vectorize_255(sentence).tolist() for sentence in tqdm(qa_sentence_pair_dict.values())]
#     with open("chat/static/models/sh_Q_vec.json", "w") as f:
#         json.dump(sh_Q_vec, f)
#     with open("chat/static/models/sh_Q_topic.json", "w") as f:
#         json.dump(sh_Q_topic, f)
#     with open("chat/static/models/sh_A_vec.json", "w") as f:
#         json.dump(sh_A_vec, f)
#     with open("chat/static/models/hb_Q_vec.json", "w") as f:
#         json.dump(hb_Q_vec, f)
#     with open("chat/static/models/hb_A_vec.json", "w") as f:
#         json.dump(hb_A_vec, f)


""" Model Score """
pro_model_score = 9996018503.12
con_model_score = 5594089327.92
neu1_model_score = 236622379.774
neu2_meta_model_score = 0.465340291272

# with open("chat/static/models/sh_A_vec.json", "w") as f:
#     sh_A_vec = json.load(f)

# # Progressive, Conservative, Neutral1
# pro_model_score = 0
# con_model_score = 0
# neu1_model_score = 0
# for q_vec, q_topic, a_vec in tqdm(zip(sh_Q_vec, sh_Q_topic, sh_A_vec)):
#     pro_a_estimate_vec = np.dot(q_vec, pro_A_estimate[q_topic])
#     con_a_estimate_vec = np.dot(q_vec, con_A_estimate[q_topic])
#     neu1_a_estimate_vec = np.dot(q_vec, neu1_A_estimate[q_topic])
#
#     pro_model_score += np.sqrt(np.mean(np.square(pro_a_estimate_vec - a_vec)))
#     con_model_score += np.sqrt(np.mean(np.square(con_a_estimate_vec - a_vec)))
#     neu1_model_score += np.sqrt(np.mean(np.square(neu1_a_estimate_vec - a_vec)))
#
# pro_model_score /= len(qa_sentence_pair_dict)
# con_model_score /= len(qa_sentence_pair_dict)
# neu1_model_score /= len(qa_sentence_pair_dict)
#
# # Neutral2 + Metadata
# neu2_meta_error = hb_A_vec - np.dot(hb_Q_vec, neu2_meta_A_estimate)
# neu2_meta_model_score = np.mean(np.sqrt(np.mean(np.square(neu2_meta_error), axis=-1)))
#
# print()
# print(pro_model_score)
# print(con_model_score)
# print(neu1_model_score)
# print(neu2_meta_model_score)


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
