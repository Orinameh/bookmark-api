
from flask import Flask, redirect
import os

import werkzeug
from src.auth import auth
from src.bookmarks import bookmarks
from src.constants.http_status_code import HTTP_404_NOT_FOUND
from src.database import db, Bookmark
from flask_jwt_extended import JWTManager


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(SECRET_KEY=os.environ.get(
            "SECRET_KEY"), SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_URI_DB"),
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"))

    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    JWTManager(app)

    # register the blueprint
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    @app.get('/<short_url>')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits = bookmark.visits + 1
            db.session.commit()

            return redirect(bookmark.url)


    @app.errorhandler(werkzeug.exceptions.NotFound)
    def handle_not_found(e):
        return f'{e}', HTTP_404_NOT_FOUND

    with app.app_context():
        db.create_all()

    return app
