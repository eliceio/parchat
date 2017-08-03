from flask import Flask, request;
import jpype
import json
import numpy as np
from gensim.models import Word2Vec
from gensim.models import LdaMulticore
import pickle
from gensim import corpora
from konlpy.tag import Twitter

twitter = Twitter()

lda_model = LdaMulticore.load('./LDA.model')
w2v_model = Word2Vec.load('./W2V.model')

sentence_noun_dict = json.loads(open('./sentence_noun_dict.json').read())
real_sentences = list(sentence_noun_dict.keys())
sentences = list(sentence_noun_dict.values())
dictionary = corpora.Dictionary(sentences)

A = np.array(json.loads(open('./A_estimate.json').read()))

sv = json.loads(open('./sentence_vector_dict.json').read())
orig_sentences = np.array(list(sv.keys()))
orig_vectors = np.array(list(sv.values()))

app = Flask(__name__)

@app.route("/", methods=["POST"])
def chat():
  jpype.attachThreadToJVM()
  msg = ""
  if request.method == 'POST':
    data = request.json
    msg = data['msg']

  print("Parsing {}".format(msg))
  vect = twitter.nouns(msg)
  v = np.mean([w2v_model.wv[word] if word in w2v_model.wv else np.zeros(200) for word in vect], axis=0)
  
  bow = dictionary.doc2bow(vect)
  lda_topics = lda_model.get_document_topics(bow)
  lda_vector = np.zeros(30)
  for topic in lda_topics:
    lda_vector[topic[0]] = topic[1]

  test_lda = np.array(lda_model[dictionary.doc2bow(vect)])[:, 1]
  test_w2v = np.array(v)
  print("Parsed {}, {}".format(np.shape(test_w2v), np.shape(test_lda)))
  w2v = np.reshape(test_w2v, (200, 1))
  lda = np.reshape(lda_vector, (30, 1))
  testvect = np.concatenate((w2v, lda))

  dv = np.dot(A, testvect)
  idx = np.argmin(np.sum(orig_vectors - dv.T, axis = 1) ** 2)
  return orig_sentences[idx]

if __name__ == "__main__":
  app.run(debug = True, host='0.0.0.0', port=5000)
