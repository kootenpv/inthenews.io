import cloudant


with open('cloudant.login') as f:
    USERNAME, PASSWORD = f.read().split('\n')


def get_cloudant_database(topic, source, doc_type):
    account = cloudant.Account(USERNAME)
    account.login(USERNAME, PASSWORD)
    db = account.database('{}_{}_{}'.format(topic, source, doc_type))
    # create db if non existant
    db.put()
    return db


def add_date_view(db):
    date_view_design = {
        "views": {
            "viewdate": {"map": "function(doc){emit(doc.date)}"}
        }
    }
    if db['_design/dateview'].head().status_code != 200:
        db['_design/dateview'] = date_view_design
