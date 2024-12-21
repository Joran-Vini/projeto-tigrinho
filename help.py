from flask import redirect, url_for, session
from functools import wraps

def login_required(f):
    "Decorate routes to require login"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
    