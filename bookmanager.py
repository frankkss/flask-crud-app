import os
from flask import Flask, redirect, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = f"sqlite:///{os.path.join(project_dir, 'bookdatabase.db')}"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SECRET_KEY"] = "your_secret_key"  # Needed for flash messages

db = SQLAlchemy(app)

class Book(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return f"<Title: {self.title}>"

@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        title = request.form.get("title")
        if not title:
            flash("Title cannot be empty", "error")
        else:
            try:
                book = Book(title=title)
                db.session.add(book)
                db.session.commit()
                flash("Book added successfully", "success")
            except IntegrityError:
                db.session.rollback()
                flash("Book with this title already exists", "error")
            except Exception as e:
                db.session.rollback()
                flash(f"Failed to add book: {e}", "error")
    books = Book.query.all()
    return render_template("home.html", books=books)

@app.route("/update", methods=["POST"])
def update():
    newtitle = request.form.get("newtitle")
    oldtitle = request.form.get("oldtitle")
    if not newtitle or not oldtitle:
        flash("Title fields cannot be empty", "error")
    else:
        try:
            book = Book.query.filter_by(title=oldtitle).first()
            if book:
                book.title = newtitle
                db.session.commit()
                flash("Book updated successfully", "success")
            else:
                flash("Book not found", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Couldn't update book title: {e}", "error")
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    if not title:
        flash("Title cannot be empty", "error")
    else:
        try:
            book = Book.query.filter_by(title=title).first()
            if book:
                db.session.delete(book)
                db.session.commit()
                flash("Book deleted successfully", "success")
            else:
                flash("Book not found", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Couldn't delete book: {e}", "error")
    return redirect("/")

@app.route('/initdb')
def initdb():
    db.create_all()
    return "Database initialized!"

if __name__ == "__main__":
    app.run(debug=True)
