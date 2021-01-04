from flask import Blueprint, flash, g, redirect, request, url_for
from flaskr.db import get_db
import os

bp = Blueprint('upload', __name__, url_prefix='/upload')


def up(_formname, db_operation, return_point):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(APP_ROOT, 'static/uploads/')
    if not os.path.isdir(target):
        os.mkdir(target)

    for upload in request.files.getlist(_formname):
        if upload is not None and upload != '':
            filename = upload.filename
            destination = "/".join([target, filename])
            upload.save(destination)

            db = get_db()
            db_operation(upload, db)
        else:
            flash('Image is required.')
            return return_point()


@bp.route('/new_ava', methods=('POST',))
def new_ava():
    def operation(upload, db):
        db.execute(
            'UPDATE user SET img = ?'
            ' WHERE id = ?',
            (upload.filename, g.user['id'])
        )
        db.commit()
        db.execute(
            'INSERT INTO images(img, user_id) VALUES(?, ?)',
            (upload.filename, g.user['id'])
        )
        db.commit()

    up('file', operation, lambda: redirect(url_for('profile.settings')))

    flash('New avatar')

    return redirect(url_for('profile.settings'))


@bp.route('/upload_file', methods=('POST',))
def upload_img_profile():
    def operation(upload, db):
        db.execute(
            'INSERT INTO images(img, user_id) VALUES(?, ?)',
            (upload.filename, g.user['id'])
        )
        db.commit()

    up('file_img', operation, lambda: redirect(url_for('profile.people', profile_id=g.user['id'])))

    flash('New images for profile')

    return redirect(url_for('profile.people', profile_id=g.user['id']))


@bp.route('/new_username', methods=('POST',))
def new_username():
    db = get_db()

    user = get_db().execute(
        'SELECT id'
        ' FROM user'
        ' WHERE username = ?',
        (request.form['username'],)
    ).fetchone()
    if user is not None:
        flash('Username is taken')
        return redirect(url_for('profile.settings'))

    db.execute(
        'UPDATE user SET username = ?'
        ' WHERE id = ?',
        (request.form['username'], g.user['id'])
    )
    db.commit()

    flash('New username profile')

    return redirect(url_for('profile.settings'))
