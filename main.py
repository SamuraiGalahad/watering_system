import time
import csv
from flask import Response, request, render_template, Flask, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime
import json


""""
Ниже происходит инициализация самого сайта и базы данных.
"""
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///info.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

""""
Класс базы данных. По обращению к объекту очень
похож на JSON.
"""


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    temp = db.Column(db.String(100), nullable=False)
    vlag = db.Column(db.String(100), nullable=False)
    UrV = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return "<template %r>" % self.id


""""
Быстрые данные per session.
"""

allInfo_to = []
allInfo_from = dict()
string = "0 0 0 0"

""""
Главная страница сайта. Можно обращаться: (/home,/)
"""


@app.route("/")
@app.route("/home")
def hello():
    return render_template("base.html")


""""
Закрытый статус страницы. Выводит его статус обновления, который пока-что 
меняется вручную. Также необновляемое время на серввере во время запроса. Если быть точным, то по time
показывается время получения обратного запроса, проще - время страницы.
"""


@app.route("/status")
def status():
    return {
        "status": True,
        "name": "SamuraiGalahads serv",
        "time": time.asctime()
    }


""""
Резервный метод передачи данных с помощью JSON. Записываются в csv файл. Не имеет пути.
"""


@app.route("/imposter", methods=["POST"])
def send():
    data = request.json
    if isinstance(data, dict) is False:
        return Response("error", "Not JSON")

    sensor_type = data.get("sensorType")
    values = data.get("values")
    timestamps = data.get("timestamps")
    global allInfo_to

    if isinstance(sensor_type, str):
        allInfo_to.append({"sensor_type": sensor_type,
                           "time_on_serv": time.asctime(),
                           "values": values,
                           "timestamps": timestamps})
        formal_data = [["Sensor_Type", "Values", "Time"],
                       [sensor_type, values, timestamps]]

        with open("test.csv", "a") as writer_to_file:
            writer = csv.writer(writer_to_file)
            writer.writerows(formal_data)

        return Response("ok")
    else:
        return Response("ok", 400)


""""
Метод передачи данных. Передается bin.string, и потом расшифровывается. Сообщения имеют формат:
T V UrV TDOP TAFP PER. Температура(крадусы по цельсию), влажность (проценты), уровень воды (проценты), 
время до полива (минуты), время после полива (минуты), период (минуты).
"""


@app.route("/post", methods=["POST"])
def post_text():
    def control_s(stat):
        if stat == "0":
            return "NO_WATER"
        elif stat == "1":
            return "NO_COMMAND"
        elif stat == "2":
            return "WATERING_IS_NOT_NECESSARY"
        elif stat == "3":
            return "WILL_BE_WATERING"
        elif stat == "4":
            return "WAS_WATERING"
    data = request.data
    numbers_in_string = data.decode("ascii")
    listok = numbers_in_string.split()
    stats = listok[0]
    temperature = listok[1]
    vlag = listok[2]
    UrV = listok[3]
    current_time = time.asctime()
    allInfo_from[current_time] = listok
    article = Article(title="ДАННЫЕ С ДАТЧИКОВ", status=control_s(stats),  temp=temperature,
                      vlag=vlag, UrV=UrV, date=datetime.datetime.utcnow())

    with open("test.csv", "a") as writer_to_file:
        writer = csv.writer(writer_to_file)
        writer.writerow([numbers_in_string])

    try:
        db.session.add(article)
        db.session.commit()
        return "OK"

    except:
        return "Произошла ошибка"


@app.route("/reserv")
def reserv():
    return


@app.route("/all_messages")
def get_imposter():
    article = Article.query.order_by(Article.date.desc()).all()
    return render_template("all_messages.html", article=article)


@app.route("/create-article", methods=["POST", "GET"])
def get_string():
    global string
    if request.method == "POST":
        auto = request.form["AUTO"]
        string1 = request.form["string1"]
        string2 = request.form["string2"]
        string3 = request.form["string1"]
        dop = request.fop["dop"]
        return redirect("/")
    else:
        return render_template("add_new.html")


@app.route("/get_data", methods=["GET"])
def get_data():
    global string
    if string != "0 0 0 0":
        last_string = string
        string = "0 0 0 0"
        return last_string
    elif string == "0 0 0 0":
        return string


if __name__ == "__main__":
    app.run(port=4000)