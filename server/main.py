from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from requests import get
from dotenv import load_dotenv
from os import environ


load_dotenv()

app = App(token=environ['SLACK_BOT_TOKEN'], signing_secret=environ['SLACK_SIGNING_SECRET'])
flask_app = Flask(__name__)

handler = SlackRequestHandler(app)

try:
    with open('pico_ip.txt', 'r') as f:
        pass
except FileNotFoundError:
    with open('pico_ip.txt', 'w') as f:
        f.write('')

@app.command("/toggle-lamp")
def handle_command(ack, body, client, respond):
    ack()
    user_id = body["user_id"]
    username = body["user_name"]
    print(f"<{user_id}|{username}> toggled the lamp.")
    pico_ip = open('pico_ip.txt').read()
    print(f"IP: {pico_ip}")
    req = get(f"http://{pico_ip}/toggle")
    info = req.text.split('\n')[1]
    try:
        client.chat_postMessage(channel=body["channel_id"], text=info)
    except Exception:
        respond(info)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route('/check', methods=['GET'])
def check():
    pico_ip = request.args.get('ip')
    with open('pico_ip.txt', 'w') as f:
        f.write(pico_ip)
    
    return pico_ip


if __name__ == "__main__":
    flask_app.run(port=3000)