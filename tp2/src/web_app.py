"""
Exercise 5: Flask web application
"""
from flask import Flask, jsonify, request
from uuid import uuid4

def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(TESTING=False)
    if config:
        app.config.update(config)

    # Stockage en mémoire réinitialisé à chaque create_app
    app.state = {"users": {}}  # id -> {"id","name","age"}

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.post("/users")
    def create_user():
        if not request.is_json:
            return jsonify({"error": "JSON required"}), 400
        data = request.get_json()

        # validations simples
        name = data.get("name")
        age = data.get("age")
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "name is required"}), 400
        if not isinstance(age, int) or age < 0:
            return jsonify({"error": "age must be a non-negative integer"}), 400

        uid = str(uuid4())
        user = {"id": uid, "name": name.strip(), "age": age}
        app.state["users"][uid] = user
        return jsonify(user), 201

    @app.get("/users")
    def list_users():
        return jsonify(list(app.state["users"].values())), 200

    @app.get("/users/<uid>")
    def get_user(uid: str):
        user = app.state["users"].get(uid)
        if not user:
            return jsonify({"error": "not found"}), 404
        return jsonify(user), 200

    @app.put("/users/<uid>")
    def update_user(uid: str):
        user = app.state["users"].get(uid)
        if not user:
            return jsonify({"error": "not found"}), 404
        if not request.is_json:
            return jsonify({"error": "JSON required"}), 400
        data = request.get_json()

        name = data.get("name", user["name"])
        age = data.get("age", user["age"])
        if not isinstance(name, str) or not name.strip():
            return jsonify({"error": "invalid name"}), 400
        if not isinstance(age, int) or age < 0:
            return jsonify({"error": "invalid age"}), 400
        user = {"id": uid, "name": name.strip(), "age": age}
        app.state["users"][uid] = user
        return jsonify(user), 200

    @app.delete("/users/<uid>")
    def delete_user(uid: str):
        if uid not in app.state["users"]:
            return jsonify({"error": "not found"}), 404
        del app.state["users"][uid]
        return "", 204

    return app
