import argparse
import sys

import pandas as pd
from .helpers import load_pickle, read_xml

import hnswlib
from sentence_transformers import SentenceTransformer, CrossEncoder

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input Directory", type=str)
    parser.add_argument("-o", help="Output Directory String", type=str)
    parser.add_argument("-p", help="Index Path", type=str)
    argv = parser.parse_args()
    return argv

def load_index(index_name):
    index = hnswlib.Index(space = 'cosine', dim = 256)
    print("Loading Index")
    index.load_index(index_path)
    return index


def search(index_, pickle_, model, topics_dict, query_id, top_k):
    query_result_pairs = list()
    query = topics_dict[query_id]
    
    embedded_text = model.encode(query)
    labels, _ = index_.knn_query(embedded_text, k = 50)
    indexes_to_ids_text = [pickle_.get(label) for label in list(labels[0])]
    
    for result in indexes_to_ids_text:
        _id = result[0]
        text = result[1]
        query_result_pairs.append((query_id, _id, query, text))
        
    return query_result_pairs

def search_all_topics(index_, pickle_, model, topics_dict, top_k = 25):
    sentence_pairs = {}
    for tid, tname in topics_dict.items():
        results = search(index_, pickle_, model, topics_dict, tid, top_k)
        sentence_pairs[tid] = results
    return sentence_pairs


if __name__ == "__main__":
    args = parse_args()
    input_path = args.i
    sys.stdout.write("Input Path:"+input_path)

    pretrained_path = args.p 
    hns_index = load_index(pretrained_path+'hnswlib-gold.index') #"./output/training-biencoder-gold-latest/hnswlib.index"
    hns_index.set_ef(500)  # ef should always be > top_k_hits

    pickle_ = load_pickle(pretrained_path + "index_to_ids_text-gold.pkl")

    model = SentenceTransformer(pretrained_path+"args-me-biencoder-v1/")
    # ce_model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    topics_dict = read_xml(input_path+"topics.xml")
    # sys.stdout.write(topics_dict)

    sentence_pairs_dict = search_all_topics(hns_index, pickle_, model, topics_dict, 50)

    model = CrossEncoder(pretrained_path+"args-me-crossencoder-v1/", max_length = 504)

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
    sys.stdout.write("Total Lines Output" +len(output_lines))

    output_path = args.o + "run2.txt"

    with open(output_path, 'w') as writefile:
        for line in output_lines:
            writefile.writelines(line+"\n")
    print("Successful Write!")