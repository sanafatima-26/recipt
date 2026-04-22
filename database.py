from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class StudentReceipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receipt_number = db.Column(db.String(20), unique=True, nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    mother_name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    roll_number = db.Column(db.String(50), nullable=False)
    registration_number = db.Column(db.String(50), nullable=False)
    fee_amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_mode = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'receipt_number': self.receipt_number,
            'student_name': self.student_name,
            'father_name': self.father_name,
            'mother_name': self.mother_name,
            'course': self.course,
            'semester': self.semester,
            'roll_number': self.roll_number,
            'registration_number': self.registration_number,
            'fee_amount': self.fee_amount,
            'payment_date': self.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
            'payment_mode': self.payment_mode,
            'transaction_id': self.transaction_id,
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }