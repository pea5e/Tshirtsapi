from flask import Flask, request, jsonify, send_file
from flask import render_template
import models
import json
from flask_cors import CORS
from datetime import datetime, timedelta

app = Flask(__name__)

# CORS(app, resources={r"*": {"origins": "*printsplash.repl.co*"}})
CORS(app, resources={r"*": {"origins": "*"}})
# jsonify(message="Simple server is running").headers.add("Access-Control-Allow-Origin", "*")


@app.route('/', methods=['GET', 'POST', 'DELETE'])
def index():
  return "Welcome in Printsplash API"


@app.route('/<path:path>png', methods=['GET', 'POST', 'DELETE'])
def image(path):
  return send_file(path + "png", mimetype='image/png')


@app.route('/signup', methods=['GET', 'POST', 'DELETE'])
def signup():
  data = request.json
  # if models.is_secured(data["secret_key"]):
  new_designer = models.designer(data["email"].lower(), data["nom"],
                                 data["password"])
  new_designer.save()
  print("logged")
  return jsonify({
    "response": "200",
    "security_key": models.get_security_key()
  })
  # return jsonify({"response":"423","message":"Locked"})


@app.route('/usedmail', methods=['GET', 'POST', 'DELETE'])
def usedmail():
  data = request.json
  if models.designer.get_designer(data["email"]) is None:
    print("notfound")
    return jsonify({"response": "200"})
  return jsonify({"response": "302 ", "message": "Used"})


@app.route('/login', methods=['GET', 'POST', 'DELETE'])
def login():
  data = request.json
  designer = models.designer.get_designer(data["email"])
  if models.decode_pass(designer.password) == data["password"]:
    return jsonify({
      "response": "200",
      "email": designer.email,
      "nom": designer.nom,
      "security_key": models.get_security_key()
    })
  return jsonify({"response": "401", "message": "Wrong Password"})


@app.route('/sendmessage', methods=['GET', 'POST', 'DELETE'])
def sendmessages():
  data = request.json
  date = str(datetime.now())[:19]
  mes = models.message(data["email"], data["message"], date)
  mes.save()
  return jsonify({"response": "200"})


@app.route('/getmessages', methods=['GET', 'POST', 'DELETE'])
def getmessages():
  mes = models.message.get_messages()
  return jsonify({"response": "200", "messages": mes})


@app.route('/get_designers', methods=['GET', 'POST', 'DELETE'])
def get_designers():
  designers = models.designer.get_alldesigners()
  # for i,des in enumerate(designers) :
  #   designers[i] = (des[0],des[1],models.decode_pass(des[2]))

  return jsonify({"response": "200", "designers": designers})


@app.route('/add', methods=['GET', 'POST', 'DELETE'])
def addtshirt():
  data = request.json
  if models.is_secured(data["secret_key"]):
    models.tshirt(data["prix"], data["email"]).save()
    x = models.savetshirt(data)
    print(x)
    return jsonify(x)
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/getprice', methods=['GET', 'POST', 'DELETE'])
def getprice():
  data = request.json
  if models.is_secured(data["secret_key"]):
    price = models.tshirt.get_tshirt(data["tshirt_id"])
    if price:
      return jsonify({"response": "200", "prix": price})
    return jsonify({"response": "404", "message": "Unfound"})
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/getmyshirts', methods=['GET', 'POST', 'DELETE'])
def getmyshirts():
  data = request.json
  if models.is_secured(data["secret_key"]):
    tshirts = models.tshirt.get_tshirts_of_designer(
      models.designer.get_id(data["email"]))
    if tshirts:
      return jsonify({"response": "200", "tshirts": tshirts})
    return jsonify({"response": "404", "message": "Unfound"})
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/getshirt', methods=['GET', 'POST', 'DELETE'])
def getshirt():
  data = request.json
  tshirt = models.tshirt.get_tshirt(data["id"])
  if tshirt:
    return jsonify({"response": "200", "price": tshirt[0]})
  return jsonify({"response": "404", "message": "Unfound"})


@app.route('/getshirts', methods=['GET', 'POST', 'DELETE'])
def getshirts():
  tshirts = models.tshirt.get_tshirts()
  if tshirts:
    return jsonify({"response": "200", "tshirts": tshirts})
  return jsonify({"response": "404", "message": "Unfound"})


@app.route('/update', methods=['GET', 'POST', 'DELETE'])
def update_shirt():
  data = request.json
  if models.is_secured(data["secret_key"]):
    models.tshirt.update_tshirt(data["tshirt_id"], data["prix"])
    return jsonify({"response": "200"})
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/delete', methods=['GET', 'POST', 'DELETE'])
def delete_shirt():
  data = request.json
  if models.is_secured(data["secret_key"]):
    models.tshirt.delete_tshirt(data["tshirt_id"])
    return jsonify({"response": "200"})
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/pay', methods=['GET', 'POST', 'DELETE'])
def pay():
  data = request.json
  date = str(datetime.now())[:19]
  commande = models.Commande(data["lieu"], date, data["nom"], data["carte"],
                             list(zip(data["products"], data["qte"])))
  commande.save()
  return jsonify({"response": "200"})


