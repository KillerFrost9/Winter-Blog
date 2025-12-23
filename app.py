from flask import Flask, render_template_string, request, redirect, make_response, jsonify
import datetime, json, os
import uuid
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
FILE = "posts.json"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['UPLOAD_MAX_SIZE'] = 5 * 1024 * 1024     # For clarity (optional, but good)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


ADMIN_PASSWORD = "wintersoldier225"

next_reply_id = 1

if os.path.exists(FILE):
    posts = json.load(open(FILE, encoding="utf-8"))

    # Collect all existing reply IDs to find the next available
    all_reply_ids = set()

    def collect_and_assign_ids(replies):
        global next_reply_id
        for r in replies:
            if "id" in r:
                all_reply_ids.add(r["id"])
            else:
                r["id"] = next_reply_id
                all_reply_ids.add(next_reply_id)
                next_reply_id += 1
            r.setdefault("likes", 0)
            r.setdefault("replies", [])
            collect_and_assign_ids(r["replies"])

    for p in posts:
        p.setdefault("likes", 0)
        p.setdefault("shares", 0)
        p.setdefault("comments", [])

        for c in p["comments"]:
            c.setdefault("id", len([x for x in p["comments"] if "id" in x]) + 1)
            c.setdefault("likes", 0)
            c.setdefault("replies", [])
            collect_and_assign_ids(c["replies"])

    # Set next_reply_id to one above the highest existing
    if all_reply_ids:
        next_reply_id = max(all_reply_ids) + 1

else:
    posts = [{
        "id": 1,
        "title": "WinterBlog — Pure Winter",
        "content": "Only beautiful blue snowflakes falling — clean, and now everything works perfectly!",
        "author": "Frost King",
        "date": "2025-12-19",
        "likes": 0,
        "shares": 0,
        "comments": []
    }]
        "id": 1,
        "title": "WinterBlog — Pure Winter",
        "content": "Only beautiful blue snowflakes falling — clean, and now everything works perfectly!",
        "author": "Frost King",
        "date": "2025-12-19",
        "likes": 0,
        "shares": 0,
        "comments": []
    }]


def save():
    json.dump(posts, open(FILE, "w", encoding="utf-8"), indent=4)


def count_total_comments(post):
    total = len(post["comments"])

    def count_nested(replies):
        nonlocal total
        total += len(replies)
        for r in replies:
            count_nested(r.get("replies", []))

    for c in post["comments"]:
        count_nested(c.get("replies", []))
    return total


def is_admin():
    """Check if current user is admin via cookie"""
    return request.cookies.get("admin_key") == "true"

snow_effect = """
<script>
    setInterval(() => {
        let s = document.createElement('div');
        s.innerHTML = '&#10052;&#65039;';
        s.style.position = 'fixed';
        s.style.left = Math.random() * 100 + 'vw';
        s.style.top = '-10vh';
        s.style.fontSize = (Math.random() * 1.4 + 1.8) + 'em';
        s.style.color = '#00e0ff';
        s.style.pointerEvents = 'none';
        s.style.userSelect = 'none';
        s.style.animation = 'snowfall linear forwards';
        s.style.animationDuration = (Math.random() * 10 + 12) + 's';
        s.style.opacity = 0.9;
        s.style.zIndex = '9999';
        document.body.appendChild(s);
        setTimeout(() => s.remove(), 35000);
    }, 300);
</script>
<style>
    @keyframes snowfall {
        from { transform: translateY(-100vh) rotate(0deg); }
        to   { transform: translateY(120vh) rotate(360deg); }
    }
</style>
"""

heart_style = """
<style>
    @keyframes floatUp {
        0% { transform: translateY(0) scale(1); opacity: 1; }
        100% { transform: translateY(-300px) scale(1.5); opacity: 0; }
    }
    .floating-heart {
        position: fixed;
        font-size: 40px;
        pointer-events: none;
        animation: floatUp 1.8s ease-out forwards;
        z-index: 10000;
        color: #c0392b;
        text-shadow: 0 0 15px #c0392b;
        left: var(--heart-x);
        bottom: var(--heart-y);
    }
    .delete-btn-small {
        background: #990000;
        color: white;
        border: none;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 12px;
        cursor: pointer;
        margin-left: 10px;
    }
</style>
"""


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            resp = make_response(redirect("/"))
            resp.set_cookie("admin_key", "true", max_age=60 * 60 * 24 * 365)
            return resp
        else:
            return "<h2 style='color:red;text-align:center;'>Wrong password!</h2><a href='/admin-login'>Try again</a>"
    return """
    <html><head><title>Admin Login</title>
    <style>body{background:#0a0e17;color:#00ffff;font-family:Arial;text-align:center;padding:100px;}
    input{padding:15px;width:300px;margin:20px;font-size:20px;background:#111;border:3px solid #00ffff;border-radius:12px;color:#00ffff;}
    button{padding:15px 50px;background:#00ffff;color:#000;border:none;border-radius:12px;font-size:22px;cursor:pointer;}
    </style></head><body>
    <h1>🔐 Admin Login</h1>
    <form method="post">
        <input type="password" name="password" placeholder="Enter admin password" required>
        <br>
        <button type="submit">Login</button>
    </form>
    <br><a href="/" style="color:#888;">← Back to blog</a>
    </body></html>
    """


