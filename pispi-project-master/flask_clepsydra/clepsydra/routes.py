import re

from flask import render_template, request, make_response, redirect, url_for, json, session, flash, jsonify

from . import app, db, cache
from .forms import LoginForm, RegisterForm, CommentForm, PostForm, DeleteComment, Reply  # user form, comment form
from .models import User, Article, Comments  # database models
from .survey_calc import *


# Returns a boolean variable if the current user in the session is the admin or not that can be used in all of the
# html files.
@app.context_processor
def is_admin():
    if current_user() is None:
        return dict(is_admin=False)
    elif current_user().admin == 1:
        return dict(is_admin=True)

    return dict(is_admin=False)


@app.context_processor
def get_username():
    if current_user() is None:
        return dict(the_username=False)
    return dict(the_username=current_user().username)


# Removes html tags from previews.
TAG_RE = re.compile(r'<[^>]+>')


# Setting a function for the above functionality in order to be able to pass it in the template rendering.
def remove_tags(text):
    return TAG_RE.sub('', text)


# Route to the home page of the site. Selects two of the most recent articles of each category and displays them.
@app.route("/")
def frontpage():
    industry_articles = Article.query.order_by(Article.date_posted.desc()).filter_by(category='Industry').limit(2).all()
    personal_articles = Article.query.order_by(Article.date_posted.desc()).filter_by(category='Personal').limit(2).all()
    return render_template("home.html", industry_articles=industry_articles, personal_articles=personal_articles,
                           my_function=remove_tags)


# Routes to a page where every article of the Industry Effects category is displayed.
@app.route("/industry_effects")
def industry():
    articles = Article.query.order_by(Article.date_posted.desc()).filter_by(category='Industry').all()
    return render_template("category_industry_impact.html", articles=articles, my_function=remove_tags)


# Routes to a page where every article of the Personal Impact category is displayed.
@app.route("/personal_impact")
def personal():
    articles = Article.query.order_by(Article.date_posted.desc()).filter_by(category='Personal').all()
    return render_template("category_personal_impact.html", articles=articles, my_function=remove_tags)


# This function finds all comments in one article and returns these in format for display.
def find_parents(article_id):
    all_comments = dict()

    for comment in Comments.query.filter_by(parent=None).filter_by(article_id=article_id).order_by(
            Comments.date_posted.desc()):
        kids = []
        replies_to_parent = Comments.nested_comments(comment, kids)
        all_comments.update({comment: replies_to_parent})
    return all_comments


# Routes to the article depending on the article id or the article title to accommodate the function of searching.
@app.route("/article/<int:article_id>", methods=['GET', 'POST'])
@app.route("/article/<int:article_id>/<string:error_message>", methods=['GET', 'POST'])
@app.route("/article/<article_descr>", methods=['GET', 'POST'])
def article(article_id=None, error_message=None, article_descr=None):
    the_article = ""
    if article_id is not None:
        Article.query.get_or_404(article_id)
    user_id = None
    # Init the forms
    is_logged_in = current_user()
    delete_form = DeleteComment()
    add_comment = CommentForm()
    reply_form = Reply(meta={'csrf': False})
    # Check if the article is posted from admin
    if article_descr is not None:
        the_article = Article.query.filter_by(title=article_descr).one()
    else:
        the_article = Article.query.filter_by(id=article_id).one()
    # if request method is POST then the user try to interact with the forms. Check which form submitted
    if request.method == 'POST':
        if add_comment.submit1.data:  # comment form check
            if add_comment.validate():
                if is_logged_in:
                    add_comment.add_comment(current_user(), the_article.id)
                    return redirect(url_for('article', article_descr=article_descr, article_id=article_id))
                else:
                    return redirect(url_for('login', message='Please login first'))  # redirect to login page if no
                    # one is on session
            else:
                add_comment.comment1.data = ''
                error_message = 'Maximum limit allowed is 450 characters'  # redirect and display error message
                return redirect(
                    url_for('article', error_message=error_message, article_descr=article_descr, article_id=article_id))
            # reply form check
        if reply_form.reply.data:
            if reply_form.validate():
                if is_logged_in:
                    reply_form.add_reply(current_user(), int(reply_form.parent.data), the_article.id)
                    return redirect(url_for('article', article_descr=article_descr, article_id=article_id))
                else:
                    return redirect(url_for('login', message='Please login first'))
            else:
                reply_form.comment2.data = ''
                error_message = 'Maximum limit allowed is 450 characters'  # if not pass the validate() redirect with
                # error
                return redirect(
                    url_for('article', error_message=error_message, article_descr=article_descr, article_id=article_id))

        if delete_form.submit2.data and delete_form.hidden.data:  # delete form
            if is_logged_in and is_admin().get('is_admin'):
                Comments.delete_comment(comment_id=int(delete_form.hidden.data))
                return redirect(url_for('article', article_descr=article_descr, article_id=article_id))

    if current_user():  # check if current user is not none
        user_id = current_user().id
    parent_comment = find_parents(the_article.id)
    return render_template("article.html", article=the_article, form=add_comment, csform=reply_form,
                           parent_comment=parent_comment, dform=delete_form,
                           current_user_id=user_id, error_message=error_message)


