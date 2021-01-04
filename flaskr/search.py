from flask import Blueprint, render_template, request
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('search', __name__)


@bp.route('/search', methods=('GET', 'POST'))
def search():

    if request.method == 'POST':
        db = get_db()

        _type = request.form['_type']

        if _type == 'post':
            post_name = request.form['search']
            result_posts = db.execute(
                'SELECT p.id, p.img as post_img, title, body, created, author_id, username, u.img as user_img, u.id as user_id,'
                ' p.quote_body as quote_body, p.quote_footer as quote_footer'
                ' FROM post p JOIN user u ON p.author_id = u.id'
                ' WHERE p.title = ?'
                ' ORDER BY created DESC',
                (post_name,)
            ).fetchall()

            if result_posts is None:
                abort(404, "Posts name {0} doesn't exist.".format(post_name))

            return render_template('search/search_single.html', posts=result_posts)

        elif _type == 'people':
            people_name = request.form['search']
            result_people = db.execute(
                'SELECT username, img FROM user WHERE username = ?',
                (people_name,)
            ).fetchall()
            return render_template('search/search_single.html', people=result_people)

    return render_template('search/search_single.html')
