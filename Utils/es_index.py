from pathlib import Path

import ujson
from elasticsearch import Elasticsearch

#Reading into a list of dicts

def read_jsonl(file_path):
    with Path(file_path).open('r', encoding='utf8') as f:
        for line in f:
            try:  # hack to handle broken jsonl
                yield ujson.loads(line.strip())
            except ValueError:
                continue

path = "/mnt/data/touche-macbeth/preprocessed_debateorg.jsonl"
d = read_jsonl(path)

lines = []
i = 0
while True:
    try:
        lines.append(next(d))
        i=i+1
        if i%100000 == 0:
            print("Lines Read: ", i)
    except Exception as e:
        print(e)
        break

#Elasticsearch

es = Elasticsearch()
index_name = "debateorg-preprocessed"

es.indices.create(index=index_name, ignore=[400]) 

for i,row in enumerate(lines):
    if not i%10000:
        print("Lines Indexed: ", i)
    response = es.index(
        index = index_name,
        id = row['id'],
        body = {"text" : row["text"]
               })
            
#Test
s = "Should bullfighting be banned? Why or why not?"
res = es.search(index = index_name, body={"query": {"match": {"text": s} } }, size = 25)['hits']['hits']

print("Elasticsearch test results: ", res)