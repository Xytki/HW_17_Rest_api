# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from sqlalchemy.orm import query

from schemas import MovieSchema, GenreSchema, DirectorSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False}
db = SQLAlchemy(app)
api = Api(app)

movie_ns = api.namespace("movies")
movie_schemas = MovieSchema(many=True)
movie_schema = MovieSchema()


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


@movie_ns.route("/")
class MovieViews(Resource):
    def get(self):
        all_movies = Movie.query.all()

        if director_id := request.args.get('director_id'):
            all_movies = db.session.query(Movie).filter(Movie.director_id == director_id)

        if genre_id := request.args.get('genre_id'):
            all_movies = db.session.query(Movie).filter(Movie.genre_id == genre_id)

        return movie_schemas.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_info = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_info)

        return '', 201

    def delete(self, bid: int):
        movie = db.session.query(Movie).get(bid)

        db.session.delete(movie)
        db.session.commit()

        return '', 204


@movie_ns.route("/<int:bid>")
class MovieViews(Resource):
    def get(self, bid: int):
        try:
            movie = Movie.query.get(bid)
            return movie_schema.dump(movie), 200
        except Exception as e:
            return '', 404

    def put(self, bid: int):
        data = request.json
        try:
            db.session.query.filter(Movie.id == bid).update(
                data
            )
            db.session.commit()
            return '', 201

        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 404


genre_ns = api.namespace("genres")
genre_schemas = GenreSchema(many=True)
genre_schema = GenreSchema()


@genre_ns.route("/")
class GenreViews(Resource):
    def get(self):
        all_genres = Genre.query.all()

        return genre_schemas.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_info = Genre(**req_json)

        with db.session.begin():
            db.session.add(new_info)

        return '', 201

    def delete(self, bid: int):
        genre_ = db.session.query(Genre).get(bid)

        db.session.delete(genre_)
        db.session.commit()

        return '', 204


@genre_ns.route("/<int:bid>")
class GenreViews(Resource):
    def get(self, bid: int):
        try:
            genre_ = Genre.query.get(bid)
            return movie_schema.dump(genre_), 200

        except Exception as e:
            return '', 404

    def put(self, bid: int):
        data = request.json
        try:
            db.session.query.filter(Genre.id == bid).update(
                data
            )
            db.session.commit()
            return '', 201

        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 404


directors_ns = api.namespace("directors")
director_schemas = DirectorSchema(many=True)
director_schema = DirectorSchema()


@directors_ns.route("/")
class DirectorsViews(Resource):
    def get(self):
        all_directors = Director.query.all()

        return director_schemas.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_info = Director(**req_json)

        with db.session.begin():
            db.session.add(new_info)

        return '', 201

    def delete(self, bid: int):
        genre_ = db.session.query(Director).get(bid)

        db.session.delete(genre_)
        db.session.commit()

        return '', 204


@directors_ns.route("/<int:bid>")
class DirectorsViews(Resource):
    def get(self, bid: int):
        try:
            genre_ = Director.query.get(bid)
            return movie_schema.dump(genre_), 200
        except Exception as e:
            return '', 404

    def put(self, bid: int):
        data = request.json
        try:
            db.session.query.filter(Director.id == bid).update(
                data
            )
            db.session.commit()
            return '', 201

        except Exception as e:
            print(e)
            db.session.rollback()
            return e, 404


if __name__ == '__main__':
    app.run(debug=True)
