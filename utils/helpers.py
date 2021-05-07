import pickle
import xmltodict

def read_xml(path):
    with open(path) as f:
        lines = f.read()
    topics = xmltodict.parse(lines)
    topic_dict = {}
    for topic in topics['topics']['topic']:
        topic_dict.update({topic['number']: topic['title']})
    return topic_dict

def load_pickle(pickle_path):
    print("Loading Pickle")
    with open(pickle_path, 'rb') as handle:
        b = pickle.load(handle)
    return b

