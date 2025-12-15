from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Contact {self.name}>'

# Create tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    user_count = User.query.count()
    return render_template('home.html', title='Home', user_count=user_count)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        
        flash(f'Thank you {name}! Your message has been received.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', title='Contact')

@app.route('/users')
def users():
    all_users = User.query.order_by(User.date_created.desc()).all()
    return render_template('users.html', title='Users', users=all_users)

@app.route('/users/add', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    
    if not username or not email:
        flash('Username and email are required!', 'error')
        return redirect(url_for('users'))
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash(f'Username {username} already exists!', 'error')
        return redirect(url_for('users'))
    
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        flash(f'Email {email} already exists!', 'error')
        return redirect(url_for('users'))
    
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    
    flash(f'User {username} added successfully!', 'success')
    return redirect(url_for('users'))

@app.route('/users/delete/<int:id>')
def delete_user(id):
    user = User.query.get_or_404(id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User {username} deleted successfully!', 'success')
    return redirect(url_for('users'))

@app.route('/messages')
def messages():
    all_messages = Contact.query.order_by(Contact.date_sent.desc()).all()
    return render_template('messages.html', title='Messages', messages=all_messages)

@app.route('/api/users')
def api_users():
    all_users = User.query.all()
    users_list = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'date_created': user.date_created.strftime('%Y-%m-%d %H:%M:%S')
    } for user in all_users]
    return jsonify(users_list)

@app.route('/api/stats')
def api_stats():
    stats = {
        'total_users': User.query.count(),
        'total_messages': Contact.query.count(),
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify(stats)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', title='404 - Page Not Found'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
