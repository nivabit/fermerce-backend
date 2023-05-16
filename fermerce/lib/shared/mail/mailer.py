from email import encoders
from email.mime.base import MIMEBase
import os
import smtplib
from email.mime import multipart, text
from email.utils import formataddr
from typing import Optional, List, Union
import pydantic
from fermerce.lib.shared.mail import exception
from fermerce.lib.shared.mail import template_finder
from fermerce.core.settings import config

from fermerce.lib.errors import error


class Mailer(template_finder.MailTemplate):
    def __init__(
        self,
        subject: str,
        sender_email: Optional[pydantic.EmailStr] = config.admin_email,
        sender_password: Optional[str] = config.admin_password,
        email_host: Optional[str] = config.email_host,
        email_server_port: Optional[int] = config.email_port,
        template_folder: Optional[
            pydantic.DirectoryPath
        ] = config.email_template_dir,
        website_name: str = config.project_name,
        use_google: Optional[bool] = True,
        body: Optional[str] = None,
        template_name: Optional[str] = None,
        context=None,
    ) -> None:
        super().__init__(template_folder)
        if context is None:
            context = {}
        self.admin_email = sender_email
        self.admin_password = sender_password
        self.template_name = template_name
        self.email_host = email_host
        self.email_server_port = email_server_port
        self.use_google = use_google
        self.website_name = website_name
        self.body = body
        self.context = context
        self.subject = subject
        self.attachments = []

    def add_attachment(self, attachment_paths: List[str]) -> None:
        for attachment_path in attachment_paths:
            with open(attachment_path, "rb") as f:
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}",
                )
                self.attachments.append(attachment)

    def send_mail(
        self,
        email: Union[List[pydantic.EmailStr], pydantic.EmailStr],
    ):
        message = multipart.MIMEMultipart()
        if isinstance(email, list):
            message["To"] = ", ".join(email)
        if isinstance(email, str):
            message["To"] = email
        from_email = self.admin_email
        subject: str = self.subject
        message["Subject"] = subject
        message["From"] = formataddr((self.website_name, from_email))

        if self.template_name and self.template_folder:
            body_content = self.render(self.template_name, self.context)
            message.attach(text.MIMEText(body_content, "html"))
        elif self.body:
            body_content = self.body
            message.attach(text.MIMEText(body_content, "plain"))
        else:
            raise exception.InvalidEmailContentError(
                "Email body content is required"
            )
        if self.attachments:
            for attachment in self.attachments:
                message.attach(attachment)
        try:
            with smtplib.SMTP_SSL(
                host=self.email_host, port=self.email_server_port
            ) as smtp:
                smtp.login(
                    user=self.admin_email,
                    password=self.admin_password,
                )
                smtp.sendmail(from_email, email, message.as_string())
            pass
        except Exception:
            raise error.ServerError("Could not connect to mail server")
