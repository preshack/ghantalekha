from app import create_app
from app.extensions import db
from app.models.attendance import Attendance

app = create_app()
with app.app_context():
    db.session.query(Attendance).update({'work_duration_minutes': None})
    db.session.commit()
    print('All preset hours removed.')
