import os
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Set up secret key for flash messages
app.config["SECRET_KEY"] = "your_secret_key_here"

# Set up the path for SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'test.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.id}>"


# Ensure the database tables are created if not exist
with app.app_context():
    db.create_all()


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task_content = request.form["task"]
        if task_content:
            new_task = Todo(content=task_content)
            try:
                db.session.add(new_task)
                db.session.commit()
                flash("Task added successfully!", "success")
                return redirect("/")
            except Exception as e:
                flash(f"There was an issue adding the task: {e}", "danger")
        else:
            flash("Task content cannot be empty!", "warning")
    else:
        tasks = Todo.query.order_by(Todo.pub_date).all()
        return render_template("index.html", tasks=tasks)


@app.route("/delete/<int:id>")
def delete(id):
    task = Todo.query.get_or_404(id)
    try:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully!", "success")
        return redirect("/")
    except Exception as e:
        flash(f"There was an issue deleting the task: {e}", "danger")
        return redirect("/")


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form["task"]
        try:
            db.session.commit()
            flash("Task updated successfully!", "success")
            return redirect("/")
        except Exception as e:
            flash(f"There was an issue updating the task: {e}", "danger")
            return redirect("/")
    else:
        return render_template("update.html", task=task)


if __name__ == "__main__":
    app.run(debug=True)
