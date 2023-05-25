# coding=utf-8
from flask import Flask, make_response,request,Response
import os
import json
import requests
import logging


app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
app.config['JSON_AS_ASCII'] = False




@app.route('/', methods=['GET'])
def home():
    return 'Hello, World!'

@app.route('/chat', methods=['POST'])
def text_process():
    bot = chat()
    if request.method == 'GET':
        return 'This is a GET request to /chat'
    if request.method == 'POST':
        data = json.loads(request.data)
        key = data['key']
        del data['key']
        model = data['model']
        content = data['messages'][0]['content']
        response = chat.create_chatgpt_request(key,model,content)
        return response
    
@app.route('/translate', methods=['GET','POST'])
def audio_translate():
    bot = chat()
    if request.method == 'GET':
        return 'This is a GET request to Trasnlate'
    if request.method == 'POST': 
        model = "gpt-3.5-turbo"
        for header in request.headers:
            if(header[0] == "Authorization"):  
                key = header[1].replace('Bearer ','')

        for file_name in request.files:
            file = request.files.get(file_name) 
            

        logger.info(file)

        response_trans = chat.whisper_translate(key,file)

        response_trans_json = response_trans.json()
        if(response_trans.status_code != 200):
             
             response_trans_json['model'] = "whisper-trasnlate"
             logger.warn(response_trans_json)
        
        else:
            logger.info(response_trans_json)

            logger.info("wating for GPT response......")
            response_gpt = chat.create_chatgpt_request(key,model,response_trans_json['text'])
            response_gpt_json = response_gpt.json()

            if(response_gpt.status_code != 200):

                response_gpt_json['model'] = model
                logger.warn(response_gpt_json)

            else:

                response_gpt_json['whisper'] = response_trans_json['text']
                logger.info(response_gpt_json)

            return response_gpt_json

    

@app.route('/audio' ,methods=['GET','POST'])
def audio_process():
    bot = chat()
    if request.method == 'GET':

        return "this audio test"
    if request.method == 'POST':
        model = "gpt-3.5-turbo"



        for header in request.headers:
            if(header[0] == "Authorization"):  
                key = header[1].replace('Bearer ','')

        for file_name in request.files:
            file = request.files.get(file_name) 

        logger.info(file)

        response_stt = chat.whisper_transcribe(key,file)
        response_stt_json = response_stt.json()
        if(response_stt.status_code != 200):
             
             response_stt_json['model'] = "whisper"
             logger.warn(response_stt_json)
             
             return response_stt_json
        
        else:
            logger.info(response_stt_json)
            logger.info("wating for GPT response......")
            content = response_stt_json['text'] 
            response_gpt = chat.create_chatgpt_request(key,model,content)
            response_gpt_json = response_gpt.json()
           

            if(response_gpt.status_code != 200):

                response_gpt_json['model'] = model
                logger.warn(response_gpt_json)

            else:
                

                response_gpt_json['whisper'] = response_stt_json['text']

                logger.info(response_gpt_json)

           
            return response_gpt_json

    
class chat ():
    def create_chatgpt_request(OPENAI_API_KEY, model, content):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + OPENAI_API_KEY
        }

        messages=[{"role":"system", "content":"answer in just one sentence "},
                    {"role":"user", "content": content}]
        data = {
        "model":model,
        "messages": messages,
        }
        print(data)
        response = requests.post(url, headers=headers, json=data)
 
        return response

    def whisper_transcribe(OPENAI_API_KEY,audio_file):
        url="https://api.openai.com/v1/audio/transcriptions"
        headers = {
            # "Content-Type": "multipart/from-data",
            "Authorization": "Bearer " + OPENAI_API_KEY,
        }


        files = {
                'file': (audio_file.filename, audio_file.read()),
                'model': (None, "whisper-1"),
                 }
        response = requests.post(url, headers=headers, files=files)
        

        return response

    def whisper_translate(OPENAI_API_KEY,audio_file):
        url="https://api.openai.com/v1/audio/translations"
        headers = {
            # "Content-Type": "application/json",
            "Authorization": "Bearer " + OPENAI_API_KEY
        }
        files = {
                'file': (audio_file.filename, audio_file.read()),
                'model': (None, "whisper-1"),
                 }
      
        response = requests.post(url, headers=headers, files=files)
     
       
        return response


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
