from mock import Mock
from flask_mail import Message
from flask_mail import Mail
from taskmaster import app, settings

if settings.ENABLE_EMAIL:
    mail = Mail(app)
else:
    mail = Mock()
