from firebase_admin import credentials, initialize_app, firestore
from flask import *
from cors import *
import uuid
import json

app = Flask(__name__, template_folder="", static_folder="")
cred = credentials.Certificate('rookiecourses-350922-53455e3bbfe3.json')
initialize_app(cred)
db = firestore.client()

def get_data(doc_name):
  for doc in db.collection("rookiecourses").stream():
    if doc.id == doc_name:
      return doc.to_dict()

def set_data(doc_name, data):
  doc_ref = db.collection("rookiecourses").document(doc_name)
  doc_ref.update(data)

@crossdomain(origin="*")
@app.route("/get_courses", methods=["GET", "POST"])
def get_courses():
  findata = []
  for k, v in get_data("courses").items():
    findata.append(v)
  return jsonify(findata)

@crossdomain(origin="*")
@app.route("/get_courses_by_likes", methods=["GET", "POST"])
def get_courses_by_likes():
  findata = []
  for k, v in {k: v for k, v in sorted(get_data("courses").items(), key=lambda item: item[1]["likes"])}.items():
    findata.append(v)
  return jsonify(reversed(findata))

@crossdomain(origin="*")
@app.route("/post_course", methods=["GET", "POST"])
def post_course():
  info = request.json
  info["id"] = str(uuid.uuid4())
  info["likes"] = 0
  set_data("courses", {info["id"]: info})
  return ""

@crossdomain(origin="*")
@app.route("/get_one_course", methods=["GET", "POST"])
def get_one_course():
  print(request.json)
  info = request.json
  for k, v in get_data("courses").items():
    if k == info["course_id"]:
      return v["videos"][get_data("users")[info["wallet_address"]][str(info["course_id"])]]

@crossdomain(origin="*")
@app.route("/continue_user", methods=["GET", "POST"])
def continue_user():
  info = request.json
  prevdata = get_data("users")[info["wallet_address"]]
  if info["forward"]:
    prevdata[str(info["course_id"])] += 1
  else:
    prevdata[str(info["course_id"])] -= 1
  set_data("users", {info["wallet_address"]: prevdata})
  return ""

@crossdomain(origin="*")
@app.route("/set_user", methods=["GET", "POST"])
def set_user():
  info = request.json
  if info["wallet_address"] not in list(get_data("users").keys()):
    set_data("users", {info["wallet_address"]: {}})
  prevdata = get_data("users")[info["wallet_address"]]
  prevdata[str(info["course_id"])] = 0
  set_data("users", {info["wallet_address"]: prevdata})
  return ""

@crossdomain(origin="*")
@app.route("/add_likes", methods=["GET", "POST"])
def add_likes():
  info = request.json
  prevdata = get_data("courses")[info["course_id"]]
  prevdata["likes"] += 1
  set_data("courses", {info["course_id"]: prevdata})
  return ""

app.run(host="0.0.0.0")
