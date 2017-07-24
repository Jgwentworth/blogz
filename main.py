from flask import Flask, request, redirect, render_template, session
from hashutils import check_pw_hash
from app import app, db
from models import User, Blog
import string

app.secret_key = "jhyboadnun"

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', "blog_page", "index"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")

@app.route("/blog")
def blog_page():
    posts = Blog.query.all()
    user = User.query.all()
    
    if "userid" in request.args:
        author = request.args.get("userid")
        content = Blog.query.filter_by(owner_id=author).all()
        user = User.query.filter_by(id=author).first()
        return render_template('blog_page.html', content = content, user=user)

    if "id" in request.args:
        post = request.args.get("id")
        content = Blog.query.filter_by(id=post).first()
        author = content.owner_id
        user = User.query.filter_by(id=author).first()
        return render_template("single_post.html", content=content, user=user)

    return render_template('blog_list.html', title="Blog Post",
              posts = posts, user=user)

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
    authors = User.query.all()

    return render_template('index.html', authors = authors)

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

        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')
        # TODO need to fix this
        #if not user:
            #username = ""
            #user_error = "Incorrect Username or User doesn't exist"
        #if password != user.password:
            #password = ""
            #pass_error = "Incorrect Password"    
        else:
            user_error = "Incorrect Username or User doesn't exist"
            pass_error = "Incorrect Password"
            username = ""
            password = ""
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