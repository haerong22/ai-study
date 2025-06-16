import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from backend import lol_chain

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.message("안녕")
def message_hello(message, say):
    message_text = message["text"]
    response = lol_chain(message_text, [])
    say(response, thread_ts=message["ts"])

# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()