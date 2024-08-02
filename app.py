from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv
import os
from moesifwsgi import MoesifMiddleware

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key here
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Customer Onboarding ChatBot!"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')

    # Define the onboarding conversation
    conversation = [
        {"role": "system", "content": "You are a customer onboarding agent."},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=150
    )

    # Extract the response text and token usage

    response_text = response.choices[0].message['content'].strip()
    tokens_used = response.usage.total_tokens

    response_obj =  jsonify({
        'response': response_text,
        # you can put token used.
        # 'tokens_used': tokens_used
    })

    # Add the token usage to the response headers
    response_obj.headers['X-Tokens-Used'] = tokens_used

    return response_obj



## Moesif Middleware Setup:
def identify_user(app, environ, response_headers=dict()):
    # Your custom code that returns a user id string
    return "my-chat-user"

def identify_company(app, environ, response_headers=dict()):
    # Your custom code that returns a company id string
    return "my-chat-company"

moesif_settings = {
    'APPLICATION_ID': os.getenv('MOESIF_APPLICATION_ID'),
    'DEBUG': False,
    'LOG_BODY': True,
    'IDENTIFY_USER': identify_user,
    'IDENTIFY_COMPANY': identify_company,
    'CAPTURE_OUTGOING_REQUESTS': False
}

# flask
app.wsgi_app = MoesifMiddleware(app.wsgi_app, moesif_settings)

if __name__ == "__main__":
    app.run(debug=True)
