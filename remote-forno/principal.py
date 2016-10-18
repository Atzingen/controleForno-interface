from flask import Flask, url_for, request, render_template

app = Flask(__name__)

@app.route("/")
def principal():
    return render_template("controle.html")

if __name__ == "__main__":
    app.run()
