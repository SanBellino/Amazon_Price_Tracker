import requests
from bs4 import BeautifulSoup
import os
import smtplib
from email.message import EmailMessage
import time

#Header to avoid getting blocked by amazon
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

#Email configuration from .env file
email_sender = os.getenv("EMAIL_SENDER")
email_password = os.getenv("EMAIL_PASSWORD")
email_receiver = os.getenv("EMAIL_RECEIVER")
port = os.getenv("PORT")
smtp_server = os.getenv("SMTP_SERVER")

#Asks the user for the amazon link
get_link = input("Insert the link of the amazon product you want to know the price of: ")

#Asks the user for a treshold
price_treshold = float(input("Insert the treshold (example: 10.99), you'll receive an email if the product's price becomes below the treshold: "))

# Request the HTML content of the product page
r = requests.get(get_link, headers=headers).text

#deletes the index.html file if it already exists, otherwise it will create a new one
def create_index():
 if os.path.exists("index.html"):
    os.remove("index.html")
 else:
    create_html = open("index.html", "x")

#Writes the response of the r variable into index.html and parses it with BeautifulSoup
def write_index():
 with open("index.html", "w", encoding="utf-8") as f:
    f.write(r)

 with open("index.html", encoding="utf-8") as fp:
    soup = BeautifulSoup(fp, 'html.parser')
 return soup

# Scrapes the product title and price from the parsed HTML
def gather_data():
 find_title = soup.find('span', id="productTitle")
 find_price_whole =  soup.find('span', class_="a-price-whole")
 find_price_fraction =  soup.find('span', class_= "a-price-fraction")

 if find_title:
   if find_title:
    title = find_title.text.strip()
 else:
    title = "Title not found"

 if find_price_whole and find_price_fraction:
    whole = find_price_whole.text.strip().replace('.', '').replace(',', '')
    fraction = find_price_fraction.text.strip()
    price = float(whole + "." + fraction) 
 else:
    price = "Couldn't parse the price"
 return title, price

# Sends an email if the current price is lower than the threshold
def send_email(price):
  if price < price_treshold:
   msg = EmailMessage()
   msg['Subject'] = 'Tracker notification'
   msg['From'] = email_sender
   msg['To'] = email_receiver
   msg.set_content(f"   Product name: {title} \n " \
      f"   Actual price: {price} \n " \
      f"   Link: {get_link}")
   with smtplib.SMTP_SSL(smtp_server, port) as server:
    server.login(email_sender, email_password)
    server.send_message(msg)
  else:
   print("Not sending anything...")


# Repeats the process every x (60 for example ) seconds
while True:
 create_index()
 soup = write_index()
 title, price = gather_data()
 send_email(price)
 time.sleep(60)

