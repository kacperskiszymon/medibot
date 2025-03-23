import os, smtplib, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def google_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        credentials_json = os.getenv("GOOGLE_CREDENTIALS")
        if credentials_json:
            flow = InstalledAppFlow.from_client_config(json.loads(credentials_json), SCOPES)
        else:
            # fallback na plik credentials.json (np. lokalnie)
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def send_email(subject, message, recipient):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
    except Exception as e:
        print(f"Błąd wysyłki email: {e}")

def make_booking(data):
    try:
        service = google_calendar_service()

        # przygotowanie daty i czasu wydarzenia
        start_time = datetime.fromisoformat(data['datetime'])
        end_time = start_time + timedelta(minutes=30)  # wizyta będzie trwała 30 minut

        event = {
            'summary': f"Wizyta: {data['name']}",
            'description': f"Telefon: {data['phone']}",
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Europe/Warsaw'
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Europe/Warsaw'
            },
        }

        event_result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        # wysyłka email potwierdzającego dla lekarza
        send_email(
            "Nowa rezerwacja wizyty MediBot",
            f"Nowa rezerwacja:\nPacjent: {data['name']}\nTermin: {start_time.strftime('%Y-%m-%d %H:%M')}\nTel: {data['phone']}",
            EMAIL_ADDRESS
        )

        # wysyłka email do pacjenta
        send_email(
            "Potwierdzenie wizyty w MediBot",
            f"Dziękujemy za rezerwację wizyty, {data['name']}!\nTermin wizyty: {start_time.strftime('%Y-%m-%d %H:%M')}\n\nDo zobaczenia!",
            data['email']
        )

        return {"status": "success", "message": "Rezerwacja zakończona sukcesem! Sprawdź e-mail."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
