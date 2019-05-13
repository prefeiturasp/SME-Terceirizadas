from des.models import DynamicEmailConfiguration
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template import loader
from django.utils.translation import ugettext as _

# Create your views here.
from django.views.decorators.http import require_http_methods

subject = getattr(settings, 'DES_TEST_SUBJECT', _("Test Email"))
text_template = getattr(settings, 'DES_TEST_TEXT_TEMPLATE', "des/test_email.txt")
html_template = getattr(settings, 'DES_TEST_HTML_TEMPLATE', None)

message_text = loader.render_to_string(text_template)
message_html = loader.render_to_string(html_template) if html_template else None


# @require_http_methods(["POST"])
def send_test_email(request):
    email = request.POST.get('email', None)
    config = DynamicEmailConfiguration.get_solo()

    if email:
        try:
            send_mail(
                subject,
                message_text,
                config.from_email or None,
                [email],
                html_message=message_html)
            response = _("Test email sent. Please check \"{}\" for a "
                         "message with the subject \"{}\"").format(
                email,
                subject)
        except Exception as e:
            response = _("Could not send email. {}").format(e)
    else:
        response = _("You must provide an email address to test with.")

    return HttpResponse({'xx': response})
