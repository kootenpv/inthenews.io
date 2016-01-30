import elasticsearch
from elasticsearch import helpers

es = elasticsearch.Elasticsearch([{'host': 'localhost', 'port': 9200}])


def get_all_documents(server, index, doc_type):
    query = {"query": {"match_all": {}}}
    res = server.search(body=query, doc_type=doc_type, index=index)
    return [doc['_source'] for doc in res['hits']['hits']]


def prep_doc(doc, index, doc_type):
    new_doc = {'_index': index,
               '_type': doc_type,
               '_id': doc.pop('_id'),
               '_op_type': 'update'}
    if 'likes' in doc:
        like = doc.pop('likes')
        script = "ctx._source.likes = (ctx._source.likes) ? ctx._source.likes + like : [like]"
        new_doc["script"] = script
        new_doc['upsert'] = doc
        new_doc['upsert']['likes'] = [like]
        new_doc['params'] = {"like": like}
    else:
        new_doc['_source'] = doc
    return new_doc


def save_bulk(server, index, doc_type, docs):
    doc_generator = (prep_doc(x, index, doc_type) for x in docs)
    return helpers.bulk(server, doc_generator)
