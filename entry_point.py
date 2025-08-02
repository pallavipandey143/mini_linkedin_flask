from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db
from models import User, Post

app = Flask(__name__, template_folder='html_page')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('home.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if User.query.filter_by(email=email).first():
            flash("Email already exists!")
            return redirect(url_for('register'))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created!")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Logged in!")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out!")
    return redirect(url_for('login'))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    return render_template('profile.html', user=user, posts=posts)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        flash("Login required")
        return redirect(url_for('login'))

    if request.method == 'POST':
        content = request.form['content']
        new_post = Post(content=content, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
        flash("Post created!")
        return redirect(url_for('home'))
    return render_template('create_post.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