# Takes as a parameter the form object and saves the file in the specified path
def save_image(form_image):
    image_path = os.path.join(app.root_path, 'static/resources/hero_images',
                              form_image.filename)  # building the desired path
    form_image.save(image_path)  # saving in the path
    return form_image.filename


# Route to a form that allows only the admin to make a new post
@app.route("/post_article", methods=['GET', 'POST'])
def new_article():
    form = PostForm()
    if form.validate_on_submit():
        flash('Article created successfully')
        image_file = 'default.jpg'
        if form.image.data:  # if the user has uploaded an image then it saves it otherwise the default.jpg is used.
            image_file = save_image(form.image.data)
        # Creating and saving the article in the database according to the form values.
        post = Article(title=form.title.data, subtitle=form.subtitle.data, author=form.author.data,
                       category=form.category.data, image=image_file, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("frontpage"))
    # Only allows the admin to access the page otherwise it redirects to the homepage
    if current_user() is not None and current_user().admin == 1:
        return render_template("post_article.html", form=form, legend="Create")
    else:
        return redirect(url_for("frontpage"))


# Route to a form that allows only the admin to update an existing post.
@app.route("/article/<int:article_id>/update_article", methods=['GET', 'POST'])
def update_article(article_id):
    article = Article.query.get_or_404(article_id)  # if the article does not exist then it throws error.
    if current_user() is None or current_user().admin != 1:
        return redirect(
            url_for('frontpage'))  # redirects the non-admin user to the home page if he tries to access the url
    form = PostForm()
    if form.validate_on_submit():  # if the submission of the form is valid it updates the values of the article object
        article.title = form.title.data
        article.subtitle = form.subtitle.data
        article.author = form.author.data
        article.category = form.category.data
        if form.image.data:  # if the user has uploaded an image then it saves it otherwise the previous one is used
            article.image = save_image(form.image.data)

        article.content = form.content.data
        db.session.commit()
        return redirect(url_for('article', article_id=article.id))  # redirects to the updated article
    elif request.method == 'GET':  # if the request method is GET then it populates the form fields with the
        # established values of the article object
        form.title.data = article.title
        form.subtitle.data = article.subtitle
        form.author.data = article.author
        form.category.data = article.category
        form.image.data = article.image
        form.content.data = article.content
    return render_template("post_article.html", form=form,
                           legend="Update")  # uses the same template as the post_article one


# Route that allows only the admin to delete an existing post and redirects him to the frontpage.
@app.route("/article/<int:article_id>/delete_article", methods=['GET', 'POST'])
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)  # if the article does not exist then it throws error.
    if current_user() is None or current_user().admin != 1:
        return redirect(url_for('frontpage'))
    # the article is deleted only if the above condition is passed
    all_comments = find_parents(article_id)
    for parent in all_comments.keys():  # find all comments in this article and delete them
        Comments.delete_comment(comment_id=parent.id)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('frontpage'))


