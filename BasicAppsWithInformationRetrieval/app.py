import identity
import identity.web
import requests
from flask import Flask, redirect, render_template, request, session, url_for,jsonify
from flask_session import Session

import config
import aiapi
# import config.DevelopmentConfig

app = Flask(__name__)
app.config.from_object(config.DevelopmentConfig)
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config.get("AUTHORITY"),
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)


@app.route("/login")
def login():
    return render_template("login.html", version=identity.__version__, **auth.log_in(
        scopes=config.DevelopmentConfig.SCOPE, # Have user consent to scopes during log-in
        redirect_uri=url_for("auth_response", _external=True), # Optional. If present, this absolute URL must match your app's redirect_uri registered in Azure Portal
        ), config_class = config)


@app.route(config.DevelopmentConfig.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route("/")
def index():
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        # This check is not strictly necessary.
        # You can remove this check from your production code.
        return render_template('config_error.html')
    if not auth.get_user():
        return redirect(url_for("login"))
        #return render_template('login.html', )
    return render_template('index.html', user=auth.get_user(), version=identity.__version__)


@app.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(config.DevelopmentConfig.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        config.DevelopmentConfig.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('display.html', result=api_result)

@app.route('/gpt_answer', methods = ['POST', 'GET'])
def gpt_response():
    print('GPTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
    if request.method == 'POST':
      #prompt = request.form['prompt'] # check val name inside index.html jquery description ajax
      print(request.form)
      prompt = request.form.get('prompt')# check val name inside index.html jquery description ajax
      email = request.form.get('useremail')# check val name inside index.html jquery description ajax

      print(prompt)
      print(email)  
      print('|'*30)
      print('|'*30)
      
      res = {}
      #res['answer'] = aiapi.generateChatResponse(prompt)
      #res['answer'] = aiapi.generateChatResponseGivenHistory(prompt)
      res['answer'] = aiapi.generateChatResponseGivenHistoryCosmosDB(prompt,email)
      return jsonify(res), 200 # 200 is a success status code

    return render_template('index.html', **locals())

@app.route('/gpt_answer_PDF', methods = ['POST', 'GET'])
def gpt_pdf_response():
    print('GPTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
    if request.method == 'POST':
      #prompt = request.form['prompt'] # check val name inside index.html jquery description ajax
      print(request.form)
      prompt = request.form.get('prompt')# check val name inside index.html jquery description ajax
      email = request.form.get('useremail')# check val name inside index.html jquery description ajax

      print(prompt)
      print(email)  
      print('|'*30)
      print('|'*30)
      
      res = {}

      res['answer'] = aiapi.generateChatResponseQnACosmosDB(prompt,email)
      return jsonify(res), 200 # 200 is a success status code

    return render_template('index.html', **locals())


if __name__ == "__main__":
    app.run()
