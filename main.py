from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)

API_KEY = "de62470244e0fb2b1e9d292318c76260"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

class RateMovie(FlaskForm):
    rating = StringField(label="Your rating out of 10")
    review = StringField(label="Your review")
    update = SubmitField(label="Update")

class AddMovie(FlaskForm):
    movie = StringField(label="Movie title", validators=[DataRequired()])
    year = StringField(label="Year", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    rating = FloatField("Rating", validators=[DataRequired()])
    ranking = FloatField("Ranking", validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    img_url = StringField('Url', validators=[DataRequired()])
    add = SubmitField(label="Add Movie")

# CREATE DB
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[int] = mapped_column(String(500), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()

# with app.app_context():
#     second_movie = Movie(
#         title="Avatar The Way of Water",
#         year=2022,
#         description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#         rating=7.3,
#         review="I liked the water.",
#         img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
#     )
#     db.session.add(second_movie)
#     db.session.commit()

@app.route("/")
def home():
    movies = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = movies.scalars().all() # convert ScalarResult to Python List

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i

    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    update_form = RateMovie()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if update_form.validate_on_submit():
        movie.rating = float(update_form.rating.data)
        movie.review = update_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, update_form=update_form)

@app.route('/delete')
def delete():
    movie_id = request.args.get("id")
    movie_delete = db.get_or_404(Movie, movie_id)
    db.session.delete(movie_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods=["GET", "POST"])
def add():
    add_form = AddMovie()
    if add_form.validate_on_submit():
        new_movie = Movie(
            title=add_form.movie.data,
            year=add_form.year.data,
            description=add_form.description.data,
            rating=add_form.rating.data,
            ranking=add_form.ranking.data,
            review=add_form.review.data,
            img_url=add_form.img_url.data
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", add_form=add_form)

if __name__ == '__main__':
    app.run(debug=True)
