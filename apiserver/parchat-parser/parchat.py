import json
from konlpy.tag import Twitter
from konlpy.tag import Kkma

import slack

slack.send('load pokr json file')
with open("../pokr.json", "r") as f:
  stmts = json.load(f)
print(len(stmts))

stmts = stmts[:100000]

twitter = Twitter()
filtered_sentence_nouns_dict = {}
filtered_stmt_list = []
for idx, stmt in enumerate(stmts, 1):
  sentences = [sentence.strip() for sentence in stmt["content"].split(".") if len(sentence.strip()) > 0 and len(sentence.split()) <= 100]
  if len(sentences) <= 8:
    stmt["sentence_word_matrix"] = []
    for sentence in sentences:
      nouns = twitter.nouns(sentence)
      if nouns:
        filtered_sentence_nouns_dict[sentence] = nouns
        stmt["sentence_word_matrix"].append(nouns)
    if stmt["sentence_word_matrix"]:
      stmt.pop("content")
      filtered_stmt_list.append(stmt)

import slack

slack.send(json.dumps(filtered_stmt_list[0]))

with open('stmt_list.json', 'w') as f:
  json.dump(filtered_stmt_list, f)

with open('sentence_noun_dict.json', 'w') as f:
  json.dump(filtered_sentence_nouns_dict, f)

slack.send("Preprocessing complete")
