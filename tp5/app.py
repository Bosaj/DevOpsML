from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Bonjour, ceci est une application Docker TP!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)