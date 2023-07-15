from flask import Flask, render_template,session, request,redirect, jsonify
from flask_babel import Babel 
from moviepy.editor import *
import openai
import os

app = Flask(__name__)


app.config['BABEL_DEFAULT_LOCALE'] = 'en'


def get_locale():
    return 'en'

babel = Babel(app)
babel.init_app(app, locale_selector=get_locale)



app.secret_key = 'mysecretkey'

def split_file(file_path, chunk_size=2*1024*1024):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk

@app.route('/')
def home():
    return redirect('/index')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        key = request.form['key']
        openai.api_key = key
        try:
            openai.Completion.create(
              engine="text-davinci-003",
              prompt="This is a test.",
              max_tokens=5
            )
            session['key'] = key
            return render_template('index.html')
        except Exception as e:
            return render_template('index.html', error=e)    
    return render_template('index.html')

@app.route('/delete_key',methods=['GET', 'POST'])
def delete_key():
    try:
        session.pop('key', None)
    except Exception:
        pass
    return redirect('/index')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if request.method == 'POST':
        file = request.files['audioFile']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        print("file_path: " + file_path)
        print("type: " + str(type(file_path)))
        file.save(file_path)


        

        if file.filename.split(".")[1] == "mp4":
            ##  extract audio (mp3) from video (mp4)
            video = VideoFileClip(file_path)
            new_file_path = file_path.split(".")[0] + ".mp3"
            audio = video.audio
            audio.write_audiofile(new_file_path)
            if new_file_path:
                file_path = new_file_path

        
        key = session['key']

        try:
            openai.api_key = key
            openai.Completion.create(
              engine="text-davinci-003",
              prompt="This is a test.",
              max_tokens=5
            )

        except Exception as e:
            return jsonify(error="Invalid API Key") 
        
        tt = ""
        if file:
            audio_file = open(file_path, 'rb')

            transcription = openai.Audio.transcribe("whisper-1", audio_file)
            transcription = transcription.text 

            chunk_name = file_path.split("/")[1].split(".")[0]
            print("chunk_name: " + chunk_name)

            directory = "audio/"+chunk_name

            if not os.path.exists(directory):
                os.makedirs(directory)

            # for i, chunk in enumerate(split_file(file_path)):
            #     path_to_chunk = f'audio/{chunk_name}/output_{i}.mp3'
            #     with open(path_to_chunk, 'wb') as f:
            #         f.write(chunk)
            #     filee = open(path_to_chunk,'rb')
            #     transcription = openai.Audio.transcribe("whisper-1", filee)
            #     transcription = transcription.text  

            #     tt += transcription          
            return jsonify(transcription = transcription)

        return redirect('/index')
    
# @babel.localeselector
# def get_locale():
#     return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'audio'
    app.run()