# Gable
>[!Warning]
> School project, pretty rushed and not my proudest work.
> Looks cool though, learned some new stuff.

Wordle copy using Flask web server, client-side javascript and server-side python.

Front end all raw html and css.

HTTP requests are sent to server on each key press and dynamic html updates
are then injected into the clients webpage.

>[!Warning]
>The deployment site is <ins>much</ins> slower than running locally
>since I chose to do most back end code in Python server-side by
>handling ever key press as a seperate POST request.

Currently hosted at: https://gable-fsqv.onrender.com

-------
![Example image](https://github.com/GabrielNakamoto/Gable/blob/main/example.png)

-------
## Setup
1. Clone this repository
```git clone https://github.com/GabrielNakamoto/Gable```
3. [Install pip](https://pip.pypa.io/en/stable/installation/)
4. [Install flask](https://flask.palletsprojects.com/en/stable/installation/)
6. Run ```flask --app main run``` in the local repositor7
7. Go to port 5000 on localhost (https://127.0.0.1:5000)
