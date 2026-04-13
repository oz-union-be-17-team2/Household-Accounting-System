from django.core.mail import EmailMessage


def send_email(subject: str, message: str, to_email: str | list[str]):
    to_email = [to_email] if isinstance(to_email, str) else to_email
    email = EmailMessage(subject, message, to=to_email)
    email.content_subtype = "html"
    return email.send()
