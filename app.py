from vectorizer import vect
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import pickle
import sqlite3
import os
import numpy as np

import sqlite3

connection = sqlite3.connect('data.db')

cursor = connection.cursor()

create_table = "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, review text, sentiment int, probability real)"
cursor.execute(create_table)

connection.commit()

connection.close()

# 로컬 디렉토리에서 HashingVectorizer를 임포트합니다

# 로컬 디렉토리에서 업데이트 함수를 임포트합니다
# from update import update_model

# 분류기 준비
cur_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(cur_dir,
                                    'pkl_objects',
                                    'classifier.pkl'), 'rb'))
# db = os.path.join(cur_dir, 'reviews.sqlite')


def classify(document):
    # label = {0: 'negative', 1: 'positive'}
    X = vect.transform([document])
    y = clf.predict(X)[0]
    proba = np.max(clf.predict_proba(X))
    return y, proba


def train(document, y):
    X = vect.transform([document])
    clf.partial_fit(X, [y])


# def sqlite_entry(path, document, y):
#     conn = sqlite3.connect(path)
#     c = conn.cursor()
#     c.execute("INSERT INTO review_db (review, sentiment, probability)"
#               " VALUES (?, ?, DATETIME('now'))", (document, y))
#     conn.commit()
#     conn.close()


app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/item/*": {"origins": "*"}})


class Item(Resource):
    TABLE_NAME = 'items'

    def get(self, name):
        item = self.find_by_name(name)
        if item:
            return item
        return {'message': 'Item not found'}, 404

    def find_by_name(self, name):

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM {table} WHERE name=?".format(
            table=self.TABLE_NAME)
        result = cursor.execute(query, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            return {'item': {'id': row[0], 'review': row[1], 'sentiment': row[2], 'probability': row[3]}}

    def post(self, name):

        data = request.get_json()
        classify_result = classify(data['review'])

        item = {
            'name': data['review'], 'sentiment': int(classify_result[0]), 'probability': float(round(classify_result[1]*100, 2))}
        # print(item)
        try:
            self.insert(item)
        except:
            return {"message": "An error occurred inserting the item."}

        item['sentiment'] = str(item['sentiment'])
        item['probability'] = str(item['probability'])
        return jsonify(item)

    def insert(self, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "INSERT INTO {table} VALUES(null, ?, ?, ?)".format(
            table=self.TABLE_NAME)
        cursor.execute(
            query, (item['name'], item['sentiment'], item['probability']))

        connection.commit()
        connection.close()


class ItemList(Resource):
    TABLE_NAME = 'items'

    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        query = "SELECT * FROM {table}".format(table=self.TABLE_NAME)
        result = cursor.execute(query)
        items = []
        for row in result:
            items.append({'id': str(row[0]), 'review': str(row[1]),
                          'sentiment': str(row[2]), 'probability': str(row[3])})
        connection.close()

        return jsonify({'items': items})


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

if __name__ == '__main__':
    app.run(debug=True)  # important to mention debug=True
