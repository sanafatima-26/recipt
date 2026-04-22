from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from database import db, StudentReceipt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import os
from datetime import datetime
import random
import string
from io import BytesIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fe_receipts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

def generate_receipt_number():
    """Generate unique receipt number"""
    prefix = "FER"
    date_str = datetime.now().strftime("%Y%m%d")
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{date_str}{random_num}"

def generate_pdf_receipt(student_data):
    """Generate PDF receipt for student"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        alignment=1,
        spaceAfter=30
    )
    title = Paragraph("FEE RECEIPT", title_style)
    elements.append(title)
    
    # Institution details
    inst_style = ParagraphStyle(
        'Institution',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor('#333333')
    )
    institution = Paragraph("<b>FUTURE ENGINEERS COLLEGE</b><br/>"
                          "Approved by AICTE, Affiliated to Technical University<br/>"
                          "Address: Knowledge Park, Greater Noida, UP - 201310", inst_style)
    elements.append(institution)
    elements.append(Spacer(1, 20))
    
    # Receipt number and date
    receipt_info = [
        ["Receipt Number:", student_data['receipt_number']],
        ["Date:", student_data['payment_date']],
        ["Payment Mode:", student_data['payment_mode']]
    ]
    
    receipt_table = Table(receipt_info, colWidths=[2*inch, 3*inch])
    receipt_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(receipt_table)
    elements.append(Spacer(1, 20))
    
    # Student details table
    student_details = [
        ["Student Details", ""],
        ["Student Name:", student_data['student_name']],
        ["Father's Name:", student_data['father_name']],
        ["Mother's Name:", student_data['mother_name']],
        ["Roll Number:", student_data['roll_number']],
        ["Registration Number:", student_data['registration_number']],
        ["Course:", student_data['course']],
        ["Semester:", student_data['semester']],
        ["Email:", student_data['email']],
        ["Phone:", student_data['phone']],
        ["Address:", student_data['address']]
    ]
    
    student_table = Table(student_details, colWidths=[2*inch, 3.5*inch])
    student_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 20))
    
    # Fee details
    fee_details = [
        ["Fee Details", ""],
        ["Fee Amount:", f"₹ {student_data['fee_amount']:,.2f}"],
        ["Transaction ID:", student_data['transaction_id'] or "N/A"]
    ]
    
    fee_table = Table(fee_details, colWidths=[2*inch, 3.5*inch])
    fee_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
    ]))
    elements.append(fee_table)
    elements.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,
        textColor=colors.grey
    )
    footer = Paragraph("This is a computer generated receipt. No signature required.", footer_style)
    elements.append(footer)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    """Home page - Student entry form"""
    return render_template('index.html')

@app.route('/submit_receipt', methods=['POST'])
def submit_receipt():
    """Handle receipt submission"""
    try:
        # Generate receipt number
        receipt_number = generate_receipt_number()
        
        # Create new receipt entry
        new_receipt = StudentReceipt(
            receipt_number=receipt_number,
            student_name=request.form['student_name'],
            father_name=request.form['father_name'],
            mother_name=request.form['mother_name'],
            course=request.form['course'],
            semester=request.form['semester'],
            roll_number=request.form['roll_number'],
            registration_number=request.form['registration_number'],
            fee_amount=float(request.form['fee_amount']),
            payment_date=datetime.strptime(request.form['payment_date'], '%Y-%m-%d'),
            payment_mode=request.form['payment_mode'],
            transaction_id=request.form.get('transaction_id', ''),
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address']
        )
        
        # Save to database
        db.session.add(new_receipt)
        db.session.commit()
        
        flash(f'Receipt generated successfully! Receipt Number: {receipt_number}', 'success')
        return redirect(url_for('view_receipt', receipt_id=new_receipt.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error generating receipt: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/receipt/<int:receipt_id>')
def view_receipt(receipt_id):
    """View receipt details"""
    receipt = StudentReceipt.query.get_or_404(receipt_id)
    return render_template('receipt.html', receipt=receipt)

@app.route('/download_receipt/<int:receipt_id>')
def download_receipt(receipt_id):
    """Download receipt as PDF"""
    receipt = StudentReceipt.query.get_or_404(receipt_id)
    
    student_data = {
        'receipt_number': receipt.receipt_number,
        'student_name': receipt.student_name,
        'father_name': receipt.father_name,
        'mother_name': receipt.mother_name,
        'course': receipt.course,
        'semester': receipt.semester,
        'roll_number': receipt.roll_number,
        'registration_number': receipt.registration_number,
        'fee_amount': receipt.fee_amount,
        'payment_date': receipt.payment_date.strftime('%Y-%m-%d'),
        'payment_mode': receipt.payment_mode,
        'transaction_id': receipt.transaction_id,
        'email': receipt.email,
        'phone': receipt.phone,
        'address': receipt.address
    }
    
    pdf_buffer = generate_pdf_receipt(student_data)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"receipt_{receipt.receipt_number}.pdf",
        mimetype='application/pdf'
    )

@app.route('/all_receipts')
def all_receipts():
    """View all receipts"""
    receipts = StudentReceipt.query.order_by(StudentReceipt.created_at.desc()).all()
    return render_template('view_receipts.html', receipts=receipts)

@app.route('/api/receipts')
def api_receipts():
    """API endpoint for receipts data"""
    receipts = StudentReceipt.query.all()
    return jsonify([receipt.to_dict() for receipt in receipts])

@app.route('/search_receipt')
def search_receipt():
    """Search receipt by number or name"""
    query = request.args.get('q', '')
    if query:
        receipts = StudentReceipt.query.filter(
            (StudentReceipt.receipt_number.contains(query)) |
            (StudentReceipt.student_name.contains(query)) |
            (StudentReceipt.roll_number.contains(query))
        ).all()
    else:
        receipts = []
    
    return render_template('view_receipts.html', receipts=receipts, search_query=query)

if __name__ == '__main__':
    app.run(debug=True, port=5000)