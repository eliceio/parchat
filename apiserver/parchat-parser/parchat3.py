import json

with open("sentence_noun_dict.json", "r") as f:
  sentence_nouns_dict = json.load(f)
sentences = list(sentence_nouns_dict.values())

from gensim import corpora

dictionary = corpora.Dictionary(sentences)
corpus = [dictionary.doc2bow(sentence) for sentence in sentences]


from gensim.models import LdaMulticore

LDA_model = LdaMulticore(corpus, workers=4, num_topics=30, id2word=dictionary, passes=1)
LDA_model.save("LDA.model")

import slack

slack.send("LDA model has been generated")
