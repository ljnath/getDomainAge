import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from getDomainAge.handlers.environment import Environment
from getDomainAge.handlers.log import LogHandler


class EmailService:
    def __init__(self):
        self.__env = Environment()
        self.__logger = LogHandler().get_logger(__name__, self.__env)

    def send_email(self, job_id: int, receiver_email: str, result_file: str) -> bool:
        """
        Method to send the result to the requester via email
        :param job_id : job_id as integer whose results needs to be emailed
        :param receiver_email : receiver_email as string who is suppose to receive the email
        :param result_file : result_file as string is the filepath to the CSV result file which will be attached with the email
        :return status : mail send status
        """
        mail_status = True
        try:
            html_message = '''
            <html>
                <head>
                    <title>
                        getDomainAge() - Results
                    </title>
                </head>
                <body>
                    Hello User,<br>
                    Thank you for using getDomainAge(), \
                        please find the age of your requested domain name(s) in the attached file.
                    <br><br>
                    -Cheers!<br>
                    getDomainAge()
                </body>
            </html>
                            '''

            email_message = MIMEMultipart('alternative')
            email_message['To'] = receiver_email
            email_message['From'] = self.__env.smtp_sender_email
            email_message['Subject'] = f'getDomainAge() - result of job #{job_id}'
            email_message.attach(MIMEText(html_message, 'html'))

            # attaching result file
            if os.path.exists(result_file):
                with open(result_file, "rb") as file_handler:
                    attachment_part = MIMEBase('application', 'octet-stream')
                    attachment_part.set_payload(file_handler.read())
                    encoders.encode_base64(attachment_part)
                    attachment_part.add_header(
                        'Content-Disposition', "attachment; filename= {}".format(os.path.basename(result_file)))
                    email_message.attach(attachment_part)
            smtp_server = smtplib.SMTP(host=self.__env.smtp_host, port=self.__env.smtp_port)
            smtp_server.starttls()

            # using authentication is specified in config.json file
            if self.__env.smtp_username and self.__env.smtp_password:
                smtp_server.login(self.__env.smtp_username, self.__env.smtp_password)

            smtp_server.sendmail(email_message['From'], email_message['To'], email_message.as_string())
            smtp_server.quit()
            self.__logger.info(
                f'Successfully emailed results for job #{job_id} {receiver_email} and attached {os.path.basename(result_file)}')

        except Exception as e:
            mail_status = False
            self.__logger.error(
                f'Failed to send email for job #{job_id} to {receiver_email} with {os.path.basename(result_file)}')
            self.__logger.exception(e, exc_info=True)

        return mail_status
