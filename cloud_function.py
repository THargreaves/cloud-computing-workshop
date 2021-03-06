import datetime as dt
import requests
import os

from bs4 import BeautifulSoup
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.

    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    html_content = scrape_news()
    
    message = Mail(
        from_email='tim.hargreaves@icloud.com',
        to_emails='tim.hargreaves@icloud.com',
        subject=f"Your morning news for {dt.date.today()}",
        html_content=html_content)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def scrape_news():
    """Scrape news from BBC homepage."""
    try:
        # Scrape BBC homepage
        res = requests.get('https://www.bbc.co.uk/news')
        if 200 <= res.status_code < 300:
            raise ValueError(f"request failed with code {res.status_code}")
        soup = BeautifulSoup(res.content, 'html.parser')

        # Find top stories section
        top_stories = soup.find('div', {
            'class': 'nw-c-top-stories__tertiary-items'
        })
        stories = top_stories.find_all('a', {
            'class': 'gs-c-promo-heading'
        })

        # Create email content
        email_lines = []
        base_url = 'https://www.bbc.co.uk'
        for story in stories:
            email_lines.append(f"<a href='{{base_url + story['href']}}'>{story.text}</a>")
        return '<br>'.join(email_lines)

    except Exception as e:
        return e
