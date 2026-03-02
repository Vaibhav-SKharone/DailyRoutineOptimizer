<<<<<<< HEAD
from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, User, Task
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os
from datetime import datetime, timedelta

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

# ---------------- AI OPTIMIZATION ENGINE ---------------- #

def optimize_schedule(tasks):
    priority_map = {"High": 1, "Medium": 2, "Low": 3}
    now = datetime.now()

    # AUTO PRIORITY BOOST (only update once, then commit at end)
    updated = False
    for task in tasks:
        if task.status != "Completed" and task.deadline < now:
            if task.priority != "High":
                task.priority = "High"
                updated = True

    if updated:
        db.session.commit()

    # Sort after updating priority
    sorted_tasks = sorted(
        tasks,
        key=lambda x: (priority_map.get(x.priority, 3), x.deadline)
    )

    optimized_schedule = []
    current_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

    for task in sorted_tasks:
        start_time = current_time
        end_time = start_time + timedelta(minutes=task.duration)

        conflict = end_time > task.deadline

        optimized_schedule.append({
            "task": task,
            "start": start_time,
            "end": end_time,
            "conflict": conflict
        })

        current_time = end_time + timedelta(minutes=10)

    return optimized_schedule

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    optimized = optimize_schedule(tasks)

    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "Completed"])

    productivity_score = 0
    if total_tasks > 0:
        productivity_score = round((completed_tasks / total_tasks) * 100, 2)

    # Category Time Distribution
    category_data = {}
    for task in tasks:
        if task.category:
            category_data[task.category] = category_data.get(task.category, 0) + task.duration

    return render_template(
        "dashboard.html",
        tasks=tasks,
        optimized=optimized,
        productivity_score=productivity_score,
        category_labels=list(category_data.keys()),
        category_values=list(category_data.values())
    )

@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    title = request.form.get("title")
    priority = request.form.get("priority")
    duration = request.form.get("duration")
    deadline = request.form.get("deadline")
    category = request.form.get("category")

    deadline_date = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")

    task = Task(
        title=title,
        priority=priority,
        duration=int(duration),
        deadline=deadline_date,
        category=category,
        user_id=current_user.id,
        status="Pending"
    )

    db.session.add(task)
    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        task.title = request.form.get("title")
        task.priority = request.form.get("priority")
        task.duration = int(request.form.get("duration"))
        task.category = request.form.get("category")
        task.deadline = datetime.strptime(
            request.form.get("deadline"),
            "%Y-%m-%dT%H:%M"
        )

        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("edit_task.html", task=task)

@app.route("/complete_task/<int:task_id>")
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.status = "Completed"
        db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/delete_task/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/weekly_report")
@login_required
def weekly_report():
    one_week_ago = datetime.now() - timedelta(days=7)

    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.deadline >= one_week_ago
    ).all()

    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "Completed"])
    pending_tasks = total_tasks - completed_tasks
    total_time = sum([t.duration for t in tasks])

    completion_rate = 0
    if total_tasks > 0:
        completion_rate = round((completed_tasks / total_tasks) * 100, 2)

    return render_template(
        "weekly_report.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        total_time=total_time,
        completion_rate=completion_rate
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()
=======
from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, User, Task
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os
from datetime import datetime, timedelta

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

# ---------------- AI OPTIMIZATION ENGINE ---------------- #

def optimize_schedule(tasks):
    priority_map = {"High": 1, "Medium": 2, "Low": 3}
    now = datetime.now()

    # AUTO PRIORITY BOOST (only update once, then commit at end)
    updated = False
    for task in tasks:
        if task.status != "Completed" and task.deadline < now:
            if task.priority != "High":
                task.priority = "High"
                updated = True

    if updated:
        db.session.commit()

    # Sort after updating priority
    sorted_tasks = sorted(
        tasks,
        key=lambda x: (priority_map.get(x.priority, 3), x.deadline)
    )

    optimized_schedule = []
    current_time = now.replace(hour=9, minute=0, second=0, microsecond=0)

    for task in sorted_tasks:
        start_time = current_time
        end_time = start_time + timedelta(minutes=task.duration)

        conflict = end_time > task.deadline

        optimized_schedule.append({
            "task": task,
            "start": start_time,
            "end": end_time,
            "conflict": conflict
        })

        current_time = end_time + timedelta(minutes=10)

    return optimized_schedule

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(name=name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    optimized = optimize_schedule(tasks)

    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "Completed"])

    productivity_score = 0
    if total_tasks > 0:
        productivity_score = round((completed_tasks / total_tasks) * 100, 2)

    # Category Time Distribution
    category_data = {}
    for task in tasks:
        if task.category:
            category_data[task.category] = category_data.get(task.category, 0) + task.duration

    return render_template(
        "dashboard.html",
        tasks=tasks,
        optimized=optimized,
        productivity_score=productivity_score,
        category_labels=list(category_data.keys()),
        category_values=list(category_data.values())
    )

@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    title = request.form.get("title")
    priority = request.form.get("priority")
    duration = request.form.get("duration")
    deadline = request.form.get("deadline")
    category = request.form.get("category")

    deadline_date = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")

    task = Task(
        title=title,
        priority=priority,
        duration=int(duration),
        deadline=deadline_date,
        category=category,
        user_id=current_user.id,
        status="Pending"
    )

    db.session.add(task)
    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        task.title = request.form.get("title")
        task.priority = request.form.get("priority")
        task.duration = int(request.form.get("duration"))
        task.category = request.form.get("category")
        task.deadline = datetime.strptime(
            request.form.get("deadline"),
            "%Y-%m-%dT%H:%M"
        )

        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("edit_task.html", task=task)

@app.route("/complete_task/<int:task_id>")
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        task.status = "Completed"
        db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/delete_task/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/weekly_report")
@login_required
def weekly_report():
    one_week_ago = datetime.now() - timedelta(days=7)

    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.deadline >= one_week_ago
    ).all()

    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "Completed"])
    pending_tasks = total_tasks - completed_tasks
    total_time = sum([t.duration for t in tasks])

    completion_rate = 0
    if total_tasks > 0:
        completion_rate = round((completed_tasks / total_tasks) * 100, 2)

    return render_template(
        "weekly_report.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        total_time=total_time,
        completion_rate=completion_rate
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> fa706b1b96a925328b3b1aff641e7b0d1fcd484d