@app.route("/user_profile", methods=['GET', 'POST'])
def user_profile():
    if current_user():
        image_file = url_for("static", filename="resources/user_images/" + current_user().image_file)

        if current_user().cat1_number is not None:

            all_results = current_user().cat1_number + current_user().cat2_number + current_user().cat3_number + current_user().cat4_number

            return render_template("user_profile.html",
                                   user=current_user(),
                                   image_file=image_file,
                                   all_results=all_results, survey_done=True)
        else:
            return render_template("user_profile.html",
                                   user=current_user(),
                                   image_file=image_file, survey_done=False)

    return redirect("/login")


# SURVEY AND SURVEY JSON

@app.route('/survey', methods=["GET", "POST"])
def survey():
    if current_user() is None:
        return redirect("login")
    else:
        if request.method == "POST":
            # Pass survey results to user
            data = request.get_json()
            results = calc_survey_results(data)

            current_user().cat1_number = results[0]
            current_user().cat2_number = results[1]
            current_user().cat3_number = results[2]
            current_user().cat4_number = results[3]
            db.session.commit()

            return redirect(url_for("user_profile"))

        return create_survey_response()


# Cache result of html page response for survey, because the questions change from the survey.json file.
@cache.cached(timeout=0, key_prefix='create_survey_response')
def create_survey_response():
    site_root = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(site_root, "static/survey", "survey.json")
    with open(json_url, 'r', encoding='utf8') as survey_file:
        survey_data = json.load(survey_file)
        return make_response(render_template('survey.html', survey=survey_data))


#  /SURVEY

#           START OF USER MANIPULATIONS. LOGIN, SIGN-UP, SIGN-OUT, GET CURRENT_USER


@app.route('/login', methods=["POST", "GET"])  # normal login route
@app.route("/login/<string:message>", methods=["POST", "GET"])  # login with message (from sign_up)
def login(message=None):
    login_form = LoginForm(meta={'csrf': False})
    message = message  # message to be shown in view
    if request.method == 'POST':
        u = User.query.filter_by(email=login_form.email.data).filter_by(password=login_form.password.data).first()
        if u is not None:
            session['userID'] = str(u.id)  # store user id in encrypted session
            session.permanent = True  # will expire after a month
            return redirect(url_for('frontpage'))  # go to frontpage
        else:
            message = "Please try again"

    return render_template("login.html", form=login_form, error=message,
                           type=1)  # render login if get-request or credentials wrong, type=1 for login


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    sign_up_form = RegisterForm(meta={'csrf': False})
    error = None
    if request.method == 'POST':
        username = sign_up_form.username.data
        email = sign_up_form.email.data
        password = sign_up_form.password.data
        if username == "" or email == "" or password == "":
            error = "Please fill the fields"
        else:
            user = User(username=username, email=email, password=password, admin=0)
            db.session.add(user)
            try:
                db.session.commit()
                return redirect(url_for('login', message="Account successfully created"))  # return to the login screen
            except:
                db.session.rollback()
                error = "Error saving user"

    return render_template("login.html", form=sign_up_form, error=error, type=2)  # type=2 is for sign_up


@app.route('/sign_out', methods=['POST', 'GET'])
def sign_out():
    if 'userID' in session:
        session.pop('userID')
    return redirect(url_for('frontpage'))  # go to frontpage (MAY NEED CHANGE -alex)


def current_user():  # returns a user if stored in sessions of else returns None
    if "userID" not in session:
        return None
    return User.query.get(session['userID'])


#           END OF USER MANIPULATIONS


@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    found_articles = Article.query.msearch(query, fields=['title'], limit=20)
    search_results = []

    for result in found_articles:
        search_results.append(result.title)

    return jsonify(matching_results=search_results)
