import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.users import User

app = create_app()
with app.app_context():
    u = User.query.filter_by(username='labtech1').first()
    if u:
        db.session.delete(u)
        db.session.commit()
        print('✅ labtech1 deleted')
    else:
        print('ℹ️ labtech1 not found')