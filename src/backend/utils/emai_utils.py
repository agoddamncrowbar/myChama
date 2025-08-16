import smtplib
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, body: str):
    from_email = "mychamacorporation@gmail.com"
    app_password = "xsph usyo tqdo vnag"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.send_message(msg)
