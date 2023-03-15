from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
import validators
from src.constants.http_status_code import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from src.database import Bookmark, db

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route('/', methods=['GET', 'POST'])
@jwt_required()
def handle_bookmarks():
    current_user_id = get_jwt_identity()
    if request.method == 'POST':
        body = request.json.get('body', '')
        url = request.json.get('url', '')

        if not validators.url(url):
            return jsonify({
                'error', 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                'error', 'URl already exists'
            }), HTTP_409_CONFLICT

        bookmark = Bookmark(url=url, body=body, user_id=current_user_id)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at

        }), HTTP_201_CREATED

    else:
        page = request.args.get('page', 1, type=int)

        per_page = request.args.get('per_page', 5, type=int)

        bookmark_list = db.paginate(Bookmark.query.filter_by(
            user_id=current_user_id), page=page, per_page=per_page)

        data = []

        for bookmark in bookmark_list.items:
            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visit': bookmark.visits,
                'body': bookmark.body,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at
            })

            meta = {
                "page": bookmark_list.page,
                "pages": bookmark_list.pages,
                "total_count": bookmark_list.total,
                "prev": bookmark_list.prev_num,
                "next": bookmark_list.next_num,
                "has_prev": bookmark_list.has_prev,
                "has_next": bookmark_list.has_next,


            }

        return jsonify({'data': data, 'meta': meta}), HTTP_200_OK


@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark(id):
    current_user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user_id, id=id).first()

    if not bookmark:
        return jsonify({'message': "Item not found"}), HTTP_404_NOT_FOUND

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
    }), HTTP_200_OK


@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def edit_bookmark(id):
    current_user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user_id, id=id).first()

    if not bookmark:
        return jsonify({'message': "Item not found"}), HTTP_404_NOT_FOUND

    body = request.json.get('body', '')
    url = request.json.get('url', '')

    if not validators.url(url):
        return jsonify({
            'error', 'Enter a valid url'
        }), HTTP_400_BAD_REQUEST
    
    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
    }), HTTP_200_OK


@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
    current_user_id = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user_id, id=id).first()

    if not bookmark:
        return jsonify({'message': "Item not found"}), HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()
    
    return jsonify({}), HTTP_204_NO_CONTENT


@bookmarks.get('/stats')
@jwt_required()
def get_stats():
    current_user_id = get_jwt_identity()
    data = []

    items = Bookmark.query.filter_by(user_id=current_user_id).all()

    for item in items:
        new_link = {
            "visits": item.visits,
            "url": item.url,
            "id": item.id,
            "short_url": item.short_url
        }

        data.append(new_link)

    return jsonify({"data": data}), HTTP_200_OK

