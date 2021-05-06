"""
The submission format for the task will follow the standard TREC format:

qid Q0 doc rank score tag

With:

qid: The topic number.
Q0: Unused, should always be Q0.
doc: The document ID (the official args.me ID) returned by your system for the topic qid.
rank: The rank the document is retrieved at.
score: The score (integer or floating point) that generated the ranking. The score must be in descending (non-increasing) order. It is important to handle tied scores (trec_eval sorts documents by the score values and not your rank values).
tag: A tag that identifies your group and the method you used to produce the run.
"""

import argparse

import xmltodict
import pandas as pd

from elasticsearch import Elasticsearch
from sentence_transformers import CrossEncoder

es = Elasticsearch()
index_name = "debateorg-preprocessed"

pretrained_model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
model = CrossEncoder(pretrained_model_name, max_length = 504)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input Directory", type=str)
    parser.add_argument("-o", help="Output Directory String", type=str)
    argv = parser.parse_args()
    return argv

def read_xml(path):
    with open(path) as f:
        lines = f.read()
        
    topics = xmltodict.parse(lines)
    topic_dict = {}
    for topic in topics['topics']['topic']:
        topic_dict.update({topic['number']: topic['title']})
    return topic_dict

def search(index_, topics_dict, query_id, top_k):
    query_result_pairs = list()
    query = topics_dict[query_id]
    results = es.search(index = index_, \
        body={"query": {"match": {"text": query} } }, size = top_k)['hits']['hits']
    for result in results:
        _id = result['_id']
        text = result['_source']['text']
        query_result_pairs.append((query_id, _id, query, text))
    return query_result_pairs

def search_all_topics(index_, topics_dict, top_k = 25):
    sentence_pairs = {}
    for tid, tname in topics_dict.items():
        results = search(index_, topics_dict, tid, top_k)
        sentence_pairs[tid] = results
    return sentence_pairs


if __name__ == "__main__":
    args = parse_args()
    input_path = args.i
    
    topics_dict = read_xml(input_path+"topics.xml")

    sentence_pairs_dict = search_all_topics(index_name, topics_dict, 50)

    output_lines = []
    for k,v in sentence_pairs_dict.items():
        df = pd.DataFrame(v,columns=['qid','doc','Question','original_text'])
        qa_pairs = list(df[['Question','original_text']].itertuples(index=False,name=None))
        similarity_scores = model.predict(qa_pairs)
        df['score'] = similarity_scores
        df = df.sort_values(by=['score'],ascending=False)
        df['rank'] = df['score'].rank(method="first",ascending=False)
        df["rank"] = df["rank"].astype(int)
        print(k, df.head())
        for row in df.itertuples():
            qid = row[1]
            doc = row[2]
            rank = row[6]
            score = row[5]
            output_string = qid + " Q0 " + doc + " " +\
                    str(rank) + " " + str(score) + " macbethPretrainedBaseline"
            output_lines.append(output_string)

    output_path = args.o + "run.txt"
    with open(output_path, 'w') as writefile:
        for line in output_lines:
            writefile.writelines(line+"\n")