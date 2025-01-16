from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request
from requests import get
from dotenv import load_dotenv
from pyairtable import Table, Api
from os import environ


load_dotenv()

app = App(token=environ['SLACK_BOT_TOKEN'], signing_secret=environ['SLACK_SIGNING_SECRET'])
flask_app = Flask(__name__)

handler = SlackRequestHandler(app)
airtable = Api(environ['AIRTABLE_API_KEY'])
user_table = airtable.table(base_id=environ['AIRTABLE_BASE_ID'], table_name='Users')

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
    airtable_user = user_table.first(formula=f"{{Slack ID}}='{user_id}'")
    if not airtable_user:
        user_table.create({'Slack ID': user_id, 'Username': username})
        return respond("You don't have permission to do that!")
    elif environ['AIRTABLE_RECORD_ID'] not in airtable_user['fields'].get('Permissions', []):
        return respond("You don't have permission to do that!")
    
    print(f"<{user_id}|{username}> toggled the lamp.")
    pico_ip = open('pico_ip.txt').read()
    print(f"IP: {pico_ip}")
    req = get(f"http://{pico_ip}/toggle")
    info = req.text.split('\n')[1]
    try:
        client.chat_postMessage(channel=body["channel_id"], text=info)
    except Exception:
        respond(info)
        

@app.command("/amber-trust-lamp")
def handle_trust_cmd(ack, body, client, respond):
    ack()
    mentioned_user = body["text"].split()[0]
    mentioned_user_id = mentioned_user[2:-1].split('|')[0]
    mentioned_user_username = mentioned_user.split('|')[1][:-1]
    user_id = body["user_id"]
    username = body["user_name"]
    airtable_user = user_table.first(formula=f"{{Slack ID}}='{user_id}'")
    if not airtable_user:
        user_table.create({'Slack ID': user_id, 'Username': username})
        return respond("You don't have permission to do that!")
    elif not airtable_user['fields'].get('Admin', False):
        return respond("You don't have permission to do that!")
        
    mentioned_airtable_user = user_table.first(formula=f"{{Slack ID}}='{mentioned_user_id}'")
    if not mentioned_airtable_user:
        user_table.create({'Slack ID': mentioned_user_id, 'Username': mentioned_user_username, 'Permissions': [environ['AIRTABLE_RECORD_ID']]})
        return respond(f"Granted <@{mentioned_user_id}> permission to toggle the lamp.")
    elif environ['AIRTABLE_RECORD_ID'] in mentioned_airtable_user['fields'].get('Permissions', []):
        return respond(f"<@{mentioned_user_id}> already has permission to toggle the lamp.")
    else:
        permissions = mentioned_airtable_user['fields'].get('Permissions', [])
        permissions.append(environ['AIRTABLE_RECORD_ID'])
        user_table.update(mentioned_airtable_user['id'], {'Permissions': permissions})
        return respond(f"Granted <@{mentioned_user_id}> permission to toggle the lamp.")


@app.command("/amber-untrust-lamp")
def handle_untrust_cmd(ack, body, client, respond):
    ack()
    mentioned_user = body["text"].split()[0]
    mentioned_user_id = mentioned_user[2:-1].split('|')[0]
    mentioned_user_username = mentioned_user.split('|')[1][:-1]
    user_id = body["user_id"]
    username = body["user_name"]
    airtable_user = user_table.first(formula=f"{{Slack ID}}='{user_id}'")
    if not airtable_user:
        user_table.create({'Slack ID': user_id, 'Username': username})
        return respond("You don't have permission to do that!")
    elif not airtable_user['fields'].get('Admin', False):
        return respond("You don't have permission to do that!")
        
    mentioned_airtable_user = user_table.first(formula=f"{{Slack ID}}='{mentioned_user_id}'")
    if not mentioned_airtable_user:
        user_table.create({'Slack ID': mentioned_user_id, 'Username': mentioned_user_username, 'Permissions': [environ['AIRTABLE_RECORD_ID']]})
        return respond(f"<@{mentioned_user_id}> doesn't have permission to toggle the lamp!")
    elif environ['AIRTABLE_RECORD_ID'] in mentioned_airtable_user['fields'].get('Permissions', []):
        permissions = mentioned_airtable_user['fields'].get('Permissions', [])
        permissions.remove(environ['AIRTABLE_RECORD_ID'])
        user_table.update(mentioned_airtable_user['id'], {'Permissions': permissions})
        return respond(f"<@{mentioned_user_id}> no longer has permission to toggle the lamp.")
    else:
        return respond(f"<@{mentioned_user_id}> doesn't have permission to toggle the lamp!")


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