@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>WinterBlog</title>
        <style>
            body {font-family:Arial; background:#0a0e17; color:#fff; margin:0; padding:20px;}
            h1 {text-align:center; color:#00ffff; text-shadow:0 0 30px #00ffff; font-size:50px;}
            .btn {background:#00ffff; color:#000; padding:20px 50px; text-decoration:none; border-radius:15px; font-weight:bold; font-size:24px; display:inline-block;}
            .post {background:#1a2332; padding:30px; margin:40px auto; max-width:900px; border-radius:20px; border-left:8px solid #00ffff; box-shadow:0 0 40px rgba(0,255,255,0.3); position:relative;}
            .edit-btn {position:absolute; top:20px; right:20px; background:#000; color:#fff; border:none; padding:8px 16px; border-radius:8px; font-size:14px; cursor:pointer;}
            .post-title {margin:0 120px 10px 0; color:#00ffff; font-size:28px;}
            .post-meta {color:#888; margin-bottom:15px;}
            .post-content {line-height:1.9; font-size:19px;}
            .actions-bottom {display:flex; gap:12px; justify-content:flex-end; flex-wrap:wrap; margin-top:30px;}
            .action-btn {padding:10px 20px; border:none; border-radius:12px; cursor:pointer; font-weight:bold; font-size:14px; position:relative; overflow:hidden;}
            .like-btn    {background:#27ae60; color:white;}
            .comment-btn {background:#ffcc00; color:black;}
            .share-btn   {background:#0088ff; color:white;}
            .delete-btn  {background:#ff0066; color:white;}
            .comment-section {display:none; margin-top:30px; background:#000; padding:30px; border-radius:15px; border:3px solid #00ffff;}
            input, textarea {width:100%; padding:18px; margin:15px 0; background:#111; color:#00ffff; border:3px solid #00ffff; border-radius:12px;}
            button.send {background:#00ffff; color:black; padding:15px 40px; border:none; border-radius:12px;}
            .reply-item {background:#222; padding:14px; border-radius:10px; margin:15px 0 0 40px; border-left:4px solid #00aaff; box-shadow:0 0 10px rgba(0,170,255,0.2);}
            .nested-reply {margin-left: 50px; border-left:2px dashed #00aaff; padding-left:15px;}
        </style>
        """ + heart_style + """
    </head>
    <body>
        <div style="text-align:center; margin:60px 0 40px; display:flex; justify-content:center; align-items:center; gap:60px; flex-wrap:wrap;">
            <img src="https://i.pinimg.com/originals/83/be/51/83be51d616bcc58a6829d81828be77a5.gif" alt="Twinkling Christmas Tree" style="height:80px; width:auto;">
            <h1 style="margin:0; font-size:50px; color:#00ffff; text-shadow:0 0 30px #00ffff;">WinterBlog</h1>
            <img src="https://i.pinimg.com/originals/83/be/51/83be51d616bcc58a6829d81828be77a5.gif" alt="Twinkling Christmas Tree" style="height:80px; width:auto;">
        </div>

        <center>
    <a href="/new" class="btn">+ New Post</a>
    {% if is_admin() %}
        <span style="margin-left:30px; color:#00ff00; font-size:18px;">(Admin Mode 🔑)</span>
        <a href="/admin-logout" style="margin-left:20px; color:#ff4444; font-size:16px; text-decoration:underline;">Logout</a>
    {% else %}
        <br><br>
        <a href="/admin-login" style="color:#888; font-size:16px;">Admin Login</a>
    {% endif %}
</center>
        <hr style="border-color:#333;">

        {% for p in posts[::-1] %}
        <div class="post" id="post{{p.id}}">
            {% set current_author = request.cookies.get('author_' + p.id|string) or p.author %}
{% if is_admin() or current_author == p.author %}
    <a href="/edit/{{p.id}}"><button class="edit-btn">Edit</button></a>
    
    <form method="post" action="/delete/{{p.id}}" onsubmit="return confirm('Delete this post forever?');" style="display:inline; margin-left:15px;">
        <button type="submit" class="action-btn delete-btn" style="padding:8px 14px; font-size:13px; background:#990000;">Delete Post</button>
    </form>
{% endif %}

            <h2 class="post-title">{{p.title}}</h2>
            <div class="post-meta">{{p.author}} — {{p.date}}</div>

            {% if p.image %}
            <div style="text-align:center; margin:20px 0;">
                <img src="{{p.image}}" style="max-width:100%; max-height:600px; border-radius:15px; border:4px solid #00ffff; box-shadow:0 0 30px rgba(0,255,255,0.5);">
            </div>
            {% endif %}

            <div class="post-content">{{p.content|replace('\n','<br>')|safe}}</div>

            <div class="actions-bottom">
                <button class="action-btn like-btn" onclick="likePost(event, {{p.id}})">
                    ❤️ Like <span id="post-likes-{{p.id}}">{{p.likes}}</span>
                </button>

                <button class="action-btn comment-btn" onclick="toggleComment('c{{p.id}}')">
                    💬 Comment <span id="total-comments-{{p.id}}">{{ count_total_comments(p) }}</span>
                </button>
                <button class="action-btn share-btn" onclick="sharePost({{p.id}}, {{ p.title|tojson }})">
                    📤 Share {{p.shares}}
                </button>

            </div>

            <div class="comment-section" id="c{{p.id}}">
                <h3 style="color:#00ffff;">Comments (<span id="comments-count-{{p.id}}">{{ count_total_comments(p) }}</span>)</h3>

                <div id="comments-list-{{p.id}}">
                {% macro render_replies(replies, post_id, parent_id) %}
                    {% for r in replies %}
                    <div class="reply-item" id="reply-{{post_id}}-{{r.id}}">
                        <div style="display:flex; justify-content:space-between; align-items:start;">
                            <div>
                                <strong>{{r.name}}:</strong>
                                <div style="margin-top:6px; font-size:15px;">
                                    {{r.text|replace('\n','<br>')|safe}}
                                </div>
                            </div>
                        {% if is_admin() or request.cookies.get('reply_author_' + r.id|string) == r.name %}
                            <form method="post" action="/delete-reply/{{post_id}}/{{r.id}}" onsubmit="return confirm('Delete this reply?');">
                                <button type="submit" class="delete-btn-small">🗑️ Delete</button>
                            </form>
                            {% endif %}
                        </div>
                        <div style="margin-top:10px; display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
                            <button onclick="likeReply(event, {{post_id}}, {{r.id}})">👍 <span id="reply-likes-{{post_id}}-{{r.id}}">{{r.likes}}</span></button>
                            <button onclick="toggleReply('nr{{post_id}}_{{parent_id}}_{{r.id}}')">💬 Reply</button>
                        </div>

                        {% if r.replies %}
                            <div class="nested-reply">
                                {{ render_replies(r.replies, post_id, r.id) }}
                            </div>
                        {% endif %}

                        <div id="nr{{post_id}}_{{parent_id}}_{{r.id}}" style="display:none; margin-top:12px;">
                            <form onsubmit="submitNestedReply(event, {{post_id}}, {{r.id}})">
                                <input name="name" placeholder="Your name" required>
                                <textarea name="reply" rows="3" placeholder="Write a reply..." required></textarea>
                                <button type="submit">Reply</button>
                            </form>
                        </div>
                    </div>
                    {% endfor %}
                {% endmacro %}

                {% for c in p.comments %}
                <div style="background:#111;padding:18px;border-radius:12px;margin:12px 0;" id="comment-{{p.id}}-{{c.id}}">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div>
                            <strong>{{c.name}}:</strong>
                            <div style="margin-top:8px;">
                                {{c.text|replace('\n','<br>')|safe}}
                            </div>
                        </div>
                        {% if is_admin() or c.name == request.cookies.get('comment_author_' + c.id|string) %}
                        <form method="post" action="/delete-comment/{{p.id}}/{{c.id}}" onsubmit="return confirm('Delete this comment and all replies?');">
                            <button type="submit" class="delete-btn-small">🗑️ Delete</button>
                        </form>
                        {% endif %}
                    </div>

                    <div style="margin-top:12px; display:flex; gap:12px; align-items:center;">
                        <button onclick="likeComment(event, {{p.id}}, {{c.id}})">👍 <span id="comment-likes-{{p.id}}-{{c.id}}">{{c.likes}}</span></button>
                        <button onclick="toggleReply('r{{p.id}}_{{c.id}}')">💬 Reply</button>
                    </div>

                    <div class="replies-container">
                        {{ render_replies(c.replies, p.id, c.id) }}
                    </div>

                    <div id="r{{p.id}}_{{c.id}}" style="display:none; margin-top:12px;">
                        <form onsubmit="submitReply(event, {{p.id}}, {{c.id}})">
                            <input name="name" placeholder="Your name" required>
                            <textarea name="reply" rows="3" placeholder="Write a reply..." required></textarea>
                            <button type="submit">Reply</button>
                        </form>
                    </div>
                </div>
                {% endfor %}
                </div>

                <form onsubmit="submitComment(event, {{p.id}})">
                    <input name="name" placeholder="Your name" required>
                    <textarea name="comment" placeholder="Write a comment..." required></textarea>
                    <button type="submit" class="send">Post Comment</button>
                </form>
            </div>
        </div>
        {% endfor %}

        <script>
            // All your existing JS remains exactly the same
            function createHeart(x, y) {
                const heart = document.createElement('div');
                heart.className = 'floating-heart';
                heart.innerHTML = '❤️';
                heart.style.setProperty('--heart-x', x + 'px');
                heart.style.setProperty('--heart-y', window.innerHeight - y + 'px');
                document.body.appendChild(heart);
                setTimeout(() => heart.remove(), 2000);
            }

            function toggleComment(id) {
                const el = document.getElementById(id);
                el.style.display = el.style.display === "block" ? "none" : "block";
            }

            function toggleReply(id) {
                const el = document.getElementById(id);
                el.style.display = el.style.display === "block" ? "none" : "block";
            }

            async function likePost(event, postId) {
                const btn = event.currentTarget;
                const rect = btn.getBoundingClientRect();
                const x = rect.left + rect.width / 2;
                const y = rect.top + rect.height / 2;
                createHeart(x, y);

                const resp = await fetch("/like/" + postId, { method: "POST" });
                const data = await resp.json();
                document.getElementById("post-likes-" + postId).textContent = data.likes;
            }

            async function likeComment(event, postId, commentId) {
                const btn = event.currentTarget;
                const rect = btn.getBoundingClientRect();
                const x = rect.left + rect.width / 2;
                const y = rect.top + rect.height / 2;
                createHeart(x, y);

                const resp = await fetch(`/comment-like/${postId}/${commentId}`, { method: "POST" });
                const data = await resp.json();
                document.getElementById("comment-likes-" + postId + "-" + commentId).textContent = data.likes;
                updateCommentCounts(postId);
            }

            async function likeReply(event, postId, replyId) {
                const btn = event.currentTarget;
                const rect = btn.getBoundingClientRect();
                const x = rect.left + rect.width / 2;
                const y = rect.top + rect.height / 2;
                createHeart(x, y);

                const resp = await fetch(`/reply-like/${postId}/${replyId}`, { method: "POST" });
                const data = await resp.json();
                document.getElementById("reply-likes-" + postId + "-" + replyId).textContent = data.likes;
                updateCommentCounts(postId);
            }

            function updateCommentCounts(postId) {
                fetch("/comment-count/" + postId)
                    .then(r => r.json())
                    .then(data => {
                        const total = document.getElementById("total-comments-" + postId);
                        const count = document.getElementById("comments-count-" + postId);
                        if (total) total.textContent = data.count;
                        if (count) count.textContent = data.count;
                    });
            }

            async function submitComment(event, postId) {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                const name = formData.get('name');
                const resp = await fetch("/comment/" + postId, { method: "POST", body: formData });
                const data = await resp.json();
                document.getElementById("comments-list-" + postId).insertAdjacentHTML('afterbegin', data.html);
                form.reset();
                updateCommentCounts(postId);
                // Remember author for delete permission
                if (data.comment_id) {
                    document.cookie = `comment_author_${data.comment_id}=${encodeURIComponent(name)}; path=/; max-age=315360000`;
                }
            }

            async function submitReply(event, postId, commentId) {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                const resp = await fetch("/reply/" + postId + "/" + commentId, { method: "POST", body: formData });
                const data = await resp.json();
                const container = document.querySelector("#comment-" + postId + "-" + commentId + " .replies-container");
                container.insertAdjacentHTML('afterbegin', data.html);
                form.reset();
                updateCommentCounts(postId);
            }

            async function submitNestedReply(event, postId, parentReplyId) {
                event.preventDefault();
                const form = event.target;
                const formData = new FormData(form);
                const resp = await fetch("/nested-reply/" + postId + "/" + parentReplyId, { method: "POST", body: formData });
                const data = await resp.json();
                const parent = document.getElementById("reply-" + postId + "-" + parentReplyId);
                let nested = parent.querySelector(".nested-reply");
                if (!nested) {
                    nested = document.createElement("div");
                    nested.className = "nested-reply";
                    parent.appendChild(nested);
                }
                nested.insertAdjacentHTML('afterbegin', data.html);
                form.reset();
                updateCommentCounts(postId);
            }

            function sharePost(id, title) {
                const confirmCopy = confirm("Do you want to copy this post to clipboard?");
                if (!confirmCopy) return;
                const url = window.location.origin + "/#post" + id;
                const text = `"${title}" — Check this amazing post on FrostBlog!\\n${url}`;
                navigator.clipboard.writeText(text).then(() => {
                    alert("Post copied to clipboard! 🎉");
                    fetch("/share/" + id, { method: "POST" });
                });
            }
        </script>
    </body>
    </html>
    """, posts=posts, count_total_comments=count_total_comments, is_admin=is_admin)

@app.route("/like/<int:post_id>", methods=["POST"])
def like(post_id):
    cookie_name = f"liked_post_{post_id}"
    for p in posts:
        if p["id"] == post_id:
            was_liked = request.cookies.get(cookie_name)
            if was_liked:
                p["likes"] -= 1
            else:
                p["likes"] += 1
            save()
            resp = make_response(jsonify({"likes": p["likes"]}))
            if was_liked:
                resp.set_cookie(cookie_name, "", expires=0)
            else:
                resp.set_cookie(cookie_name, "1", max_age=60 * 60 * 24 * 365 * 10)
            return resp
    return jsonify({"likes": 0})


@app.route("/comment-like/<int:post_id>/<int:comment_id>", methods=["POST"])
def like_comment(post_id, comment_id):
    cookie_name = f"liked_comment_{post_id}_{comment_id}"
    was_liked = request.cookies.get(cookie_name)

    for p in posts:
        if p["id"] == post_id:
            for c in p["comments"]:
                if c["id"] == comment_id:
                    if was_liked:
                        c["likes"] -= 1
                    else:
                        c["likes"] += 1
                    save()
                    resp = make_response(jsonify({"likes": c["likes"]}))
                    if was_liked:
                        resp.set_cookie(cookie_name, "", expires=0)
                    else:
                        resp.set_cookie(cookie_name, "1", max_age=60 * 60 * 24 * 365 * 10)
                    return resp
    return jsonify({"likes": 0})


@app.route("/reply-like/<int:post_id>/<int:reply_id>", methods=["POST"])
def like_reply(post_id, reply_id):
    cookie_name = f"liked_reply_{post_id}_{reply_id}"
    was_liked = request.cookies.get(cookie_name)

    def toggle(replies):
        nonlocal was_liked
        for r in replies:
            if r["id"] == reply_id:
                if was_liked:
                    r["likes"] -= 1
                else:
                    r["likes"] += 1
                save()
                resp = make_response(jsonify({"likes": r["likes"]}))
                if was_liked:
                    resp.set_cookie(cookie_name, "", expires=0)
                else:
                    resp.set_cookie(cookie_name, "1", max_age=60 * 60 * 24 * 365 * 10)
                return resp
            if r.get("replies"):
                result = toggle(r["replies"])
                if result: return result
        return None

    for p in posts:
        if p["id"] == post_id:
            for c in p["comments"]:
                result = toggle(c["replies"])
                if result:
                    return result
    return jsonify({"likes": 0})

@app.route("/nested-reply/<int:post_id>/<int:parent_reply_id>", methods=["POST"])
def nested_reply(post_id, parent_reply_id):
    global next_reply_id

    def find_and_add(replies):
        for r in replies:
            if r["id"] == parent_reply_id:
                new_reply = {
                    "id": next_reply_id,
                    "name": request.form["name"],
                    "text": request.form["reply"],
                    "likes": 0,
                    "replies": []
                }
                global next_reply_id
                next_reply_id += 1
                r.setdefault("replies", []).insert(0, new_reply)
                save()

                html = render_template_string("""
                <div class="reply-item" id="reply-{{post_id}}-{{id}}">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div>
                            <strong>{{name}}:</strong>
                            <div style="margin-top:6px; font-size:15px;">
                                {{text|replace('\n','<br>')|safe}}
                            </div>
                        </div>
                        {% if is_admin() or request.cookies.get('reply_author_' + id|string) == name %}
                        <form method="post" action="/delete-reply/{{post_id}}/{{id}}" onsubmit="return confirm('Delete this reply?');">
                            <button type="submit" class="delete-btn-small">🗑️ Delete</button>
                        </form>
                        {% endif %}
                    </div>
                    <div style="margin-top:10px; display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
                        <button onclick="likeReply(event, {{post_id}}, {{id}})">👍 <span id="reply-likes-{{post_id}}-{{id}}">0</span></button>
                        <button onclick="toggleReply('nr{{post_id}}_{{parent_id}}_{{id}}')">💬 Reply</button>
                    </div>
                    <div class="nested-reply"></div>
                    <div id="nr{{post_id}}_{{parent_id}}_{{id}}" style="display:none; margin-top:12px;">
                        <form onsubmit="submitNestedReply(event, {{post_id}}, {{id}})">
                            <input name="name" placeholder="Your name" required>
                            <textarea name="reply" rows="3" placeholder="Write a reply..." required></textarea>
                            <button type="submit">Reply</button>
                        </form>
                    </div>
                </div>
                """, post_id=post_id, parent_id=parent_reply_id, id=new_reply["id"], name=new_reply["name"], text=new_reply["text"])

                resp = make_response(jsonify({"html": html}))
                resp.set_cookie(f"reply_author_{new_reply['id']}", new_reply["name"], max_age=60*60*24*365*10)
                return resp

            if r.get("replies"):
                result = find_and_add(r["replies"])
                if result:
                    return result
        return None

    for p in posts:
        if p["id"] == post_id:
            for c in p["comments"]:
                result = find_and_add(c.get("replies", []))
                if result:
                    return result

    return jsonify({"html": ""})


@app.route("/comment-count/<int:post_id>")
def comment_count(post_id):
    for p in posts:
        if p["id"] == post_id:
            return jsonify({"count": count_total_comments(p)})
    return jsonify({"count": 0})


@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    global next_reply_id
    for p in posts:
        if p["id"] == post_id:
            next_id = max([c.get("id", 0) for c in p["comments"]], default=0) + 1
            new_comment = {
                "id": next_id,
                "name": request.form["name"],
                "text": request.form["comment"],
                "likes": 0,
                "replies": []
            }
            p["comments"].insert(0, new_comment)
            save()
            html = render_template_string("""
            <div style="background:#111;padding:18px;border-radius:12px;margin:12px 0;" id="comment-{{post_id}}-{{id}}">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div><strong>{{name}}:</strong><div style="margin-top:8px;">{{text|replace('\\n','<br>')|safe}}</div></div>
                    {% if is_admin() or name == request.form.get('name') %}
                    <form method="post" action="/delete-comment/{{post_id}}/{{id}}" onsubmit="return confirm('Delete this comment and all replies?');">
                        <button type="submit" class="delete-btn-small">🗑️ Delete</button>
                    </form>
                    {% endif %}
                </div>
                <div style="margin-top:12px; display:flex; gap:12px;">
                    <button onclick="likeComment(event, {{post_id}}, {{id}})">👍 <span id="comment-likes-{{post_id}}-{{id}}">0</span></button>
                    <button onclick="toggleReply('r{{post_id}}_{{id}}')">💬 Reply</button>
                </div>
                <div class="replies-container"></div>
                <div id="r{{post_id}}_{{id}}" style="display:none; margin-top:12px;">
                    <form onsubmit="submitReply(event, {{post_id}}, {{id}})">
                        <input name="name" placeholder="Your name" required>
                        <textarea name="reply" rows="3" placeholder="Write a reply..." required></textarea>
                        <button type="submit">Reply</button>
                    </form>
                </div>
            </div>
            """, post_id=post_id, id=next_id, name=new_comment["name"], text=new_comment["text"], is_admin=is_admin)
            return jsonify({"html": html, "comment_id": next_id})
    return jsonify({"html": ""})


@app.route("/reply/<int:post_id>/<int:comment_id>", methods=["POST"])
def reply(post_id, comment_id):
    global next_reply_id
    for p in posts:
        if p["id"] == post_id:
            for c in p["comments"]:
                if c["id"] == comment_id:
                    new_reply = {
                        "id": next_reply_id,
                        "name": request.form["name"],
                        "text": request.form["reply"],
                        "likes": 0,
                        "replies": []
                    }
                    next_reply_id += 1
                    c.setdefault("replies", []).insert(0, new_reply)
                    save()

                    html = render_template_string("""
                    <div class="reply-item" id="reply-{{post_id}}-{{id}}">
                        <div style="display:flex; justify-content:space-between; align-items:start;">
                            <div>
                                <strong>{{name}}:</strong>
                                <div style="margin-top:6px; font-size:15px;">
                                    {{text|replace('\n','<br>')|safe}}
                                </div>
                            </div>
                            {% if is_admin() or request.cookies.get('reply_author_' + id|string) == name %}
                            <form method="post" action="/delete-reply/{{post_id}}/{{id}}" onsubmit="return confirm('Delete this reply?');">
                                <button type="submit" class="delete-btn-small">🗑️ Delete</button>
                            </form>
                            {% endif %}
                        </div>
                        <div style="margin-top:10px; display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
                            <button onclick="likeReply(event, {{post_id}}, {{id}})">👍 <span id="reply-likes-{{post_id}}-{{id}}">0</span></button>
                            <button onclick="toggleReply('nr{{post_id}}_{{parent_id}}_{{id}}')">💬 Reply</button>
                        </div>
                        <div class="nested-reply"></div>
                        <div id="nr{{post_id}}_{{parent_id}}_{{id}}" style="display:none; margin-top:12px;">
                            <form onsubmit="submitNestedReply(event, {{post_id}}, {{id}})">
                                <input name="name" placeholder="Your name" required>
                                <textarea name="reply" rows="3" placeholder="Write a reply..." required></textarea>
                                <button type="submit">Reply</button>
                            </form>
                        </div>
                    </div>
                    """, post_id=post_id, parent_id=comment_id, id=new_reply["id"], name=new_reply["name"], text=new_reply["text"])

                    resp = make_response(jsonify({"html": html}))
                    resp.set_cookie(f"reply_author_{new_reply['id']}", new_reply["name"], max_age=60*60*24*365*10)
                    return resp
    return jsonify({"html": ""})

@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        new_id = max([p["id"] for p in posts], default=0) + 1
        author = request.form.get("author", "Frost King").strip() or "Frost King"

        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                pass  # No file selected
            elif not allowed_file(file.filename):
                return "<h2 style='color:red;text-align:center;'>Invalid file type! Only images allowed.</h2><a href='/new'>← Try again</a>"
            elif file.content_length > 5 * 1024 * 1024:
                return "<h2 style='color:red;text-align:center;'>File too large! Max 5MB allowed.</h2><a href='/new'>← Try again</a>"
            else:
                filename = str(uuid.uuid4()) + '.' + secure_filename(file.filename).rsplit('.', 1)[1].lower()
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f"/static/uploads/{filename}"

        posts.append({
            "id": new_id,
            "title": request.form["title"],
            "content": request.form["content"],
            "author": author,
            "date": str(datetime.date.today()),
            "image": image_url,  # Save image path
            "likes": 0,
            "shares": 0,
            "comments": []
        })
        save()

        resp = make_response(redirect("/"))
        resp.set_cookie(f"author_{new_id}", author, max_age=60 * 60 * 24 * 365 * 10)
        return resp

    return render_template_string("""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>New Post</title>
    <style>
        body {font-family:Arial; background:linear-gradient(135deg,#0a0e17,#1a2332); color:#fff; margin:0; padding:40px; min-height:100vh;}
        h1 {text-align:center; color:#00ffff; text-shadow:0 0 30px #00ffff; font-size:48px;}
        form {max-width:800px; margin:40px auto; background:rgba(26,35,50,0.9); padding:60px; border-radius:25px; border:4px solid #00ffff;}
        input, textarea {width:100%; padding:20px; margin:20px 0; background:#000; color:#00ffff; border:3px solid #00ffff; border-radius:15px; font-size:20px;}
        button {padding:22px 80px; background:#00ffff; color:#000; border:none; border-radius:18px; font-size:24px;}
        .image-preview {margin:20px 0; text-align:center;}
        .image-preview img {max-width:100%; max-height:400px; border-radius:15px; border:3px solid #00ffff; box-shadow:0 0 20px rgba(0,255,255,0.4);}
    </style></head><body>
        <h1>Create New Post</h1>
        <form method="post" enctype="multipart/form-data">
            <input name="title" placeholder="Title" required>
            <textarea name="content" rows="12" placeholder="Write your winter magic..." required></textarea>
            <input name="author" placeholder="Your name (default: Frost King)">

            <label style="display:block; margin:20px 0 10px; font-size:20px; color:#00ffff;">Add an image (optional):</label>
            <input type="file" name="image" accept="image/*" style="padding:15px; background:#111; border:2px dashed #00ffff; border-radius:12px; width:100%;">

            <div class="image-preview" id="preview"></div>

            <center><button type="submit">Publish</button></center>
        </form>
        <center><a href="/" style="color:#00ffff;font-size:22px;">← Back</a></center>

        <script>
            document.querySelector('input[type=file]').onchange = function(e) {
                if (e.target.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(ev) {
                        document.getElementById('preview').innerHTML = `<img src="${ev.target.result}" alt="Preview">`;
                    }
                    reader.readAsDataURL(e.target.files[0]);
                }
            }
        </script>
        """ + snow_effect + heart_style + """
    </body></html>
    """)


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
def edit(post_id):
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return redirect("/")

    current_author = request.cookies.get(f"author_{post_id}") or post["author"]
    if not (is_admin() or current_author == post["author"]):
        return "<h2 style='color:red;text-align:center;'>You can only edit your own posts!</h2><a href='/'>← Back</a>"

    if request.method == "POST":
        post["title"] = request.form["title"]
        post["content"] = request.form["content"]
        new_author = request.form.get("author", post["author"]).strip() or post["author"]
        post["author"] = new_author

        # Handle new image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                pass
            elif not allowed_file(file.filename):
                return "<h2 style='color:red;text-align:center;'>Invalid file type! Only images allowed.</h2><a href='/edit/{{post.id}}'>← Try again</a>".replace(
                    '{{post.id}}', str(post_id))
            elif file.content_length > 5 * 1024 * 1024:
                return "<h2 style='color:red;text-align:center;'>File too large! Max 5MB allowed.</h2><a href='/edit/{{post.id}}'>← Try again</a>".replace(
                    '{{post.id}}', str(post_id))
            else:
                filename = str(uuid.uuid4()) + '.' + secure_filename(file.filename).rsplit('.', 1)[1].lower()
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                post["image"] = f"/static/uploads/{filename}"
            # If no new image, keep old one

        save()
        resp = make_response(redirect("/"))
        resp.set_cookie(f"author_{post_id}", new_author, max_age=60 * 60 * 24 * 365 * 10)
        return resp

    return render_template_string("""
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Edit Post</title>
    <style>
        body {font-family:Arial; background:#0a0e17; color:#fff; padding:40px;}
        h1 {color:#00ffff; text-align:center; text-shadow:0 0 20px #00ffff;}
        form {max-width:800px; margin:auto; background:#1a2332; padding:50px; border-radius:20px; border:4px solid #00ffff;}
        input, textarea {width:100%; padding:18px; margin:15px 0; background:#000; color:#00ffff; border:3px solid #00ffff; border-radius:12px; font-size:18px;}
        button {background:#00ffff; color:#000; padding:18px 60px; border:none; border-radius:15px; font-size:22px;}
        .current-image {margin:20px 0; text-align:center;}
        .current-image img {max-width:100%; max-height:400px; border-radius:15px; border:3px solid #00ffff;}
    </style></head><body>
        <h1>Edit Post</h1>
        <form method="post" enctype="multipart/form-data">
            <input name="title" value="{{ post.title }}" required>
            <textarea name="content" rows="12" required>{{ post.content }}</textarea>
            <input name="author" value="{{ post.author }}">

            {% if post.image %}
            <div class="current-image">
                <p style="color:#00ffff;">Current image:</p>
                <img src="{{ post.image }}" alt="Current post image">
                <p style="color:#aaa; font-size:14px;">Upload a new image to replace it</p>
            </div>
            {% endif %}

            <label style="display:block; margin:20px 0 10px; font-size:20px; color:#00ffff;">Change image (optional):</label>
            <input type="file" name="image" accept="image/*" style="padding:15px; background:#111; border:2px dashed #00ffff; border-radius:12px; width:100%;">

            <center><button type="submit">Save Changes</button></center>
        </form>
        <center><a href="/" style="color:#888; margin-top:20px;">Cancel</a></center>
        """ + snow_effect + heart_style + """
    </body></html>
    """, post=post)


@app.route("/delete/<int:post_id>", methods=["POST"])
def delete(post_id):
    global posts
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        return redirect("/")

    current_author = request.cookies.get(f"author_{post_id}") or post["author"]
    if not (is_admin() or current_author == post["author"]):
        return "Unauthorized", 403

    posts = [p for p in posts if p["id"] != post_id]
    save()
    return redirect("/")


@app.route("/delete-comment/<int:post_id>/<int:comment_id>", methods=["POST"])
def delete_comment(post_id, comment_id):
    if not is_admin():
        # Try to match name from cookie or current session
        author_cookie = request.cookies.get(f"comment_author_{comment_id}")
        if not author_cookie:
            return "Unauthorized", 403
        # Find the comment to check name
        found = False
        for p in posts:
            if p["id"] == post_id:
                for c in p["comments"]:
                    if c["id"] == comment_id and c["name"] == author_cookie:
                        found = True
                        break
        if not found:
            return "Unauthorized", 403

    for p in posts:
        if p["id"] == post_id:
            p["comments"] = [c for c in p["comments"] if c["id"] != comment_id]
            save()
            break
    return redirect("/")


@app.route("/delete-reply/<int:post_id>/<int:reply_id>", methods=["POST"])
def delete_reply(post_id, reply_id):
    author_cookie = request.cookies.get(f"reply_author_{reply_id}")

    def remove_reply(replies):
        for i, r in enumerate(replies):
            if r["id"] == reply_id:
                # Allow if admin OR the person who wrote it (name matches cookie)
                if is_admin() or (author_cookie and r["name"] == author_cookie):
                    del replies[i]
                    save()
                    return True
                return False  # Unauthorized
            if r.get("replies"):
                if remove_reply(r["replies"]):
                    return True
        return False

    for p in posts:
        if p["id"] == post_id:
            for c in p["comments"]:
                if remove_reply(c.get("replies", [])):
                    return redirect("/")
    return "Unauthorized or reply not found", 403

@app.route("/share/<int:post_id>", methods=["POST"])
def share(post_id):
    for p in posts:
        if p["id"] == post_id:
            p["shares"] += 1
            break
    save()
    return ("", 204)

@app.route("/admin-logout")
def admin_logout():
    resp = make_response(redirect("/"))
    resp.set_cookie("admin_key", "", expires=0)  # Delete the admin cookie
    return resp

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)





