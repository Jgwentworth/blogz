from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] =True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:blogz123@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "jhyboadnun"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', "blog_page", "index"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

@app.route("/blog")
def blog_page():
    posts = Blog.query.all()
    
    if request.method == 'GET': 
        if 'id' in request.args:
            post_id = request.args.get('id')
            content = Blog.query.get(post_id)
            return render_template('blog_page.html', content = content)

    return render_template('blog_list.html', title="Blog Post",
              posts = posts)

@app.route("/newpost")
def post():
    return render_template("newpost.html")

def is_blank(resp):
    if len(resp) == 0:
        return True
    else:
        return False   
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]

        user_error = ""
        pass_error = ""
        verify_error = ""

        empty = ""

        existing_user = User.query.filter_by(username=username).first()
        if username == empty:
            user_error = "Empty Field"
        elif len(username) < 3 or len(password) > 20: 
            user_error = "Invalid username (3-20) characters"
        else: 
            if existing_user:
                user_error = "Existing User"
                username = ""
        if password == empty:
            pass_error = "Empty Field"
        else:
            if len(password) < 3 or len(password) > 20:
                pass_error = "Invalid password (3-20) characters"
                password = ""
        if verify == empty:
            verify_error = "Empty Field"
        else:
            if len(verify) < 3 or len(verify) > 20:
                verify_error = "Invalid password (3-20) characters"
                verify = ""
        if verify != password:
            verify_error = "Passwords do not match"
            verify = ""                   
        if not user_error and not pass_error and not verify_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect("/newpost")
        else:
            return render_template("signup.html",
                username = username,
                user_error = user_error,
                password = password,
                pass_error = pass_error,
                verify = verify,
                verify_error = verify_error
        )
    return render_template("signup.html") 

@app.route("/login", methods=["POST", "GET"] )
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user =  User.query.filter_by(username=username).first()

        pass_error = ""
        user_error = ""

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        if not user:
            username = ""
            user_error = "Incorrect Username"
        if password != user.password:
            password = ""
            pass_error = "Incorrect Password"    
        else:
            return render_template("login.html",
                username = username,
                password = password,
                user_error = user_error,
                pass_error = pass_error      
        )    

    return render_template("login.html")

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/blog')   

@app.route("/newpost", methods=["POST"])
def new_post():
    title = request.form['title']
    body = request.form["body"]
    owner = User.query.filter_by(username=session['username']).first()
    title_error = ""
    body_error = ""

    if is_blank(title):
        title_error = "Empty Field"

    if is_blank(body):
        body_error = "Empty Field"

    if not title_error and not body_error:
        new_post = Blog(title, body, owner)
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