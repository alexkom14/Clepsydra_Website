from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, HiddenField, RadioField, FileField
from wtforms.validators import DataRequired, Length

from .models import Comments
from . import db


class LoginForm(FlaskForm):
    email = StringField(render_kw={"placeholder": "Email"})
    password = PasswordField(render_kw={"placeholder": "Password"})


# The CommentForm class is used to the base form in template and it adds a comment in the current article
class CommentForm(FlaskForm):
    some_hidden_field = HiddenField()
    comment1 = TextAreaField(validators=[DataRequired(),
                                         Length(min=1, max=450)])
    submit1 = SubmitField(label='Submit')

    def add_comment(self, user, article):
        comment2 = Comments(article_id=article, likes=0, username=user.username, user_id=user.id,
                            comment=self.comment1.data)

        db.session.add(comment2)
        try:
            db.session.commit()
        except:
            db.session.rollback()


class DeleteComment(FlaskForm):
    hidden = HiddenField()
    submit2 = SubmitField(label='Delete')


# This class represents the reply form for nested comments, in hiddenField we pass the parent comment and in
# add_reply it save the comment to database
class Reply(FlaskForm):
    parent = HiddenField()
    comment2 = TextAreaField(validators=[DataRequired(),
                                         Length(min=1, max=450)])
    reply = SubmitField(label='Submit')

    def add_reply(self, user, parent_comment, article):
        reply = Comments(comment=self.comment2.data, article_id=article, likes=0, user_id=user.id,
                         username=user.username, parent_id=parent_comment)
        db.session.add(reply)
        try:
            db.session.commit()
        except:
            db.session.rollback()


class RegisterForm(FlaskForm):
    username = StringField(render_kw={"placeholder": "Username"})
    email = StringField(render_kw={"placeholder": "Email"})
    password = PasswordField(render_kw={"placeholder": "Password"})


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle")
    author = StringField("Author", validators=[DataRequired()])
    category = RadioField("Category", choices=[("Industry", "Industry Effects"), ("Personal", "Personal Impact")],
                          validators=[DataRequired()])
    image = FileField('Hero Image', validators=[FileAllowed(['jpg', 'png'])])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post Article")
