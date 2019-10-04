# these are SQL alchemy models to talk to the postgres data base
from sqlalchemy import Column, Integer, String, BigInteger, DateTime
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from firebase_admin import credentials, firestore, initialize_app
# from server import db
# set up dummy database
db = SQLAlchemy()
# db = SQLAlchemy(app)


class SuperCollection():
    def __init__(self, collection, pk_col=None):
        self.collection = collection
        self.pk_col = pk_col
    def upsert(self, data):
        if self.pk_col is None:
            doc_ref = self.collection.document()
        else:
            data.pop(self.pk_col)
            pk = data.get(self.pk_col)
            doc_ref = self.collection.document(pk)
        doc = doc_ref.get()
        data['timestamp']=firestore.SERVER_TIMESTAMP
        if doc.exists:
            print('doc exists!!!')
            old_data = doc.to_dict()
            if old_data == data:
                pass
            else:
                doc_ref.update(data)
        else:
            doc_ref.set(data)
        return None
    def write(self, data):
        data['timestamp']=firestore.SERVER_TIMESTAMP
        if self.pk_col is None:
            doc_ref = self.collection.document()
        else:
            data.pop(self.pk_col)
            pk = data.get(self.pk_col)
            doc_ref = self.collection.document(pk)
        doc_ref.set(data)
        return None
    def update(self, data):
        data['timestamp']=firestore.SERVER_TIMESTAMP
        if self.pk_col is None:
            doc_ref = self.collection.document()
        else:
            data.pop(self.pk_col)
            pk = data.get(self.pk_col)
            doc_ref = self.collection.document(pk)
        doc_ref.update(data)
        return None
    def get_by_user(self, user_id):
        data_list = []
        docs = self.collection.where('user_id', '==', user_id,).stream()
        for doc in docs:
            data = doc.to_dict()
            data_list.append(data)
        return data_list
        
class Token(db.Model):
    __tablename__ = 'token'
    # this is the token ID
    id = db.Column(db.BigInteger, primary_key=True)
    #this is the universal unique id for each user
    user_id = Column(db.String, unique=False, nullable=False)
    # item id, represents the "chase, capital one, etc"
    item_id = Column(db.String, unique=False, nullable=False)
    # this is the public token passed in
    public_token = db.Column(db.String(80), unique=False, nullable=False)
    # this is the private access token to look at data through plaid's api
    access_token = db.Column(db.String(80), unique=True, nullable=False)
    
    created_dt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_dt = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    def __init__(self, user_id, item_id, public_token, access_token):
        db.create_all()
        self.user_id = user_id
        self.item_id = item_id
        self.public_token = public_token
        self.access_token = access_token
    def __repr__(self):
        return "public token: {}, access_token: {}".format(self.public_token, self.access_token)
    def upsert(self):
        token = Token.query.filter_by(user_id=self.user_id, item_id=self.item_id).first()
        if token is None:
            print('creating new token for person:{} account:{}'.format(self.user_id, self.item_id))
            db.session.add(self)
            db.session.commit()
        else:
            print('updating token for person:{} account:{}'.format(self.user_id, self.item_id))
            token.public_token = self.public_token
            token.access_token = self.access_token
            db.session.commit()

# class Item():
#     def __init__(self, id, user_id):
#         self.id = id
#         self.user_id = user_id
#         self.ref = firestore_db.collection('items').document(id)
#     def set():
#         fb_item = 
#     fb_item.set({
#         'user_id': user_id,
#         'timestamp': firestore.SERVER_TIMESTAMP
#     })



def main():
    return None
    
    

if __name__ == '__main__':
    main()
    
