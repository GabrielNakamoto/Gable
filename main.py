from flask import Flask, request, jsonify, session, make_response
import random

app = Flask(__name__)
app.secret_key = "dev"

# TODO
# - 'how to' page
# - alerts: tell user the correct word, or if they do something invalid
# - use flask templates?

@app.route("/")
def init():
    if 'guess_state' not in session:
        # 0 = not entered
        # 1 = submitted, not in word
        # 2 = in word
        # 3 = in right place
        session['guess_state'] = [[(' ', 0) for _ in range(5)] for _ in range(6)]
    if 'hidden_word' not in session:
        session['hidden_word'] = "hello".upper()
    if 'current_word' not in session:
        session['current_word'] = ""
    if 'word_index' not in session:
        session['word_index'] = 0

    state_divs = serialize_state()
    head =  """<!doctype html>
    <head>
        <title>Gable</title>
        <style>
            body {
                display: flex;
                flex-direction: column;
                background-color: black;
                align-items: center;
            }

            .container {
                display: flex;
                flex-direction: column
            }

            .container > div {
                display: flex;
                flex-direction: row;
            }

            .container > div > div {
                margin: 10px;
                width: 50px;
                height: 50px;
                border: 2px solid white;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .container > div > div p {
                font-size: 35px;
                font-weight: bold;
                color: white;
            }

            #title {
                font-size: 50px;
                color: white;
            }

            #reset {
                margin-top: 20px;
                padding: 10px 30px;
            }
        </style>
         <script src="https://unpkg.com/htmx.org@2.0.4"></script></head>"""
    body = f"""
    <body>
        <h1 id="title">Gable</h1><br><br>
        <div class="container">{state_divs}</div>
        <button id="reset" hx-post="/reset-state" hx-swap="none">New Word</button>"""
    script = """
        <script>
            document.addEventListener('keydown', function(event) {
                fetch('/keypress', {
                    method: 'POST',
                    headers: {
                        'Content-Type' : 'application/json'
                    },
                    body: JSON.stringify({key: event.key})
                }).then(() => {
                    fetch('/progress_update')
                        .then(response => response.text())
                        .then(html => {
                            document.querySelector('.container').innerHTML = html;
                        });
                });
            });
        </script>
    """
    return head + "<body>" + body + script + "</body>"
def serialize_state():
    html = ""
    for word in session['guess_state']:
        html += "<div>"
        for letter, state in word:
            color = "rgba(0, 0, 0, 0)"
            if state == 1:
                color = "rgb(120,124,127)"
            elif state == 2:
                color = "rgb(200,182,83)"
            elif state == 3:
                color = "rgb(108,169,101)"
            html += f'<div style="background-color:{color}"><p>{letter}</p></div>'
        html += "</div>"
    return html

@app.route("/reset-state", methods=['POST'])
def reset_state():
    session['guess_state'] = [[(' ', 0) for _ in range(5)] for _ in range(6)]
    session['hidden_word'] = random.choice(
            [word for word in
                open("wordle-La.txt").read().split()]
    ).upper()
    print("Picked ", session['hidden_word'])
    session['current_word'] = ""
    session['word_index'] = 0

    response = make_response("")
    response.headers["HX-Redirect"] = "/"
    return response

@app.route("/progress_update", methods=['GET'])
def progress_update():
    # also store colour state?
    return serialize_state()

@app.route("/keypress", methods=['POST'])
def key_callback():
    data = request.get_json()
    key_pressed = data.get('key')
    # print(key_pressed)
    if key_pressed == "Enter":
        # check if valid word
        if session['current_word'].lower() in open('wordle-Ta.txt').read().split()+open('wordle-La.txt').read().split():
            # update word state
            for i, letter in enumerate(session['current_word']):
                state = 1
                if session['hidden_word'][i] == letter:
                    state = 3
                elif letter in session['hidden_word']:
                    state = 2
                session['guess_state'][session['word_index']][i]=(
                    session['guess_state'][session['word_index']][i][0],
                    state)
            # reset word
            session['word_index']+=1 
            session['current_word'] = ""
    elif key_pressed == 'Backspace':
        session['current_word']=session['current_word'][:-1]
    elif len(key_pressed) == 1 and len(session['current_word']) < 5:
        session['current_word'] += key_pressed.upper()
    session['guess_state'][session['word_index']]=[(' ', 0)] * 5
    for i, letter in enumerate(session['current_word']):
        session['guess_state'][session['word_index']][i]=(letter, 0)
    return jsonify({'status':'success'})
