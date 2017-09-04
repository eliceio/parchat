### Parchat
DEMO : http://bit.ly/elice_parchat

Korean National Assembly Member Chat-Bot

![Alt text](https://github.com/eliceio/parchat/blob/develop/Explanation.PNG)


### Development process
1.Data crawling - http://pokr.kr/ Minutes of the 19th National Assembly session and assembly member data.

2.Word Embedding - Word2Vec(skip-gram) and LDA.

3.QA pair prepare - Find the appropriate comments in the minutes of the meeting.

ex) Q: 증세입니까? A:글쎄 그 주목적은 결국은 ....

4.Vectorize - QA pair vectorize to 230 dimensions(word2vec(200) + lda(30)).

5.Least-square Method - Find Transformation Matrix to LSM. A(230) = Q(230) * Transformation Matrix.

6.Web Development - Django(Web server), Flask(API)


### Team members
- 김수인 - TA

- 고경민 - Project Manager, Server Management, API Design & Develop
- 김재욱 - Natural Language Processing
- 이창재 - Background Research
- 류호빈 - Front/Back-end developer, Data crawling
- 이순호 - Natural Language Processing, Data Analysis, Model Develop

