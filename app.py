#PEM PASS PHRASE HELLOW WORLD
from subprocess import run, PIPE
import marvin
from flask import Flask, render_template, request, send_from_directory, send_file, redirect, session
import os
from flask_session import Session
from openai import OpenAI
from utils import text_to_wav, saveAllAudio
import time


from flask import Flask




MAXLENGTH = 2

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



client = OpenAI()

with open("prompt.txt", "r") as file:
    system_msg = file.read()
    file.close()



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # record the user name
        session["name"] = request.form.get("name")
        session["turn"] = 0
        session["messages"] = [{"role": "system", "content": system_msg}]

        # redirect to the main page
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


@app.route('/')
def index():
    if not session.get("name"):
        # if not there in the session then redirect to the login page
        return redirect("/login")
    return render_template('index.html',username = session.get("name"))


@app.route('/audio', methods=['POST'])
def audio():
    if not os.path.exists(f"./recordings/{session["name"]}"):
        os.makedirs(f"./recordings/{session["name"]}")
    newPath = f'./recordings/{session["name"]}/User-{session["turn"]}.wav'

    with open(newPath, 'wb') as f:
        f.write(request.data)

    transcribedText = marvin.transcribe(newPath)

    reply = client.chat.completions.create(model="gpt-3.5-turbo",
                                                messages=session["messages"]).choices[0].message.content
    session["messages"].append({"role": "assistant", "content": reply})

    
    text_to_wav("es-ES-Standard-A",reply, f'./recordings/{session["name"]}/AI-{session["turn"]}.wav')




    session["turn"] +=1

    return({"transcribe":f"transcribed: {transcribedText}\nreturn: {reply}", "audioPath":f"audioAPI/{session["name"]}-{session["turn"]}"})
    
@app.route("/wavTry2")
def wavTry2():
    return render_template("wav.html", audioPath = "PinkPanther30.wav")

@app.route("/audioAPI/<path:filename>")
def audioAPI(filename):
    #not using filename?
    return send_from_directory(f'./recordings/{session["name"]}', f"AI-{session["turn"]-1}.wav")

@app.route("/downloadSession")
def downloadSession():
    time.sleep(10)
    saveAllAudio(f"./recordings/{session["name"]}",MAXLENGTH=MAXLENGTH)
    path = f"./recordings/{session["name"]}/finalAudio.wav"
    return send_file(path, as_attachment=True)


'''if __name__ == "__main__":
    #app.logger = logging.getLogger('audio-gui')
    app.run(debug=True, ssl_context=("./SSLInfo/cert.pem","./SSLInfo/key.pem"))
    #app.run(port = 4200, debug=True)'''
