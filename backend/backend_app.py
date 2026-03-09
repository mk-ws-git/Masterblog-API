from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
    {"id": 3, "title": "Third post", "content": "This is the third post."}
]

USERS = []


def authenticate():
    token = request.headers.get("Authorization")

    if not token:
        return None

    for user in USERS:
        expected_token = f"token-{user['username']}"
        if token == expected_token:
            return user

    return None


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "username and password are required"}), 400

    for user in USERS:
        if user["username"] == data["username"]:
            return jsonify({"error": "Username already exists"}), 400

    new_user = {
        "id": len(USERS) + 1,
        "username": data["username"],
        "password": data["password"]
    }

    USERS.append(new_user)

    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": new_user["id"],
            "username": new_user["username"]
        }
    }), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "username and password are required"}), 400

    for user in USERS:
        if user["username"] == data["username"] and user["password"] == data["password"]:
            return jsonify({
                "message": "Login successful",
                "token": f"token-{user['username']}"
            }), 200

    return jsonify({"error": "Invalid username or password"}), 401


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get("sort")
    direction = request.args.get("direction")

    posts = POSTS.copy()

    if sort_field:
        if sort_field not in ["title", "content"]:
            return jsonify({"error": "Invalid sort field"}), 400

        if direction and direction not in ["asc", "desc"]:
            return jsonify({"error": "Invalid direction"}), 400

        reverse = direction == "desc"

        posts = sorted(
            posts,
            key=lambda post: post[sort_field].lower(),
            reverse=reverse
        )

    return jsonify(posts)


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get("title", "").lower()
    content_query = request.args.get("content", "").lower()

    results = []

    for post in POSTS:
        title_match = title_query in post["title"].lower() if title_query else False
        content_match = content_query in post["content"].lower() if content_query else False

        if title_match or content_match:
            results.append(post)

    return jsonify(results)


@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    for post in POSTS:
        if post["id"] == post_id:
            return jsonify(post)

    return jsonify({"error": "Post not found"}), 404


@app.route('/api/posts', methods=['POST'])
def add_post():
    user = authenticate()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    missing_fields = []

    if not data or not data.get("title"):
        missing_fields.append("title")
    if not data or not data.get("content"):
        missing_fields.append("content")

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"],
        "author": user["username"]
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    user = authenticate()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    for post in POSTS:
        if post["id"] == post_id:
            if data:
                post["title"] = data.get("title", post["title"])
                post["content"] = data.get("content", post["content"])

            return jsonify(post), 200

    return jsonify({"error": "Post not found"}), 404


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    user = authenticate()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    for post in POSTS:
        if post["id"] == post_id:
            POSTS.remove(post)
            return jsonify({
                "message": f"Post with id {post_id} has been deleted successfully."
            }), 200

    return jsonify({"error": "Post not found"}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)