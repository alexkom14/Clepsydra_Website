from datetime import datetime

from . import db


class User(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), index=True, unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='avatar.png')
    password = db.Column(db.String(80), unique=False, nullable=False)
    admin = db.Column(db.Integer)

    cat1_number = db.Column(db.Float)
    cat2_number = db.Column(db.Float)
    cat3_number = db.Column(db.Float)
    cat4_number = db.Column(db.Float)

    def __repr__(self):
        return f"User('{self.username}, {self.email}, {self.image_file}, {self.admin}, " \
               f"{self.cat1_number}, {self.cat2_number}, {self.cat3_number}, {self.cat4_number}')"


class Comments(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    date_posted = db.Column(db.DateTime(), nullable=False, index=True, default=datetime.utcnow)
    likes = db.Column(db.Integer, nullable=False, default=0)
    comment = db.Column(db.Text(450), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

    replies = db.relationship(
        'Comments', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic')

    def get_parent_username(self):
        parent_comment = Comments.query.filter_by(id=self.parent_id).first()
        return parent_comment.username

    @staticmethod  # delete all comments under this parent and the parent
    def delete_comment(comment_id):
        kids = []
        selected_comment = Comments.query.filter_by(id=comment_id).first()
        comments_for_delete = Comments.nested_comments(selected_comment, kids)
        comments_for_delete.append(selected_comment)
        for i in comments_for_delete:
            db.session.delete(i)
            try:
                db.session.commit()
            except:
                db.session.rollback()

    @staticmethod  # find all nested comments to this parent
    def nested_comments(comment, kids):
        for reply in comment.replies:
            kids.append(reply)
            Comments.nested_comments(reply, kids)
        return kids


class Article(db.Model):
    __tablename__ = "article"
    __searchable__ = "title"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(100), nullable=False, default='default.jpg')
    comments = db.relationship('Comments', backref='all_comments', lazy=True)
    author = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Post('{self.title, self.comments}')"
