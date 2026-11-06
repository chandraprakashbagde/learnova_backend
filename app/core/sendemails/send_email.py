
from pathlib import Path
from brevo import AsyncBrevo
from brevo.transactional_emails import(
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem
)

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from jinja2.exceptions import TemplateError

from app.setting import setting



brevo_client = AsyncBrevo(
    api_key=setting.BREVO_API_KEY
)



# Configure Jinja2
TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "templates"
    / "email"
)


print(TEMPLATE_DIR)

template_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=True
)


def render_email_template(
    template_name: str,
    context: dict
) -> str:
    """
    Render an HTML email template using Jinja2.

    Args:
        template_name: Name of the HTML template.
        context: Dynamic variables for the template.

    Returns:
        Rendered HTML content.

    Raises:
        FileNotFoundError: If template doesn't exist.
        ValueError: If template rendering fails.
    """

    try:
        template = template_env.get_template(template_name)

        html_content = template.render(**context)

        return html_content

    except TemplateNotFound as exc:
        raise FileNotFoundError(
            f"Email template '{template_name}' not found."
        ) from exc

    except TemplateError as exc:
        raise ValueError(
            f"Failed to render email template: {exc}"
        ) from exc


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    to_name: str
):
    """
    Send an HTML email using Resend.
    """

    try:
        response = await brevo_client.transactional_emails.send_transac_email(
            subject=subject,
            html_content=html_content,
            sender=SendTransacEmailRequestSender(
                name=setting.EMAIL_FROM_NAME,
                email=setting.EMAIL_FROM,
            ),
            to=[
                SendTransacEmailRequestToItem(
                    email=to_email,
                    name=to_name,
                )
            ],
        )

        return response

    except Exception:
        print("Failed to send email to %s",
                    to_email)
        raise
