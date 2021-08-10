import email
from email.mime.text import MIMEText
from unittest.mock import MagicMock, patch, mock_open

from getDomainAge.tests import with_valid_environment
from getDomainAge.tests.mocked_util import MockedUtil


@with_valid_environment
@patch('os.path.exists', MockedUtil().get_false)
def test_email_service():
    from getDomainAge.services.email import EmailService

    with patch('smtplib.SMTP') as mocked_smtp:
        smtp_server = mocked_smtp.return_value

        mail_send_status = EmailService().send_email(1, 'ljnath@ljnath.com', 'job1.csv')
        smtp_server.starttls.assert_called()
        smtp_server.sendmail.assert_called()
        smtp_server.quit.assert_called()
        assert mail_send_status


@with_valid_environment
@patch('os.path.exists', MockedUtil().get_false)
def test_failed_email_service():
    from getDomainAge.services.email import EmailService

    with patch('smtplib.SMTP') as mocked_smtp:
        smtp_server = mocked_smtp.return_value

        mail_send_status = EmailService().send_email(1, 0.1, 'job1.csv')
        smtp_server.starttls.assert_called()
        assert not mail_send_status


@with_valid_environment
@patch('os.path.exists', MockedUtil().get_true)
def test_email_attachment():
    from getDomainAge.services.email import EmailService

    with patch('builtins.open', mock_open(read_data="data")) as _:
        with patch('smtplib.SMTP') as _:
            status = EmailService().send_email(1, 'valid@email.com', 'job1.csv')
            assert status
