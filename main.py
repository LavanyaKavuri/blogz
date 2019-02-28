from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)  
app.secret_key= "test123"  




class Blog(db.Model):  

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120)) 
    body = db.Column(db.Text)
    owner_id=db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner): 
        self.title = title
        self.body = body
        self.owner = owner



class User(db.Model):                                         
    id = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,username , password):
        self.username =username
        self.password=password



@app.route('/login', methods=['POST', 'GET'])
def login():

    pwd_error=''
    username=''
    user_error=''
    if request.method=='POST':
        user1=request.form['user1'] 
        pwd1=request.form['pwd1']
        user=User.query.filter_by(user1=user1).first() 

       
        if user and user.password== password: 
            session['user1']=user1  
            flash('logged in '+user1)
                                         
            return redirect('/newpost') 

           
        elif user and user.password != password:
            pwd_error='Incorrect Password'

        else: 
            user_error='No User Exists'

    return render_template('login.html',pwd_error=pwd_error, user_error=user_error)




@app.route("/logout")  
def logout():
    
    session.clear()
    return redirect('/blog')  

  

def validate(fieldname, fieldval, fieldlen):
    msg = ''
    if (not fieldval) or (fieldval.strip() == "") or (" " in fieldval) or (fieldlen < 3) or (fieldlen > 20):
        msg = "Please enter a valid " + fieldname
    return msg



@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        user_name_length = len(username)
        password_length = len(password)
        username_error = validate("username", username, user_name_length)
        password_error = validate("password", password, password_length)
        confirmpassword_error = ''


        if not password == confirm_password or confirm_password.strip() == "":
            confirmpassword_error = "Passwords do not match"

        user=User.query.filter_by(username=username).first()
       

        if user is not None and user.username == username:
            username_error="User already exists"

        

        if not username_error and not password_error and not confirmpassword_error:
            new_user=User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username']=username
            flash('logged in '+username)
            return redirect('/newpost')
        else:
            return render_template('signup.html', username=username,
                                   username_error=username_error,
                                   password_error=password_error,
                                   confirmpassword_error=confirmpassword_error)
    return render_template('signup.html')


@app.route('/blog', methods=['GET'])
def blogdetails():

    blogid = request.args.get('id')
    test = request.args.get('user')
    
    if blogid is not None:
        blog = Blog.query.get(blogid)
        username=User.query.get(blog.owner_id) 
        return render_template('BlogEntryDetails.html', title=blog.title, body=blog.body,owner_id= username.username)
    if test is not None:
        user=User.query.filter_by(username=test).first()
        
        return render_template('singleUser.html', title="singleUser!", user=user)

    users = User.query.all()
    return render_template('blog.html', title="Build a blog!", users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    blog_title = ''
    blog_body = ''
    titleerror = ''
    bodyerror = ''

    existing_user= User.query.filter_by (username=session['username']).first()

    if request.method == 'POST':

        blog_title = request.form['title']
        blog_body = request.form['body']

        if (not blog_title) or (blog_title.strip() == ""):
            titleerror = "Please enter a valid Title for the blog"
        if (not blog_body) or (blog_body.strip() == ""):
            bodyerror = "Please enter a valid content for the blog"
        if titleerror or bodyerror:
            return render_template('newpost.html', blogtitle=blog_title, blogbody=blog_body, titleerror=titleerror,
                                   bodyerror=bodyerror, existing_user=existing_user)

        new_blog = Blog(blog_title, blog_body, owner)
        db.session.add(new_blog)
        db.session.commit()  
        return redirect('/blog?id=' + str(new_blog.id))  

    return render_template('newpost.html', blogtitle=blog_title, blogbody=blog_body, existing_user=existing_user)

@app.route('/')
def index():
    
    selected_username = request.args.get('user')
    users = []
    if selected_username is None:
        users=User.query.order_by(User.username).all()
        return render_template('index.html', title="Blogz", users=users)
    user=User.query.filter_by(username=selected_username).first()
    users.append(user)
    return render_template('blog.html', title="Blogz", users=users)




@app.before_request  
def require_login():
    print(request.endpoint)
    if request.endpoint == 'newpost' and not 'username' in session:
        return redirect("/login")


if __name__ == '__main__':
    app.run()