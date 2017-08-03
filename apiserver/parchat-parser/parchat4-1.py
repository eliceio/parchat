import json

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

del stmts
print("Length: ", len(qa_pair_list))
