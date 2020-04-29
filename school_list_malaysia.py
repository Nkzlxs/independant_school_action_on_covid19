import requests
import json
from flask import Flask, request, render_template, url_for
from flask.logging import create_logger


import postToTelegram_module

# import time

app = Flask(__name__)
log = create_logger(app)

request_type = ("sendMessage", "sendPoll", "sendDice",
                    "sendContact", "sendVenue", "getUpdates")
REQUEST_METHOD_NAME = request_type[0]
BOT_TOKEN = "YOUR_TELEGRAM_TOKEN"+"/"
THE_URL = "https://api.telegram.org/bot"

def loadJsonData():
    readfile = open('data.json', 'r')
    # global all_posts
    all_posts = json.load(readfile)
    readfile.close()
    return all_posts


def writeJsonData(input_object):
    outfile = open('data.json', 'w')
    json.dump(input_object, outfile)
    outfile.close()


def formatToUrl(returnText, the_url):
    return f"<a href=\"{the_url}\">{returnText}</a>"


def postToTelegram():
    # with open('data.json', 'r') as readfile:
    #     all_posts = json.load(readfile)
    # readfile.close()
    all_posts = loadJsonData()

    

    full_text = ""
    for thing in all_posts['area']:
        full_text += f"<b><u>{thing['name']}</u></b>\n"
        for a_post in thing['post_list']:
            a_text = f"{a_post['school_name']} -"
            for a_post_link in a_post['post_link']:
                a_text += f"{formatToUrl(a_post_link['type'],a_post_link['link'])}"
                a_text += " "
            a_text += "\n"
            full_text += a_text
        full_text += "\n"
    PARAMETER = {
        # "chat_id": -1001293231152,
        "chat_id": "@nkzlxs",
        "parse_mode": "HTML",
        "text": full_text
    }
    the_header = {"CONTENT-TYPE": "APPLICATION/JSON"}
    request_json = requests.post(
        url=THE_URL+BOT_TOKEN+REQUEST_METHOD_NAME, json=PARAMETER, headers=the_header)
    return request_json


def appendToAllPost(title, input_object):
    all_posts = loadJsonData()

    for object in all_posts['area']:
        if(object['name'] == title):
            if len(object['post_list']) > 0:
                log.debug("PostList is greater than 0")
                for a_object in object['post_list']:
                    if a_object['school_name'] == input_object["school_name"]:
                        for url in input_object['post_link']:
                            a_object['post_link'].append(url)
                    else:
                        object['post_list'].append(input_object)
                        break
            else:
                object['post_list'].append(input_object)

    # with open('data.json', 'w') as outfile:
    #     json.dump(all_posts, outfile)
    # outfile.close()
    writeJsonData(all_posts)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.jinja2")
    if request.method == "POST":
        post_link_list = []
        for x in range(0, 5):
            name = f"the_url{x}"
            a_link = request.form.get(name)

            log.debug(f"What link i get is {a_link}")
            if not a_link == "":
                if x == 0:
                    type = "补课安排"
                elif x == 1:
                    type = "网上教学安排"
                elif x == 2:
                    type = "考试安排"
                elif x == 3:
                    type = "上课后的作业程序SOP"
                elif x == 4:
                    type = "校方内部工作安排"
                data_link = {
                    "type": type,
                    "link": a_link
                }
                post_link_list.append(data_link)
        data = {
            "school_name": request.form.get("school_name"),
            "post_link": post_link_list
        }
        section = request.form.get("area")

        appendToAllPost(section, data)

        return render_template("index.jinja2")


@app.route("/postToTelegram", methods=["GET", "POST"])
def postToTelegramPage():
    try:
        return_json = postToTelegram()
        log.debug(return_json.json())
        return render_template("postToTelegram.jinja2", result="Post Successful")
    except:
        return render_template("postToTelegram.jinja2", result="Post Failed")
