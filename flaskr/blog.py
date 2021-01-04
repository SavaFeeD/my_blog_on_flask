import random
import string

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from flaskr.upload import up

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, p.img as post_img, title, body, created, author_id, username, u.img as user_img, u.id as user_id,'
        ' p.quote_body as quote_body, p.quote_footer as quote_footer'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    return render_template('blog/select_type_create.html')


@bp.route('/create/type_complex', methods=('GET', 'POST'))
@login_required
def create_type_complex():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        quote_body = request.form['quote-body']
        quote_footer = request.form['quote-footer']

        complex_token = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))

        db = get_db()

        db.execute(
            'INSERT INTO post(author_id, complex_token, _type) VALUES(?, ?, "complex")',
            (g.user['id'], complex_token)
        )
        db.commit()

        def operation(upload, db):
            db.execute(
                'UPDATE post SET img = ?'
                ' WHERE complex_token = ? AND author_id = ?',
                (upload.filename, complex_token, g.user['id'])
            )
            db.commit()

        up('image', operation, url_for('blog.create_type_image'))

        if title is not None:
            db.execute(
                'UPDATE post SET title = ?'
                ' WHERE complex_token = ? AND author_id = ?',
                (title, complex_token, g.user['id'])
            )
            db.commit()

        if body is not None:
            db.execute(
                'UPDATE post SET body = ?'
                ' WHERE complex_token = ? AND author_id = ?',
                (body, complex_token, g.user['id'])
            )
            db.commit()

        if quote_body is not None and quote_footer is not None:
            db.execute(
                'UPDATE post SET quote_body = ?, quote_footer = ?'
                ' WHERE complex_token = ? AND author_id = ?',
                (quote_body, quote_footer, complex_token, g.user['id'])
            )
            db.commit()

        return redirect(url_for('index'))

    return render_template('blog/create_t-complex.html')


@bp.route('/create/type_quote', methods=('GET', 'POST'))
@login_required
def create_type_quote():
    if request.method == 'POST':
        quote_body = request.form['quote-body']
        quote_footer = request.form['quote-footer']

        error = [None]

        if not quote_body:
            if error[0] is None:
                error[0] = 'Body is required.'
            else:
                error.append('Body is required.')

        if not quote_footer:
            if error[0] is None:
                error[0] = 'Quote is required.'
            else:
                error.append('Quote is required.')

        if error[0] is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post(author_id, quote_footer, quote_body, _type) VALUES(?, ?, ?, "quote")',
                (g.user['id'], quote_footer, quote_body)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('blog/create_t-quote.html')


@bp.route('/create/type_image', methods=('GET', 'POST'))
@login_required
def create_type_image():
    if request.method == 'POST':
        title = request.form['title']

        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            def operation(upload, db):
                _title = request.form['title']

                db.execute(
                    'INSERT INTO post(author_id, img, title, _type) VALUES(?, ?, ?, "image")',
                    (g.user['id'], upload.filename, _title)
                )
                db.commit()

            up('image', operation, url_for('blog.create_type_image'))
            return redirect(url_for('index'))

    return render_template('blog/create_t-image.html')


@bp.route('/create/type_text', methods=('GET', 'POST'))
@login_required
def create_type_text():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = [None]

        if not title:
            if error[0] is None:
                error[0] = 'Title is required.'
            else:
                error.append('Title is required.')

        if not body:
            if error[0] is None:
                error[0] = 'Text is required.'
            else:
                error.append('Text is required.')

        if error[0] is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, _type)'
                ' VALUES (?, ?, ?, "text")',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create_t-text.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

