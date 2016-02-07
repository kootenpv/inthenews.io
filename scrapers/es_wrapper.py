import elasticsearch
from elasticsearch import helpers

es = elasticsearch.Elasticsearch([{'host': 'localhost', 'port': 9200}])


def get_documents(server, index, doc_type, size=20, sort=("date", "desc")):
    query = {"query": {"match_all": {}}, "size": size, "sort": {sort[0]: sort[1]}}
    res = server.search(body=query, doc_type=doc_type, index=index)
    return [doc['_source'] for doc in res['hits']['hits']]


def get_results(server, q, doc_type, index):
    res = server.search(body=q, doc_type=doc_type, index=index)
    docs = []
    for doc in res['hits']['hits']:
        d = doc['fields']
        d = {x: d[x][0] for x in d}
        d['_type'] = doc['_type']
        docs.append(d)
    return docs


def search(server, index, query, size=20, doc_type='', sort=None):
    q = {"size": size,
         "fields": ["url", "name", "likes", "date", "description", "title"]
         }
    q["query"] = {"query_string": {"query": query}} if query else {"match_all": {}}
    if sort is not None:
        q['sort'] = {sort: "desc"}
    res = get_results(server, q, doc_type, index)
    if not res:
        q['query'] = {"fuzzy": {"name": query}}
        res = get_results(server, q, doc_type, index)
    if not res:
        q['query'] = {"fuzzy": {"description": query}}
        res = get_results(server, q, doc_type, index)
    return res


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
