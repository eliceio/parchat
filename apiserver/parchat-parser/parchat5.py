import numpy as np
import json
import slack

slack.send('Load Q,A vector list')

qa = np.array(json.loads(open('./QA.json').read()))
Q = np.array(list(map(lambda x: x[0], qa)))
A = np.array(list(map(lambda x: x[1], qa)))

K = 230

slack.send('Estimate A matrix')

A_estimate = []
for k in range(K):
  slack.send('Line {} completed'.format(k))
  a = A[:, k]
  w = np.linalg.lstsq(Q, a)[0]
  A_estimate.append(w)

A_estimate = np.array(A_estimate).T
A_estimate = A_estimate.tolist()

slack.send('Dumping it!')

with open('./A_estimate.json', 'w') as f:
  json.dump(A_estimate, f)

slack.send("Model has been generated")
