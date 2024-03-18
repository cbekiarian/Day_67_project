import datetime

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, Form, validators, HiddenField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date


'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)
# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class MyForm(FlaskForm):

    title    = StringField('Title', [validators.DataRequired()])
    subtitle = StringField('Subtitle' ,[validators.DataRequired()])
    author = StringField('Author',[validators.DataRequired()])
    img_url = StringField('Image URl',[validators.DataRequired(), validators.URL()])
    body = CKEditorField('Body',validators=[validators.DataRequired()])
    submit = SubmitField('Ok')

# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():

    # TODO: Query the database for all the posts. Convert the data to a python list.
    with app.app_context():
        all_posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.id)).scalars().all()
    posts = []

    for post in all_posts:
        dict = {}
        dict["id"] = post.id
        dict["title"] = post.title
        dict["subtitle"]  = post.subtitle
        dict["date"] = post.date
        dict["body"]  = post.body
        dict["author"]  = post.author
        dict["img_url"] = post.img_url
        posts.append(dict)

    return render_template("index.html", all_posts=posts)

# TODO: Add a route so that you can click on individual posts.
@app.route('/post/<post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    with app.app_context():
        requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()

    return render_template("post.html", post=requested_post)

@app.route("/new-post", methods=["GET","POST"])
def new_post():
    form = MyForm()

    if form.validate_on_submit():
        new_blog = BlogPost(

            title = form.title.data,
            subtitle = form.subtitle.data,
            author = form.author.data,
            body =form.body.data,
            img_url=form.img_url.data,
            date = datetime.date.today().strftime("%B %d,%Y"),
        )
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html",form =form, flag = 0)


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/edit-post/<int:post_id>", methods= ["GET","POST"])
def edit(post_id):

    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    # post = db.get_or_404(BlogPost, post_id)
    form = MyForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )

    # @app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
    # def edit(post_id):
    #     post = db.get_or_404(BlogPost, post_id)
    #     edit_form = MyForm(
    #         title=post.title,
    #         subtitle=post.subtitle,
    #         img_url=post.img_url,
    #         author=post.author,
    #         body=post.body
    #     )
    if form.validate_on_submit():

        post.title=form.title.data
        post.subtitle=form.subtitle.data
        post.author=form.author.data
        post.body=form.body.data
        post.img_url=form.img_url.data

        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=form, flag=1)
@app.route("/delete/<post_id>")
def delete(post_id):

    delete_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    db.session.delete(delete_post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

if __name__ == "__main__":
    app.run(debug=True, port=5003)
