from flask import Flask, request, jsonify
from llama_index import SimpleDirectoryReader, GPTListIndex, readers, GPTSimpleVectorIndex, LLMPredictor, PromptHelper, ServiceContext
from langchain import OpenAI
import sys
import os
import requests
from dotenv import load_dotenv
from IPython.display import Markdown, display
from flask import Flask
from flask import request
from flask import Response

load_dotenv()
app = Flask(__name__)


openai_api_key = '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'
token = '6402013287:AAHl2WI0IA-7xxqmpV1ka3JyJCuJ1Ox7A1I'

def construct_index(directory_path):
    # set maximum input size
    max_input_size = 4096
    # set number of output tokens
    num_outputs = 80
    # set maximum chunk overlap
    max_chunk_overlap = 1000
    # set chunk size limit
    chunk_size_limit = 50

    # define prompt helper
    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

    # define LLM
    llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.4, model_name="text-davinci-003", max_tokens=num_outputs))

    documents = SimpleDirectoryReader(directory_path).load_data()

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)

    index.save_to_disk('index.json')

    return index


    



construct_index("context_data/data")
index = GPTSimpleVectorIndex.load_from_disk('index.json')


# To Get Chat ID and message which is sent by client
def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    print("Chat ID: ", chat_id)
    print("Message: ", text)
    return chat_id, text


# To send message using "SendMessage" API
def send_message_telegram(chat_id, text):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        print(msg)
        chat_id, incoming_que = message_parser(msg)
        query = "As PATGPT, an AI assistant, I answer user queries using provided data, focusing on patalgo.com. I aim for answers within 60 words. For relevant queries only. User Query: "+incoming_que
        response = index.query(query)
        print(response.response)
        
        send_message_telegram(chat_id, response.response)
        return Response('ok', status=200)
    else:
        return "<h1>Something went wrong</h1>"


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5000)



# import telegram.ext 

# def handle_message(update, context):
#     update.message.reply_text("PATGPT: Please wait...")
#     query = "As PATGPT, an AI assistant, I answer user queries using provided data, focusing on patalgo.com. I aim for answers within 60 words. For relevant queries only. User Query: "+update.message.text
#     response = index.query(query)
#     # print(response)
#     display(Markdown(f"Response: <b>{response.response}</b>"))
#     update.message.reply_text(response.response)




# # updater = telegram.ext.Updater(Token, use_context=True)
# # disp = updater.dispatcher
# # print('Telegram Bot Started ...')
# # disp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_message))
# # updater.start_polling()
# # updater.idle()



# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         msg = request.get_json()

#         chat_id, incoming_que = message_parser(msg)
#         # answer = generate_answer(incoming_que)
#         # send_message_telegram(chat_id, answer)
#         # return Response('ok', status=200)
#     else:
#         return "<h1>Something went wrong</h1>"


# if __name__ == '__main__':
#     app.run(host="0.0.0.0", debug=False, port=5000)


# @app.route('/', methods=['GET', 'POST'])
# def handle_query():
#     try:
#         data = request.get_json()
#         user_query = data['query']

#         query = "As PATGPT, an AI assistant, I answer user queries using provided data, focusing on patalgo.com. I aim for answers within 60 words. For relevant queries only. User Query: " + user_query
#         response = index.query(query)

#         # Use Markdown display if needed
#         response_html = Markdown(f"Response: <b>{response.response}</b>").to_html()
#         print(response)

#         return jsonify({"response": response.response, "response_html": response_html})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     Token = os.environ.get("TOKEN")

#     updater = telegram.ext.Updater(Token, use_context=True)
#     disp = updater.dispatcher
#     print('Telegram Bot Started ...')
#     disp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text, handle_message))
#     updater.start_polling()

#     # Run Flask app
#     app.run(host='0.0.0.0', port=5000)