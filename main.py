from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] =True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:1234@localhost:8889/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "jhyboadnun"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    
    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/blog")
def blog_page():
    posts = Blog.query.all()
    
    if request.method == 'GET': 
        if 'id' in request.args:
            post_id = request.args.get('id')
            content = Blog.query.get(post_id)
            return render_template('blog_page.html', content = content)

    return render_template('index.html', title="Blog Post",
              posts = posts)

@app.route("/newpost")
def post():
    return render_template("newpost.html")

def is_blank(resp):
    if len(resp) == 0:
        return True
    else:
        return False     


@app.route("/newpost", methods=["POST"])
def new_post():
    title = request.form['title']
    body = request.form["body"]

    title_error = ""
    body_error = ""

    if is_blank(title):
        title_error = "Empty Field"

    if is_blank(body):
        body_error = "Empty Field"

    if not title_error and not body_error:
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()
        page_id = new_post.id
        return redirect("/blog?id={0}".format(page_id))

    else:
        return render_template("newpost.html",
            title = title,
            body = body,
            title_error = title_error,
            body_error = body_error
            )

if __name__ == '__main__':
    app.run()    