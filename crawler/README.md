# How to Use
```
$ python3 -m venv myvenv
$ source myvenv/bin/activate
(myvenv) $ pip install -r requirements.txt
(myvenv) $ scrapy crawl pokr
```
After the work is over, "pokr.json" file will be generated(It took about 40m in my computer to complete). <br/>
It contains list of items, and each item consists of the following parameters.

# Parameters
```
{
  "content": Content of the statement,
  "date": Date when the statement occurred. yyyy-mm-dd,
  "speaker": Speaker of the statement,
  "url": URL of the statement in http://pokr.kr,
  "meeting_id": Unique ID of the meeting of which the statement occurred, provided by Team POPONG. The ID is consisted of the Assembly ID (대) + Session ID (회) + Sitting ID (차) + an MD5 of the committee name,
  "meeting_title": Title of the meeting,
  "person_id": 	Person ID of the speaker, provided by Team POPONG,
  "sequence": The sequence number among statements in the corresponding meeting,
  "id": Unique ID of the statement,
}
```

# How to Load Data from "pokr.json"
```
import json
data = json.load(open("pokr.json", "r"))
```
