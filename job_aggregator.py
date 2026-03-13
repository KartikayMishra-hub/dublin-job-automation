import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time

jobs = []

def scrape_indeed():

    url = "https://ie.indeed.com/jobs?q=part+time&l=Dublin"

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "lxml")

    listings = soup.select(".job_seen_beacon")

    for job in listings:

        try:
            title = job.select_one("h2").text.strip()
            company = job.select_one(".companyName").text.strip()
            link = "https://ie.indeed.com" + job.select_one("a")["href"]

            jobs.append({
                "title": title,
                "company": company,
                "link": link
            })

        except:
            continue


def validate_link(url):

    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200

    except:
        return False


def clean_jobs():

    df = pd.DataFrame(jobs)

    df = df.drop_duplicates(subset=["title","company"])

    valid_jobs = []

    for index,row in df.iterrows():

        if validate_link(row["link"]):
            valid_jobs.append(row)

        time.sleep(1)

    df = pd.DataFrame(valid_jobs)

    return df


def generate_email(df):

    body = "Daily Dublin Part-Time Jobs\n\n"

    for index,row in df.iterrows():

        body += f"{row['title']}\n"
        body += f"Company: {row['company']}\n"
        body += f"Apply: {row['link']}\n\n"

    return body


def send_email(body):

    sender = "mishrakartik99@gmail.com"
    password = "qbgymqfapgmfkrkz"

    recipient = "mishrakartik99@gmail.com"

    msg = MIMEText(body)

    msg["Subject"] = f"Dublin Part-Time Jobs {datetime.today().date()}"
    msg["From"] = sender
    msg["To"] = recipient

    server = smtplib.SMTP_SSL("smtp.gmail.com",465)

    server.login(sender,password)

    server.send_message(msg)

    server.quit()


def run():

    scrape_indeed()

    df = clean_jobs()

    body = generate_email(df)

    send_email(body)

    print("Email sent successfully")


if __name__ == "__main__":
    run()