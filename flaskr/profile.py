from flask import Blueprint, flash, g, redirect, render_template, request, url_for, make_response
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/settings', methods=('GET', 'POST'))
def settings():
    return render_template('profile/settings.html')


@bp.route('/<int:profile_id>', methods=('GET', 'POST'))
def people(profile_id):
    db = get_db()

    if g.user is None:
        g.user = db.execute(
            'SELECT * FROM user WHERE id = 1 and username = "guest"'
        ).fetchone()

    profile_info = db.execute(
        'SELECT id, username, img FROM user WHERE id = ?',
        (profile_id,)
    ).fetchall()

    if not profile_info:
        abort(404, 'User is not Found')

    profile_count_posts = db.execute(
        'SELECT COUNT(*) FROM post WHERE author_id = ?',
        (profile_id,)
    ).fetchone()

    user_posts = db.execute(
        'SELECT p.id, p.img as post_img, title, body, created, author_id, username, u.img as user_img, u.id as user_id,'
        ' p.quote_body as quote_body, p.quote_footer as quote_footer'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.author_id = ? ORDER BY created DESC',
        (profile_id,)
    ).fetchall()

    user_imgs = db.execute(
        'SELECT img, (SELECT COUNT(*) FROM images WHERE user_id = ?) as count_img FROM images WHERE user_id = ?',
        (profile_id, profile_id)
    ).fetchall()

    favorite_count = db.execute(
        'SELECT COUNT(user.id) as favorite_count'
        ' FROM user, favorites'
        ' WHERE favorites.favorite_id = user.id AND favorites.user_id = ?',
        (profile_id,)
    ).fetchone()

    follower_count = db.execute(
        'SELECT COUNT(user.id) as follower_count'
        ' FROM user, followers'
        ' WHERE followers.follower_id = user.id AND followers.user_id = ?',
        (profile_id,)
    ).fetchone()

    is_favorite = None
    if g.user['id'] != profile_id:
        is_favorite = db.execute(
            'SELECT id'
            ' FROM favorites'
            ' WHERE favorites.favorite_id = ? AND favorites.user_id = ?',
            (profile_id, g.user['id'])
        ).fetchone()
        if is_favorite is not None:
            is_favorite = 'delete'

    return render_template('profile/profile.html', profile_info=profile_info, profile_count_posts=profile_count_posts,
                           posts=user_posts, user_imgs=user_imgs, favorite_count=favorite_count['favorite_count'],
                           is_favorite=is_favorite, follower_count=follower_count['follower_count'])


@bp.route('/favorite', methods=('GET', 'POST'))
def favorite():
    db = get_db()
    favorite_list = db.execute(
        'SELECT user.id, user.username, user.img'
        ' FROM user, favorites'
        ' WHERE favorites.favorite_id = user.id AND favorites.user_id = ?',
        (g.user['id'],)
    ).fetchall()

    return render_template('profile/favorite.html', favorite_list=favorite_list)


@bp.route('/<int:profile_id>/add', methods=('GET',))
def add_favorite(profile_id):
    db = get_db()
    db.execute(
        'INSERT INTO favorites(user_id, favorite_id) VALUES(?, ?)',
        (g.user['id'], profile_id)
    )
    db.commit()

    db.execute(
        'INSERT INTO followers(user_id, follower_id) VALUES(?, ?)',
        (profile_id, g.user['id'])
    )
    db.commit()

    flash('Profile added to favorites list.')

    return redirect(url_for('profile.people', profile_id=profile_id))


@bp.route('/<int:profile_id>/delete/<int:to_page>', methods=('GET',))
def delete_favorite(profile_id, to_page):
    db = get_db()
    db.execute(
        'DELETE FROM favorites WHERE user_id = ? AND favorite_id = ?',
        (g.user['id'], profile_id)
    )
    db.commit()

    db.execute(
        'DELETE FROM followers WHERE user_id = ? AND follower_id = ?',
        (profile_id, g.user['id'])
    )
    db.commit()

    flash('Profile removed from favorites list.')

    if to_page == 1:
        return redirect(url_for('profile.favorite'))
    else:
        return redirect(url_for('profile.people', profile_id=profile_id))

