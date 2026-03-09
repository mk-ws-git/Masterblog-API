from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):

    for post in POSTS:
        if post["id"] == post_id:
            return jsonify(post)

    return jsonify({"error": "Post not found"}), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
