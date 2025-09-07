import os
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.staticfiles import finders
from email.mime.image import MIMEImage


def send_verification_email(email: str, uidb64: str, token: str) -> None:
    """Send account verification email with activation link."""
    
    subject = 'Confirm your email'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    link = f'{settings.FRONTEND_ACTIVATION_URL}?uid={uidb64}&token={token}'

    plain_message = (
        'Hello!\n\n'
        'Please confirm your email address by copying the following link into your browser:\n\n'
        f'{link}\n\n'
        'This link is valid for 24 hours.\n\n'
        'Thanks,\nYour Videoflix Team'
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=from_email,
        to=recipient_list
    )

    try:
        html_message = render_to_string('email/activation.html', {
            'link': link,
            'user_email': email
        })
        msg.attach_alternative(html_message, "text/html")
    except Exception as e:
        print(f"Warning: Could not render HTML template: {e}")

    try:
        logo_path = finders.find('logo.png')
        print(logo_path)
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<videoflix_logo>')
                img.add_header('Content-Disposition', 'inline; filename="logo.png"')
                msg.attach(img)
    except Exception as e:
        print(f"Warning: Could not attach logo: {e}")

    msg.send(fail_silently=False)


def send_password_reset_email(email: str, uidb64: str, token: str) -> None:
    """Send password reset email with reset link."""
    
    subject = 'Reset your password'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    link = f'{settings.FRONTEND_CONFIRM_PASSWORD_URL}?uid={uidb64}&token={token}'

    plain_message = (
        'Hello!\n\n'
        'You have requested a password reset.\n\n'
        'To reset your password, copy the following link into your browser:\n\n'
        f'{link}\n\n'
        'This link is valid for 24 hours.\n\n'
        'Thanks,\nYour Videoflix Team'
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=from_email,
        to=recipient_list
    )

    try:
        html_message = render_to_string('email/password_reset.html', {
            'link': link,
            'user_email': email
        })
        msg.attach_alternative(html_message, "text/html")
    except Exception as e:
        print(f"Warning: Could not render HTML template: {e}")

    try:
        logo_path = finders.find('logo.png')
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<videoflix_logo>')
                img.add_header('Content-Disposition', 'inline; filename="logo.png"')
                msg.attach(img)
    except Exception as e:
        print(f"Warning: Could not attach logo: {e}")

    msg.send(fail_silently=False)
