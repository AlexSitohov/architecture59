import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from jinja2 import Template

from celery import shared_task

EMAIL_TEMPLATE = Template(
    """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #4a6fa5;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }
        .content {
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 0 0 5px 5px;
            border: 1px solid #ddd;
        }
        .code {
            font-size: 24px;
            font-weight: bold;
            color: #4a6fa5;
            text-align: center;
            margin: 20px 0;
            padding: 10px;
            background-color: #e7eff9;
            border-radius: 5px;
        }
        .footer {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Подтверждение email</h1>
    </div>
    <div class="content">
        <p>Здравствуйте!</p>
        <p>Для завершения регистрации, пожалуйста, используйте следующий код подтверждения:</p>
        <div class="code">{{ verification_code }}</div>
        <p>Если вы не запрашивали это письмо, пожалуйста, проигнорируйте его.</p>
    </div>
    <div class="footer">
        <p>©extendo merc</p>
    </div>
</body>
</html>
"""
)


@shared_task(bind=True, name="send_verification_email")
def send_verification_email(self, to: str, verification_code: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Ваш код подтверждения"
        msg["From"] = os.environ.get("SMTP_USER")
        msg["To"] = to

        text = ""
        html = EMAIL_TEMPLATE.render(verification_code=verification_code)

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(
            host="smtp.gmail.com",
            port=587,
        ) as server:
            server.starttls()
            server.login(
                user=os.environ.get("SMTP_USER"),
                password=os.environ.get("SMTP_PASSWORD"),
            )
            server.send_message(msg)

        return {"status": "success", "message": "Email sent successfully"}

    except smtplib.SMTPException as e:

        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
