from flask import Flask, request, jsonify, session, make_response, render_template, url_for, flash, get_flashed_messages, redirect
import random

app = Flask(__name__)
app.secret_key = "dev"

color_scheme = [
    "rgba(0, 0, 0, 0)",
    "rgb(120,124,127)",
    "rgb(200,182,83)",
    "rgb(108,169,101)"]
pickable_words = open("wordle-La.txt").read().split()
valid_words = open("wordle-Ta.txt").read().split()

def string_to_div(word):
    html = ""
    for letter in word: html += f'<div><p>{letter}</p></div>'
    return "<div>" + html + "</div>" 

def serialize_state():
    html = ""
    for word in session['guess_state']:
        html += "<div>"
        for letter, state in word:
            color = color_scheme[state]
            html += f'<div style="background-color:{color}"><p>{letter}</p></div>'
        html += "</div>"
    return html

def serialize_key_state():
    html = ""
    for i, x in enumerate("QWERTYUIOPASDFGHJKLZXCVBNM"):
        if x in ['Q', 'A', 'Z']: html += "<div>"
        state = session['key_state'][ord(x.lower())-ord('a')]
        color = color_scheme[state]
        html += f'<div style="background-color:{color}"><p>{x}<p></div>'
        if x in ['P', 'L', 'M']: html += "</div>"
    return html

@app.route("/")
def init():
    if 'key_state' not in session:
        session['key_state'] = [0] * 26
    if 'game_over' not in session:
        session['game_over'] = False
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
    
    return render_template("game.html",
                           serialize_state=serialize_state,
                           serialize_key_state=serialize_key_state,
                           string_to_div=string_to_div)

@app.route("/reset-state", methods=['POST'])
def reset_state():
    session['key_state'] = [0] * 26
    session['game_over'] = False
    session['guess_state'] = [[(' ', 0) for _ in range(5)] for _ in range(6)]
    session['hidden_word'] = random.choice(pickable_words).upper()
    print("Picked ", session['hidden_word'])
    session['current_word'] = ""
    session['word_index'] = 0

    return redirect("/")

@app.route("/progress_update", methods=['GET'])
def progress_update():
    return render_template("game.html",
                           serialize_state=serialize_state,
                           serialize_key_state=serialize_key_state,
                           string_to_div=string_to_div)


@app.route("/keypress", methods=['POST'])
def key_callback():
    if session['game_over']:
        return jsonify({'status':'success'})
    data = request.get_json()
    key_pressed = data.get('key')
    if key_pressed == "Enter":
        # check if valid word
        if session['current_word'].lower() in pickable_words+valid_words:
            # end of game
            if session['word_index'] == 5 or session['current_word'] == session['hidden_word']:
                if session['current_word'] == session['hidden_word']:
                    flash("You win!")
                else:
                    flash(session['hidden_word'])
                session['game_over'] = True
            # update word state
            found = dict([(x, 0) for x in session['hidden_word']])
            for i, letter in enumerate(session['current_word']):
                state = 1
                matches = [j for j, x in enumerate(session['hidden_word']) if session['current_word'][j] == x and x == letter]
                instances = [x for x in session['hidden_word'] if x == letter]

                # we colour the first n of them yellow where n is
                # the difference between how many times its in the target
                # word and how many times the user got it right
                diff = len(instances) - len(matches)
                if letter == session['hidden_word'][i]:
                    state = 3
                elif letter in session['hidden_word'] and found[letter] < diff:
                    found[letter]+=1
                    state = 2
                # only update keybaord if its a better state?
                session['key_state'][ord(letter.lower())-ord('a')]=state
                session['guess_state'][session['word_index']][i]=(
                    session['guess_state'][session['word_index']][i][0],
                    state)
            # reset word
            session['word_index']+=1 
            session['current_word'] = ""
        else:
            flash("Not in word list")
    elif key_pressed == 'Backspace':
        session['current_word']=session['current_word'][:-1]
    elif len(key_pressed) == 1 and len(session['current_word']) < 5 and key_pressed.isalpha():
        session['current_word'] += key_pressed.upper()
    if session['word_index'] < 6:
        session['guess_state'][session['word_index']]=[(' ', 0)] * 5
    for i, letter in enumerate(session['current_word']):
        session['guess_state'][session['word_index']][i]=(letter, 0)
    return jsonify({'status':'success'})