@app.route('/getmysales', methods=['GET', 'POST', 'DELETE'])
def getmysales():
  data = request.json
  if models.is_secured(data["secret_key"]):
    sales = models.Commande.get_mysales(models.designer.get_id(data["email"]))
    if sales:
      return jsonify({"response": "200", "sales": sales})
    return jsonify({"response": "404", "message": "Unfound"})
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/getmyprofit', methods=['GET', 'POST', 'DELETE'])
def getmyprofit():
  data = request.json
  if models.is_secured(data["secret_key"]):
    profit = models.designer.get_myprofit(models.designer.get_id(
      data["email"]))
    if profit:
      return jsonify({
        "response": "200",
        "profit": profit[0],
        "our-gain": profit[1] * 60
      })
    return jsonify({"response": "404", "message": "Unfound"})
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/getmystats', methods=['GET', 'POST', 'DELETE'])
def getmystats():
  data = request.json
  if models.is_secured(data["secret_key"]):
    unite = list()
    profit = list()
    today = datetime.now() + timedelta(hours=1)
    for day in range(5):
      stats = models.designer.get_mydaystats(
        str(today - timedelta(days=4 - day))[:10],
        models.designer.get_id(data["email"]))
      unite.append(stats[0])
      profit.append(stats[1])
    return jsonify({"response": "200", "unites": unite, "profit": profit})

  return jsonify({"response": "423", "message": "Locked"})


@app.route('/getmybests', methods=['GET', 'POST', 'DELETE'])
def getmybests():
  data = request.json
  if models.is_secured(data["secret_key"]):
    sales = models.designer.get_mybest(models.designer.get_id(data["email"]))
    if sales:
      return jsonify({"response": "200", "bests": sales})
    return jsonify({"response": "404", "message": "Unfound"})
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/getprofit', methods=['GET', 'POST', 'DELETE'])
def getprofit():
  profit = models.Commande.get_profit()
  if profit:
    return jsonify({
      "response": "200",
      "profit": profit[0],
      "our-gain": profit[1] * 60
    })
  return jsonify({"response": "404", "message": "Unfound"})
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/getstats', methods=['GET', 'POST', 'DELETE'])
def getstats():
  unite = list()
  profit = list()
  today = datetime.now() + timedelta(hours=1)
  for day in range(5):
    stats = models.Commande.get_daystats(
      str(today - timedelta(days=4 - day))[:10])
    unite.append(stats[0])
    profit.append(stats[1])
  return jsonify({"response": "200", "unites": unite, "profit": profit})

  return jsonify({"response": "423", "message": "Locked"})


@app.route('/getbests', methods=['GET', 'POST', 'DELETE'])
def getbests():
  sales = models.Commande.get_best()
  if sales:
    return jsonify({"response": "200", "bests": sales})
  return jsonify({"response": "404", "message": "Unfound"})


@app.route('/admin', methods=['GET', 'POST', 'DELETE'])
def admin():
  data = request.json
  if models.AdminLog.is_admin(data["secret_key"]):
    date = str(datetime.now())[:19]
    models.AdminLog(request.remote_addr, request.user_agent.string,
                    date).save()
    return jsonify({"response": "200"})
  return jsonify({"response": "423", "message": "Locked"})


@app.route('/adminlogs', methods=['GET', 'POST', 'DELETE'])
def adminlogs():
  return jsonify({"response": "200", "admins": models.AdminLog.get_admins()})


@app.route('/getcommitems', methods=['GET', 'POST', 'DELETE'])
def getcommitems():
  data = request.json
  sales = models.Commande.get_commsales(data["cid"])
  return jsonify({"response": "200", "sales": sales})


@app.route('/getcommandes', methods=['GET', 'POST', 'DELETE'])
def getcommandes():
  sales = models.Commande.get_commands()
  if sales:
    return jsonify({"response": "200", "commandes": sales})
  return jsonify({"response": "404", "message": "Unfound"})


@app.route('/decode', methods=['GET', 'POST', 'DELETE'])
def getdecode():
  password = models.encode_pass(request.form.get("password"))
  return jsonify({"response": password})


@app.route('/encode', methods=['GET', 'POST', 'DELETE'])
def getencode():
  password = models.decode_pass(request.form.get("password"))
  return jsonify({"response": password})


@app.route('/test', methods=['GET', 'POST', 'DELETE'])
def test():
  # data = request.json
  # return jsonify({"designers":models.tshirt.get_tshirts_of_designer(models.designer.get_id(data["email"]))})
  # models.tshirt.delete_all()
  # return jsonify({"tshirts":models.tshirt.get_tshirts()})
  # return models.test()
  return jsonify(
    dir(request) + [request.remote_addr, request.user_agent.string])
  # return jsonify({"test":models.test()})
  # return models.get_security_key()
  # unite = list()
  # profit = list()
  # for day in range(5):
  #   stats = models.designer.get_mydaystats(str(datetime.now() - timedelta(days=4-day))[:10],9)
  #   unite.append(stats[0])
  #   profit.append(stats[1])

  # return jsonify({"response":"200","unites":unite,"profit":profit})


app.run(host='0.0.0.0', port=81)
