from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float


app = Flask(__name__)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"
db = SQLAlchemy(app)


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[str] = mapped_column(Float, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    result = db.session.execute(db.select(Book).order_by(Book.name))
    # Use .scalars() to get the elements rather than entire rows from the database
    all_books = result.scalars().all()
    return render_template("index.html", books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        book_name = request.form.get('title')
        book_author = request.form.get('author')
        book_rating = request.form.get('rating')
        try:
            book_rating = float(book_rating)  # Convert rating to float
        except ValueError:
            return "Please enter a valid rating."
        # CREATE
        new_book = Book(name=book_name, author=book_author, rating=book_rating)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html')


@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    book_to_edit = db.get_or_404(Book, id)
    if request.method == 'POST':
        # Update book details rating
        book_to_edit.rating = float(request.form['rating'])

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', book=book_to_edit)


@app.route("/delete/<int:id>", methods=['POST'])
def delete(id):
    book_to_delete = db.get_or_404(Book, id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

