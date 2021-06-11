rom __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests
from PIL import Image

import bs4
import os
import time
import playsound
import speech_recognition as sr
import pytz

import subprocess
from gtts import gTTS
import uuid
filename = str(uuid.uuid4()) + ".mp3"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", 'february", "march", "april", "may", "june", "july", "august", "september", "october', "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENSION =["rd", "th", "st", "nd"]



#FUNCTION THAT ALLOWS AI TO SPEAK BACK WHAT IS SAID
def speak(text):
#    engine = pyttsx3.init()
#    engine.say(text)
#    engine.runAndWait()
    
    tts=gTTS(text=text, lang="en")
    filename = str(uuid.uuid4()) + ".mp3"
 #   filename="voice.mp3"
    tts.save(filename)
    playsound.playsound(filename)



#FUNCTION THAT RETURNS VOICE
def get_audio():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source)
        said=""

        try:
            said=r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))
    return said


#START OF QUICKSTART

def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date= date.astimezone(utc)
    end_date=end_date.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        speak(f"You have {len(events)} on this day.")
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        start_time=str(start.split("T")[1].split("-")[0])
        if int(start_time.split(":")[0]) < 12:
               start_time = start_time + "am"
               
        else:
               start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(":")[1]
               start_time = start_time + "pm"
        speak(event["summary"] + "at" + start_time)
               
             
        
def get_date(text):
    text = text.lower()
    today = datetime.date.today()
    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSION:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass
    if month < today.month and month != -1:
        year = year + 1
        
    if day < today.day and month == -1 and day != -1:
            month = month + 1
            
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif+=7
            if text.count("next") >=1:
                dif+=7

        return today + datetime.timedelta(dif)
    if month == -1 or day == -1:
        return NONE
    return datetime.date(month=month, day=day, year=year)

def note(text):
    date=datetime.datetime.now()
    file_name =str(date).replace(":", "-") + "note.txt"
    with open(file_name, "w") as f:
        f.write(text)
        
    subprocess.Popen(["notepad.exe", file_name])

def conditionsToday(condURL):
     res = requests.get("https://weather.com/weather/today/l/43.12%2C-83.70?par=facebook_bookmark&fbcl")
     soup = bs4.BeautifulSoup(res.text, 'html.parser')
     condition = soup.select("#dp0-details-narrative")
     return condition[0].text.strip()
    


        
WAKE = "Gideon"
        
SERVICE=authenticate_google()
print("Start")

while True:
    print("Listening")
    text=get_audio()
    if text.count(WAKE) > 0:
        speak("Hello David. What can I do for you?")
        text = get_audio()
        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy", "what am I doing"]
        for phrase in CALENDAR_STRS:
            if phrase in text.lower():
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("Please Speak Again")
        
        NOTE_STRS = ["make a note", "write this down", "write that down", "remember this", "take note"]

        for phrase in NOTE_STRS:
            if phrase in text.lower():
                speak("What would you like me to write down?")
                note_text = get_audio()
                note(note_text)
                speak("I have made a note of that")
            
        GOODBYE_STRS = ("exit", "off", "turn off", "see you later", "goodbye", "bye", "bye now")
        for phrase in GOODBYE_STRS:
            if phrase in text.lower():
                speak("Goodbye David.")
                sys.exit()
        WEATHER_STRS = ("today's forecast", "weather forecast", "forecast for today", "today's weather")
        for phrase in WEATHER_STRS:
            if phrase in text.lower():
                narrative = conditionsToday("https://weather.com/weather/today/l/43.12%2C-83.70?par=facebook_bookmark&fbcl")

                speak(narrative)
