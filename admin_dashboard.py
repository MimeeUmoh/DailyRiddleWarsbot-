from flask import Flask, render_template_string, request, redirect, url_for
import json

ADMIN_USERNAME = "YOUR_ADMIN_USERNAME"
ADMIN_PASSWORD = "YOUR_ADMIN_PASSWORD"
USERS_FILE = "users_data.json"

app = Flask(__name__)

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid credentials", 403
    return '''
        <form method="POST">
            <input name="username" placeholder="Username">
            <input name="password" type="password" placeholder="Password">
            <button type="submit">Login</button>
        </form>
    '''

@app.route("/admin/dashboard")
def admin_dashboard():
    users = load_users()
    winners = [u for u in users if users[u].get("is_winner")]
    html = "<h1>Winners List</h1><table border=1><tr><th>Name</th><th>Bank</th><th>Phone</th><th>Paid?</th><th>Action</th></tr>"
    for username, data in users.items():
        if data.get("is_winner"):
            html += f"<tr><td>{username}</td><td>{data.get('bank_account')}</td><td>{data.get('phone')}</td><td>{data.get('paid', False)}</td><td><a href='/admin/mark_paid/{username}'>Mark Paid</a></td></tr>"
    html += "</table>"
    return html

@app.route("/admin/mark_paid/<username>")
def mark_paid(username):
    users = load_users()
    if username in users:
        users[username]["paid"] = True
        save_users(users)
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
