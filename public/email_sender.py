import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailSender:
    def __init__(
        self,
        sender_email: str,
        password: str,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
    ):
        self.sender_email = sender_email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, recipient: str, body: str, subject: str):
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.password)
                text = message.as_string()
                server.sendmail(self.sender_email, recipient, text)
        except Exception as e:
            logging.error(f"Failed sending email to {recipient}: {e}")
