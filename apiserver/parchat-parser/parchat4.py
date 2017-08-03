import json
import slack

with open('stmt_list.json', 'r') as f:
  stmts = json.load(f)

print("1. generating seq", flush=True)

def is_qa_pair(q_stmt, a_stmt):
  seq = q_stmt['sequence'] + 1 == a_stmt['sequence']
  same_meeting = q_stmt["meeting_id"] == a_stmt["meeting_id"]
  diff_person = q_stmt["person_id"] != a_stmt["person_id"]
  
  return seq and same_meeting and diff_person


print("2. generating qa pair list")

qa_pair_list = []
for idx in range(1, len(stmts)):
  if is_qa_pair(stmts[idx-1], stmts[idx]):
    questions = stmts[idx-1]["sentence_word_matrix"]
    answers = stmts[idx]["sentence_word_matrix"]
    for question in questions:
      for answer in answers:
        qa_pair_list.append((question, answer, {}))

print("Length: ", len(qa_pair_list))

with open('./qa_pair.json', 'w') as f:
  json.dump(qa_pair_list, f)
slack.send("3. generation models")

import gensim
W2V_model = gensim.models.Word2Vec.load("W2V.model")
LDA_model = gensim.models.LdaMulticore.load("LDA.model")

import json

with open("sentence_noun_dict.json", "r") as f:
  sentence_nouns_dict = json.load(f)

sentences = list(sentence_nouns_dict.values())
dictionary = gensim.corpora.Dictionary(sentences)

del sentences

slack.send("4. generating last ones")

import numpy as np

W2V_dim = 200
LDA_dim = 30

def vectorize(words, W2V_model, LDA_model):
  w2v_vector = np.mean([W2V_model.wv[word] if word in W2V_model.wv else np.zeros(W2V_dim) for word in words], axis=0)
  bow = dictionary.doc2bow(words)
  lda_topics = LDA_model.get_document_topics(bow)
  lda_vector = np.zeros(LDA_dim)
  for topic in lda_topics:
    lda_vector[topic[0]] = topic[1]
  vector = np.concatenate([w2v_vector, lda_vector])
  
  return vector

dropped_sentences = []
qa_vector_list = []
for idx, qa_pair in enumerate(qa_pair_list, 1):
  if idx % 100000 == 0:
    slack.send("{} completed".format(idx))
  question, answer, _ = qa_pair
  q_v = vectorize(question, W2V_model, LDA_model)
  a_v = vectorize(answer, W2V_model, LDA_model)
  if np.any(q_v) and np.any(a_v):
    qa_vector_list.append((q_v.tolist(), a_v.tolist(), {}))

slack.send("Vectorize all has been completed")

#with open("QA_vector_list", "w") as f:
#  json.dump(qa_vector_list, f)

#qa_vector_list = [(q.tolist(), a.tolist(), meta) for q, a, meta in qa_vector_list]

with open("QA.json", "w") as f:
  json.dump(qa_vector_list, f)
