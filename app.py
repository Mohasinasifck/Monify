from flask import Flask, render_template, redirect, url_for, flash, request, make_response, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import csv
from io import StringIO
from functools import wraps
from sqlalchemy import func
import secrets
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def get_id(self):
        return f"admin_{self.id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    icon = db.Column(db.String(50), default="fas fa-tag")  # NEW
    color = db.Column(db.String(7), default="#667eea")     # NEW
    expenses = db.relationship('Expense', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Expense {self.description}: {self.amount}>'

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    monthly_limit = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    category = db.relationship('Category', backref='budget', uselist=False)

    def __repr__(self):
        return f'<Budget {self.category.name}: {self.monthly_limit}>'

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reset_tokens')

    @staticmethod
    def generate_token():
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def __repr__(self):
        return f'<PasswordResetToken {self.token}>'

# Forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match.')
    ])
    agree_terms = BooleanField('I agree to the Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField('Create Account')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    date = StringField('Date', default=datetime.today().strftime('%Y-%m-%d'), validators=[DataRequired()])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Expense')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=50)])
    icon = SelectField('Icon', choices=[
        ('fas fa-utensils', '🍽️ Food & Dining'),
        ('fas fa-car', '🚗 Transportation'),
        ('fas fa-home', '🏠 Home & Utilities'),
        ('fas fa-shopping-cart', '🛒 Shopping'),
        ('fas fa-gamepad', '🎮 Entertainment'),
        ('fas fa-heartbeat', '💊 Healthcare'),
        ('fas fa-graduation-cap', '🎓 Education'),
        ('fas fa-plane', '✈️ Travel'),
        ('fas fa-dumbbell', '💪 Fitness'),
        ('fas fa-coffee', '☕ Coffee & Drinks'),
        ('fas fa-gas-pump', '⛽ Gas & Fuel'),
        ('fas fa-phone', '📱 Phone & Internet'),
        ('fas fa-tag', '🏷️ General')
    ], default='fas fa-tag')
    color = SelectField('Color', choices=[
        ('#667eea', '🔵 Blue'),
        ('#28a745', '🟢 Green'), 
        ('#dc3545', '🔴 Red'),
        ('#ffc107', '🟡 Yellow'),
        ('#6f42c1', '🟣 Purple'),
        ('#fd7e14', '🟠 Orange'),
        ('#20c997', '🟢 Teal'),
        ('#e83e8c', '🩷 Pink'),
        ('#6c757d', '⚫ Gray'),
        ('#17a2b8', '🔵 Cyan')
    ], default='#667eea')
    submit = SubmitField('Add Category')


class BudgetForm(FlaskForm):
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    monthly_limit = FloatField('Monthly Budget Limit (₹)', validators=[DataRequired()])
    submit = SubmitField('Set Budget')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

# Admin Forms
class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Admin Login')

class CreateAdminForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    is_super_admin = BooleanField('Super Admin')
    submit = SubmitField('Create Admin')

class AdminResetUserPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Reset User Password')

from datetime import datetime, timedelta

class RecurringExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    frequency = db.Column(db.String(20), nullable=False, default='monthly')
    next_due_date = db.Column(db.Date, nullable=False)
    auto_add = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_processed = db.Column(db.Date)
    
    category = db.relationship('Category', backref='recurring_expenses')
    user = db.relationship('User', backref='recurring_expenses')

    def get_next_due_date(self):
        """Calculate next due date based on frequency"""
        if self.frequency == 'daily':
            return self.next_due_date + timedelta(days=1)
        elif self.frequency == 'weekly':
            return self.next_due_date + timedelta(weeks=1)
        elif self.frequency == 'monthly':
            next_month = self.next_due_date.month + 1
            next_year = self.next_due_date.year
            if next_month > 12:
                next_month = 1
                next_year += 1
            try:
                return datetime(next_year, next_month, self.next_due_date.day).date()
            except ValueError:
                return datetime(next_year, next_month, 28).date()
        elif self.frequency == 'yearly':
            return datetime(self.next_due_date.year + 1, self.next_due_date.month, self.next_due_date.day).date()
        return self.next_due_date


class RecurringExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()], 
                            render_kw={"placeholder": "e.g., Netflix Subscription, Rent, Insurance"})
    amount = FloatField('Amount (₹)', validators=[DataRequired()], 
                       render_kw={"placeholder": "0.00"})
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[
        ('monthly', '📅 Monthly'),
        ('weekly', '📆 Weekly'),
        ('daily', '🔄 Daily'),
        ('yearly', '🗓️ Yearly')
    ], default='monthly')
    next_due_date = StringField('Next Due Date', 
                               default=datetime.today().strftime('%Y-%m-%d'), 
                               validators=[DataRequired()],
                               render_kw={"type": "date"})
    auto_add = BooleanField('Auto-add to expenses', default=False)
    submit = SubmitField('Create Recurring Expense')


# Admin decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('Access denied. Admin login required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin) or not current_user.is_super_admin:
            flash('Access denied. Super Admin privileges required.', 'danger')
            return redirect(url_for('admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/reset-db')
def reset_database():
    """Recreate database with new schema - USE WITH CAUTION!"""
    db.drop_all()
    db.create_all()
    
    # Create default admin
    admin = Admin(
        username='superadmin',
        email='admin@monify.ai',
        is_super_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    return "Database reset successfully! Admin: admin@monify.ai / admin123"


# User loader
@login_manager.user_loader
def load_user(user_id):
    # Check if it's an admin session
    if user_id.startswith('admin_'):
        admin_id = user_id.replace('admin_', '')
        return Admin.query.get(int(admin_id))
    else:
        return User.query.get(int(user_id))

# Context processor for current year
@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

@app.route('/')
def home():  # Change back from 'landing' to 'home'
    # Always show landing page regardless of authentication
    return render_template('home.html')

@app.route('/home')
@login_required  
def dashboard():  # Keep this as dashboard 
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('expenses'))




@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and isinstance(current_user, User):
        return redirect(url_for('home'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Create default categories for new user
        default_categories = ['Food', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Other']
        for cat_name in default_categories:
            category = Category(name=cat_name, user_id=user.id)
            db.session.add(category)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and isinstance(current_user, User):
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Create reset token
            token = PasswordResetToken(
                user_id=user.id,
                token=PasswordResetToken.generate_token(),
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            db.session.add(token)
            db.session.commit()
            
            # In a real app, you'd send an email here
            reset_url = url_for('reset_password', token=token.token, _external=True)
            flash(f'Password reset link: {reset_url}', 'info')
            flash('Check the above link to reset your password (expires in 1 hour)', 'warning')
        else:
            flash('If that email address is in our system, we have sent you a password reset link.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('auth/forgot_password.html', form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()
    
    if not reset_token or reset_token.is_expired():
        flash('Invalid or expired password reset token.', 'danger')
        return redirect(url_for('forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = reset_token.user
        user.set_password(form.password.data)
        reset_token.used = True
        db.session.commit()
        flash('Your password has been reset successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/reset_password.html', form=form, token=token)

@app.route('/expenses')
@login_required
def expenses():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    sort_by = request.args.get('sort', 'date_desc')
    
    query = Expense.query.filter_by(user_id=current_user.id)
    
    if search:
        query = query.filter(Expense.description.contains(search))
    if category_filter:
        query = query.filter_by(category_id=int(category_filter))
    
    if sort_by == 'date_desc':
        query = query.order_by(Expense.date.desc(),Expense.id.desc())
    elif sort_by == 'date_asc':
        query = query.order_by(Expense.date.asc(),Expense.id.desc())
    elif sort_by == 'amount_desc':
        query = query.order_by(Expense.amount.desc(),Expense.id.desc())
    elif sort_by == 'amount_asc':
        query = query.order_by(Expense.amount.asc(),Expense.id.desc())
    
    expenses = query.all()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    # Get recurring expenses and due ones
    recurring_expenses = RecurringExpense.query.filter_by(user_id=current_user.id, is_active=True).all()
    due_expenses = [r for r in recurring_expenses if r.next_due_date <= datetime.now().date()]
    
    total_amount = sum(expense.amount for expense in expenses)
    
    summary_data = {}
    if expenses:
        # Most expensive
        most_expensive = max(expenses, key=lambda x: x.amount)
        summary_data['most_expensive'] = {
            'amount': most_expensive.amount,
            'description': most_expensive.description
        }
        
        # Latest expense (by ID/creation order)
        latest_expense = max(expenses, key=lambda x: x.id)
        summary_data['latest_expense'] = {
            'description': latest_expense.description,
            'date': latest_expense.date
        }

        summary_data['average_amount'] = total_amount / len(expenses)
    else:
        summary_data = {
            'most_expensive': None,
            'latest_expense': None,
            'average_amount': 0
        }
    return render_template('expenses.html', 
                         expenses=expenses, 
                         categories=categories,
                         recurring_expenses=recurring_expenses,
                         due_expenses=due_expenses,
                         total_amount=total_amount,
                         summary_data=summary_data,
                         search=search,
                         category_filter=category_filter,
                         sort_by=sort_by,
                         now=datetime.now())

@app.route('/add-recurring-expense', methods=['POST'])
@login_required
def add_recurring_expense():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    try:
        description = request.form.get('description', '').strip()
        amount = float(request.form.get('amount', 0))
        category_id = int(request.form.get('category', 0))
        frequency = request.form.get('frequency', 'monthly')
        next_due_date_str = request.form.get('next_due_date')
        auto_add = bool(request.form.get('auto_add'))
        
        if not description or amount <= 0 or category_id == 0:
            flash('Please fill all required fields correctly.', 'error')
            return redirect(url_for('expenses'))
        
        next_due_date = datetime.strptime(next_due_date_str, '%Y-%m-%d').date()
        
        recurring_expense = RecurringExpense(
            description=description,
            amount=amount,
            category_id=category_id,
            user_id=current_user.id,
            frequency=frequency,
            next_due_date=next_due_date,
            auto_add=auto_add
        )
        
        db.session.add(recurring_expense)
        db.session.commit()
        flash(f'Recurring expense "{description}" created successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('expenses') + '#recurring')

@app.route('/process-recurring/<int:recurring_id>')
@login_required
def process_recurring(recurring_id):
    recurring = RecurringExpense.query.filter_by(id=recurring_id, user_id=current_user.id).first_or_404()
    
    expense = Expense(
        description=f"[Recurring] {recurring.description}",
        amount=recurring.amount,
        date=datetime.now().date(),
        user_id=current_user.id,
        category_id=recurring.category_id
    )
    db.session.add(expense)
    
    recurring.next_due_date = recurring.get_next_due_date()
    recurring.last_processed = datetime.now().date()
    
    db.session.commit()
    flash(f'Recurring expense "{recurring.description}" processed!', 'success')
    return redirect(url_for('expenses') + '#recurring')

@app.route('/delete-recurring/<int:recurring_id>', methods=['POST'])
@login_required
def delete_recurring(recurring_id):
    recurring = RecurringExpense.query.filter_by(id=recurring_id, user_id=current_user.id).first_or_404()
    recurring.is_active = False
    db.session.commit()
    flash(f'Recurring expense deleted!', 'success')
    return redirect(url_for('expenses') + '#recurring')




@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    form = ExpenseForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    
    if not form.category.choices:
        flash('Please add at least one category before adding expenses.', 'warning')
        return redirect(url_for('add_category'))
    
    if form.validate_on_submit():
        expense = Expense(
            description=form.description.data,
            amount=form.amount.data,
            date=datetime.strptime(form.date.data, '%Y-%m-%d').date(),
            user_id=current_user.id,
            category_id=form.category.data
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    return render_template('add_expense.html', form=form)

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    form = ExpenseForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        expense.description = form.description.data
        expense.amount = form.amount.data
        expense.date = datetime.strptime(form.date.data, '%Y-%m-%d').date()
        expense.category_id = form.category.data
        db.session.commit()
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('expenses'))
    
    if request.method == 'GET':
        form.description.data = expense.description
        form.amount.data = expense.amount
        form.date.data = expense.date.strftime('%Y-%m-%d')
        form.category.data = expense.category_id
    
    return render_template('edit_expense.html', form=form, expense=expense)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses'))

@app.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    form = CategoryForm()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    if form.validate_on_submit():
        existing = Category.query.filter_by(name=form.name.data, user_id=current_user.id).first()
        if existing:
            flash('Category already exists!', 'warning')
        else:
            category = Category(
                name=form.name.data, 
                user_id=current_user.id,
                icon=form.icon.data,
                color=form.color.data
            )
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('add_category'))
    
    return render_template('add_category.html', form=form, categories=categories)

@app.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first_or_404()
    
    # Check if category has expenses
    if category.expenses:
        flash(f'Cannot delete category "{category.name}" because it has {len(category.expenses)} expenses.', 'warning')
    else:
        db.session.delete(category)
        db.session.commit()
        flash(f'Category "{category.name}" deleted successfully!', 'success')
    
    return redirect(url_for('add_category'))


@app.route('/budgets')
@login_required
def budgets():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    
    # Calculate current month spending for each budget
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    budget_data = []
    for budget in budgets:
        spent_this_month = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category_id == budget.category_id,
            func.extract('month', Expense.date) == current_month,
            func.extract('year', Expense.date) == current_year
        ).scalar() or 0
        
        percentage = (spent_this_month / budget.monthly_limit) * 100 if budget.monthly_limit > 0 else 0
        
        budget_data.append({
            'budget': budget,
            'spent': spent_this_month,
            'remaining': budget.monthly_limit - spent_this_month,
            'percentage': percentage
        })
    
    return render_template('budgets.html', budget_data=budget_data)

@app.route('/add_budget', methods=['GET', 'POST'])
@login_required
def add_budget():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    form = BudgetForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    
    if form.validate_on_submit():
        existing_budget = Budget.query.filter_by(
            user_id=current_user.id, 
            category_id=form.category.data
        ).first()
        
        if existing_budget:
            existing_budget.monthly_limit = form.monthly_limit.data
            flash('Budget updated successfully!', 'success')
        else:
            budget = Budget(
                category_id=form.category.data,
                monthly_limit=form.monthly_limit.data,
                user_id=current_user.id
            )
            db.session.add(budget)
            flash('Budget set successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('budgets'))
    
    return render_template('add_budget.html', form=form)

@app.route('/delete_budget/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budgets'))

@app.route('/summary')
@login_required
def summary():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    categories = Category.query.filter_by(user_id=current_user.id).all()
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    
    # Calculate totals by category
    category_totals = {}
    category_counts = {}
    for expense in expenses:
        category_name = expense.category.name
        if category_name in category_totals:
            category_totals[category_name] += expense.amount
            category_counts[category_name] += 1
        else:
            category_totals[category_name] = expense.amount
            category_counts[category_name] = 1
    
    total_amount = sum(expense.amount for expense in expenses)
    
    # Prepare data for templates
    summary_data = {
        'category_totals': category_totals,
        'category_counts': category_counts,
        'total_amount': float(total_amount),
        'expense_count': len(expenses)
    }
    
    return render_template('summary.html', 
                         category_totals=category_totals, 
                         total_amount=total_amount,
                         expense_count=len(expenses),
                         summary_data=summary_data)


@app.route('/export_csv')
@login_required
def export_csv():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Description', 'Amount', 'Category'])
    
    # Write data
    for expense in expenses:
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.description,
            expense.amount,
            expense.category.name
        ])
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=monify_expenses_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and isinstance(current_user, Admin):
        return redirect(url_for('admin_dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and admin.check_password(form.password.data):
            admin.last_login = datetime.utcnow()
            db.session.commit()
            login_user(admin, remember=True)
            flash('Admin logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    
    return render_template('admin/login.html', form=form)

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Get statistics
    total_users = User.query.count()
    total_expenses = Expense.query.count()
    total_categories = Category.query.count()
    total_admins = Admin.query.count()
    
    # Get recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_expenses = Expense.query.order_by(Expense.date.desc()).limit(10).all()
    
    # Get monthly stats
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_expenses = db.session.query(func.sum(Expense.amount)).filter(
        func.extract('month', Expense.date) == current_month,
        func.extract('year', Expense.date) == current_year
    ).scalar() or 0
    
    # Top categories
    top_categories = db.session.query(
        Category.name, 
        func.sum(Expense.amount).label('total')
    ).join(Expense).group_by(Category.name).order_by(func.sum(Expense.amount).desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_expenses=total_expenses,
                         total_categories=total_categories,
                         total_admins=total_admins,
                         recent_users=recent_users,
                         recent_expenses=recent_expenses,
                         monthly_expenses=monthly_expenses,
                         top_categories=top_categories)

@app.route('/admin/users')
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@super_admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@super_admin_required
def admin_reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminResetUserPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        flash(f'Password reset successfully for user {user.username}!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin/reset_user_password.html', form=form, user=user)

@app.route('/admin/users/<int:user_id>/generate-temp-password', methods=['POST'])
@super_admin_required
def admin_generate_temp_password(user_id):
    user = User.query.get_or_404(user_id)
    
    # Generate random password
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
    user.set_password(temp_password)
    db.session.commit()
    
    flash(f'Temporary password for {user.username}: <strong>{temp_password}</strong>', 'warning')
    flash('Please share this password securely with the user.', 'info')
    return redirect(url_for('admin_users'))

@app.route('/admin/expenses')
@admin_required
def admin_expenses():
    page = request.args.get('page', 1, type=int)
    expenses = Expense.query.order_by(Expense.date.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template('admin/expenses.html', expenses=expenses)

@app.route('/admin/categories')
@admin_required
def admin_categories():
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    try:
        # Monthly user registrations (SQLite compatible)
        monthly_users = db.session.query(
            func.strftime('%Y-%m', User.created_at).label('month'),
            func.count(User.id).label('count')
        ).group_by(func.strftime('%Y-%m', User.created_at)).order_by('month').limit(12).all()
        
        # Monthly expense totals (SQLite compatible)
        monthly_expense_totals = db.session.query(
            func.strftime('%Y-%m', Expense.date).label('month'),
            func.sum(Expense.amount).label('total')
        ).group_by(func.strftime('%Y-%m', Expense.date)).order_by('month').limit(12).all()
        
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'danger')
        monthly_users = []
        monthly_expense_totals = []
    
    return render_template('admin/analytics.html',
                         monthly_users=monthly_users,
                         monthly_expense_totals=monthly_expense_totals)

@app.route('/admin/settings')
@super_admin_required
def admin_settings():
    admins = Admin.query.all()
    form = CreateAdminForm()
    return render_template('admin/settings.html', admins=admins, form=form)

@app.route('/admin/create-admin', methods=['POST'])
@super_admin_required
def admin_create_admin():
    form = CreateAdminForm()
    if form.validate_on_submit():
        admin = Admin(
            username=form.username.data,
            email=form.email.data,
            is_super_admin=form.is_super_admin.data
        )
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('Admin created successfully!', 'success')
    return redirect(url_for('admin_settings'))

@app.route('/admin/logout')
@admin_required
def admin_logout():
    logout_user()
    flash('Admin logged out successfully!', 'info')
    return redirect(url_for('admin_login'))

# Initialize first admin (run this once)
@app.route('/admin/init-super-admin')
def init_super_admin():
    if Admin.query.count() > 0:
        return "Super admin already exists!"
    
    admin = Admin(
        username='superadmin',
        email='admin@monify.ai',
        is_super_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    return "Super admin created! Email: admin@monify.ai, Password: admin123"

@app.route('/admin/reset-admin')
def reset_admin():
    Admin.query.delete()
    db.session.commit()
    
    admin = Admin(
        username='superadmin',
        email='admin@monify.ai',
        is_super_admin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    return "Admin reset! Email: admin@monify.ai, Password: admin123"

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
