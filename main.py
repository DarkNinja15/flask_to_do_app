from flask import Flask
from flask_restful import Resource, Api, reqparse
from pymongo import MongoClient
from mongoengine import Document, StringField, connect
import configparser

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('config.ini')
username = config['MongoDB']['username']
password = config['MongoDB']['password']
app.config['MONGO_URI'] = f'mongodb+srv://{username}:{password}@cluster0.nsmty9r.mongodb.net/'
mongo = MongoClient(app.config['MONGO_URI'])
db = mongo["todo_flask_backend"]
connect(db="todo_flask_backend", host=f"mongodb+srv://{username}:{password}@cluster0.nsmty9r.mongodb.net/")
api = Api(app)


class TodoModel(Document):
    todo_id = StringField(required=True)
    task = StringField(required=True)
    summary = StringField(required=True)


todos = {}

todo_post_args = reqparse.RequestParser()
todo_post_args.add_argument("task", required=True, type=str, help="Task is required")
todo_post_args.add_argument("summary", required=True, type=str, help="Summary is required")


class ToDo(Resource):
    def get(self, todo_id):
        fetchDocs()
        if todos.__contains__(todo_id):
            return todos[todo_id]
        return {"data": "The requested todo id does not exist"}

    def post(self, todo_id):
        fetchDocs()
        args = todo_post_args.parse_args()
        if todos.__contains__(todo_id):
            return {"data": "Task id already taken."}
        db.newCollection.insert_one({
            "todo_id": todo_id,
            "task": args["task"],
            "summary": args["summary"]
        })
        return {"data": "Task Added Successfully"}

    def put(self, todo_id):
        fetchDocs()
        args = todo_post_args.parse_args()
        filter = {"todo_id": todo_id}

        if todos.__contains__(todo_id):
            if args["task"]:
                updateTask = {"$set": {"task": args["task"]}}
                db.newCollection.update_one(filter, updateTask)
            if args["summary"]:
                updateSummary = {"$set": {"task": args["summary"]}}
                db.newCollection.update_one(filter, updateSummary)
            return {"data": "Todo updated successfully"}
        return {"data": "The requested to do id does not exist"}

    def delete(self, todo_id):
        fetchDocs()
        if todos.__contains__(todo_id):
            deleteFilter = {"todo_id": todo_id}
            db.newCollection.delete_one(deleteFilter)
            return {"data": "Todo deleted successfully"}
        return {"data": "The requested to do id does not exist"}


class TodoList(Resource):
    def get(self):
        fetchDocs()
        return todos


api.add_resource(ToDo, '/todos/<string:todo_id>')
api.add_resource(TodoList, '/todos')


def fetchDocs():
    documents = db.newCollection.find()
    for document in documents:
        todoModel = TodoModel(todo_id=document["todo_id"], task=document["task"], summary=document["summary"])
        todos[todoModel.todo_id] = {
            "task": todoModel.task,
            "summary": todoModel.summary
        }


@app.route("/")
def home_page():
    return {"data": "success"}


if __name__ == '__main__':
    app.run(debug=True)
