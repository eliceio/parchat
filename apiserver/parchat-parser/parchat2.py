import json

with open("sentence_noun_dict.json", "r") as f:
  sentence_nouns_dict = json.load(f)

sentences = list(sentence_nouns_dict.values())

from gensim.models.word2vec import Word2Vec

W2V_model = Word2Vec(sentences, size=200, workers=4, iter=10)
W2V_model.save("W2V.model")

import slack
slack.send("Word2vec model has been generated")
