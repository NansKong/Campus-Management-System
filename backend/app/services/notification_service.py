from sqlalchemy.orm import Session
from typing import List
from app.models.student import Student
from app.models.attendance import AttendanceRecord
from app.models.notification import Notification
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings

class NotificationService:
    """Service for sending notifications via Email and SMS"""
    
    @staticmethod
    def send_attendance_notifications(db: Session, session_id: str, attendance_records: List[AttendanceRecord]):
        """Send notifications to students and parents after attendance is marked"""
        
        notifications_sent = {
            'student_emails': 0,
            'parent_emails': 0,
            'student_sms': 0,
            'parent_sms': 0,
            'absentees': []
        }
        
        for record in attendance_records:
            # Get student details
            student = db.query(Student).filter(Student.student_id == record.student_id).first()
            
            if not student:
                continue
            
            # Check if absent
            if record.status == 'absent':
                notifications_sent['absentees'].append({
                    'name': f"{student.first_name} {student.last_name}",
                    'reg_no': student.registration_number
                })
                
                # Send SMS to student
                student_sms_sent = NotificationService.send_sms(
                    student.phone,
                    f"Attendance Alert: You were marked ABSENT today. Please contact your faculty if this is incorrect. - LPU Smart Campus"
                )
                if student_sms_sent:
                    notifications_sent['student_sms'] += 1
                
                # Send SMS to parent
                if student.parent_phone:
                    parent_sms_sent = NotificationService.send_sms(
                        student.parent_phone,
                        f"Dear Parent, Your ward {student.first_name} {student.last_name} (Reg: {student.registration_number}) was marked ABSENT today. - LPU"
                    )
                    if parent_sms_sent:
                        notifications_sent['parent_sms'] += 1
                
                # Send Email to student
                student_email_sent = NotificationService.send_email(
                    student.user.email,
                    "Attendance Alert - Marked Absent",
                    f"""
                    <html>
                    <body style="font-family: Arial, sans-serif;">
                        <h2 style="color: #dc2626;">Attendance Alert</h2>
                        <p>Dear {student.first_name},</p>
                        <p>You were marked <strong style="color: #dc2626;">ABSENT</strong> in today's class.</p>
                        <p><strong>Registration Number:</strong> {student.registration_number}</p>
                        <p>If you believe this is an error, please contact your faculty immediately.</p>
                        <br>
                        <p>Best regards,<br>LPU Smart Campus System</p>
                    </body>
                    </html>
                    """
                )
                if student_email_sent:
                    notifications_sent['student_emails'] += 1
                
                # Send Email to parent
                if student.parent_email:
                    parent_email_sent = NotificationService.send_email(
                        student.parent_email,
                        f"Student Attendance Alert - {student.first_name} {student.last_name}",
                        f"""
                        <html>
                        <body style="font-family: Arial, sans-serif;">
                            <h2 style="color: #dc2626;">Student Attendance Alert</h2>
                            <p>Dear Parent/Guardian,</p>
                            <p>This is to inform you that your ward has been marked <strong style="color: #dc2626;">ABSENT</strong> today.</p>
                            <p><strong>Student Name:</strong> {student.first_name} {student.last_name}</p>
                            <p><strong>Registration Number:</strong> {student.registration_number}</p>
                            <p><strong>Program:</strong> {student.program}</p>
                            <p><strong>Semester:</strong> {student.semester}</p>
                            <br>
                            <p>Please ensure your ward maintains regular attendance.</p>
                            <p>For any queries, please contact the university.</p>
                            <br>
                            <p>Best regards,<br>Lovely Professional University<br>Smart Campus System</p>
                        </body>
                        </html>
                        """
                    )
                    if parent_email_sent:
                        notifications_sent['parent_emails'] += 1
                
                # Create in-app notification
                notification = Notification(
                    user_id=student.user_id,
                    notification_type='attendance',
                    title='Attendance Alert - Marked Absent',
                    message=f'You were marked absent in today\'s class. If this is incorrect, please contact your faculty.'
                )
                db.add(notification)
        
        db.commit()
        return notifications_sent
    
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        """Send email notification"""
        try:
            # For demo purposes, we'll just print the email
            # In production, use actual SMTP settings
            print(f"\n{'='*60}")
            print(f"📧 EMAIL SENT")
            print(f"{'='*60}")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Content: {html_content[:100]}...")
            print(f"{'='*60}\n")
            
            # Uncomment below for actual email sending
            # msg = MIMEMultipart('alternative')
            # msg['Subject'] = subject
            # msg['From'] = settings.SMTP_USER
            # msg['To'] = to_email
            # 
            # html_part = MIMEText(html_content, 'html')
            # msg.attach(html_part)
            # 
            # with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            #     server.starttls()
            #     server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            #     server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False
    
    @staticmethod
    def send_sms(phone_number: str, message: str) -> bool:
        """Send SMS notification"""
        try:
            # For demo purposes, we'll simulate SMS sending
            # In production, integrate with SMS gateway like Twilio, MSG91, etc.
            print(f"\n{'='*60}")
            print(f"📱 SMS SENT")
            print(f"{'='*60}")
            print(f"To: {phone_number}")
            print(f"Message: {message}")
            print(f"{'='*60}\n")
            
            # Example Twilio integration (uncomment when ready):
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(
            #     body=message,
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=phone_number
            # )
            
            return True
        except Exception as e:
            print(f"SMS send error: {e}")
            return False

notification_service = NotificationService()