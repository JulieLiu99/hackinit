from flask import Flask, render_template, request, redirect, url_for
import requests
import json
import uuid
import os
import time
from img_proc import make_thumbnail, add_watermark

URL_FROM_NODE = "http://40.73.99.82:60000"

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        f = request.files['up-img']
        basepath = os.path.dirname(__file__)
        img_uuid = str(uuid.uuid4())
        mini_path = img_uuid + ('.png' if f.mimetype == 'image/png' else '.jpg')
        upload_path = os.path.join(basepath, 'static/upload', mini_path)
        f.save(upload_path)
        thumbnail_path = make_thumbnail(mini_path)
        watermark_path = add_watermark(thumbnail_path)
        img_url = "static/upload/" + watermark_path
        # mine
        data_to_mine = {
            "type": "pic",
            "uploaded_by": username,
            "uuid": img_uuid,
            "url": img_url,
            "timestamp": time.time()
        }
        r = requests.post(URL_FROM_NODE + '/new_transaction', json=data_to_mine, headers={"content-type": "application/json"})
        if r.status_code == 201:
            r = requests.get(URL_FROM_NODE + '/mine')
        return render_template('upload.html', hash=r.text.strip())


@app.route("/gallery")
def display_img():
    r = requests.get(URL_FROM_NODE + "/chain")
    chains = json.loads(r.text)["chain"]
    transactions = []
    for item in chains[1:]:
        transactions.append(item["transactions"])
    return render_template("gallery.html", trans=transactions)


@app.route("/purchase")
def purchase():
    pass


@app.route("/hashlookup", methods=["GET","POST"])
def hash_lookup():
    if request.method == "GET":
        return render_template("hashlookup.html")
    elif request.method == "POST":
        hash_to_lookup = request.form.get("search-box")
        r = requests.post(URL_FROM_NODE + "/hash_lookup", data=hash_to_lookup)
        hash_json = json.loads(r.text)
        hash_json["hash"] = hash_to_lookup
        return render_template("hashlookup.html", s=hash_json)
