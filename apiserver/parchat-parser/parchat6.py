import json
from gensim.models import Word2Vec
from gensim.models import LdaMulticore
from gensim import corpora
import numpy as np

W2V_dim = 200
LDA_dim = 30
with open("sentence_noun_dict.json", "r") as f:
  sentence_nouns_dict = json.load(f)

sentences = list(sentence_nouns_dict.values())

dictionary = corpora.Dictionary(sentences)

del sentences

W2V_model = Word2Vec.load("W2V.model")
LDA_model = LdaMulticore.load("LDA.model")

sentence_vector_dict = {}

for ix, (sentence, words) in enumerate(sentence_nouns_dict.items()):
  w2v_vector = np.mean([W2V_model.wv[word] if word in W2V_model.wv else np.zeros(W2V_dim) for word in words], axis=0)
  bow = dictionary.doc2bow(words)
  lda_topics = LDA_model.get_document_topics(bow)
  lda_vector = np.zeros(LDA_dim)
  for topic in lda_topics:
    lda_vector[topic[0]] = topic[1]
  sentence_vector_dict[sentence] = np.concatenate([w2v_vector, lda_vector]).tolist()

list(sentence_vector_dict.keys())[0]
list(sentence_vector_dict.values())[0]

with open("sentence_vector_dict.json", "w") as f:
  json.dump(sentence_vector_dict, f)


import slack
slack.send("Reverse table has been generated")
