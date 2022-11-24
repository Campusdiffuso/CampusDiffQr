from campusdiffuso import db, mail
from campusdiffuso.models import User
from flask_mail import Message
from flask import current_app
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO
import base64
import qrcode
import time


class QRCodeMaker:
    def __init__(self, user):
        self.name = user.nome
        self.surname = user.cognome
        self.date_of_expiration = user.data_di_scadenza

        self.qrcode_filename = f"{self.name.lower()}-{self.surname.lower()}-campus-diffuso-qrcode.png"
        self.text = f"Campus Diffuso QRCode di {self.name} {self.surname} valido fino al {self.date_of_expiration}"

        self.logo_path = "campusdiffuso/static/picture/campus-diffuso-green.jpg"
        self.image = Image.open(self.logo_path)
        self.resized = 0.125
        self.logo = self.image.resize((round(self.image.size[0] * self.resized), round(self.image.size[1] * self.resized)))

        self.W, self.H = (550, 650)
        self.text_font = ImageFont.truetype("campusdiffuso/static/font/arial.ttf", 40)
        self.date_font = ImageFont.truetype("campusdiffuso/static/font/arial.ttf", 20)
    
    def create(self):
        # making qrcode with data
        qr = qrcode.QRCode(border=1, error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(self.text)
        qr.make()
        qr_img = qr.make_image(fill_color="#64a89a", back_color="white").convert("RGB")
        
        # making white_img
        white_img = Image.new('RGB', (self.W, self.H), color="white")
        
        # paste qrcode in white_img
        logo_pos = ((qr_img.size[0] - self.logo.size[0]) // 2, (qr_img.size[1] - self.logo.size[1]) // 2)
        qr_img.paste(self.logo, logo_pos)
        white_img.paste(qr_img, ((white_img.size[0] - qr_img.size[0]) // 2, (white_img.size[1] - qr_img.size[1]) // 10))
        
        # draw name, surname and date_of_expiration
        draw = ImageDraw.Draw(white_img)
        w, wd = (
            draw.textsize(f"{self.name} {self.surname}", font=self.text_font)[0],
            draw.textsize(f"Scadenza: {self.date_of_expiration}", font=self.date_font)[0]
        )
        draw.line((30, qr_img.size[1] + 20, self.W - 30, qr_img.size[0] + 20), fill=0, width=2)
        draw.text(((self.W - w) / 2, self.W - 10), f"{self.name} {self.surname}", (0, 0, 0), font=self.text_font)
        draw.text(((self.W - wd) / 2, self.W + 40), f"Scadenza: {self.date_of_expiration}", (0, 0, 0), font=self.date_font)

        white_img.save(f"campusdiffuso/static/media/{self.qrcode_filename}")
        return self.qrcode_filename


class Checker:
    def __init__(self, form):
        self.university_names = ["torvergata", "lasapienza", "romatre"]
        self.university_domains = ["students.uniroma2.eu", "studenti.uniroma1.it", "stud.uniroma3.it"]

        # User Input Form
        self.name = str(form.name.data).lower().replace(" ", "")
        self.surname = str(form.surname.data).lower().replace(" ", "")
        self.email = str(form.email.data).lower()
        self.university = str(form.university.data).lower().replace(" ", "")

    def universityIndex(self) -> int:
        for i in range(len(self.university_names)):
            if self.email.endswith(self.university_domains[i]) and self.university == self.university_names[i]:
                return i
        return -1

    def __getSnail(self) -> list:
        for j in range(len(self.email)):
            if self.email[j] == "@":
                return j
 
    def __getIndex(self, stop: str, j: int) -> list:
        l = []
        for i in range(len(self.email[:j])):
            if self.email[i] == stop:
                l.append(i)
        return l

    def all(self, idx: int) -> bool:
        j = self.__getSnail()
        i = self.__getIndex(".", j)
        # print(self.email[:i], self.email[i+1:j])

        if len(i) == 1:
            if idx == 0: # torvergata
                 flag = True if self.name == self.email[:i[0]] and self.surname == self.email[i[0]+1:j] else False
            elif idx == 1 or idx == 2: # lasapienza o romatre
                flag = True if self.surname == self.email[:i[0]] else False
            return True if flag else False
        elif len(i) == 2:
            if idx == 0: # torvergata
                 flag = True if self.name == self.email[:i[0]] and self.surname == self.email[i[0]+1:i[1]] else False
            elif idx == 1 or idx == 2: # lasapienza o romatre
                flag = True if self.surname == self.email[:i[0]] else False
            return True if flag else False


def send_email(to, subject, template):
    msg = Message(
        subject=subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_USERNAME']
    )
    mail.send(msg)

def img_to_base64(img_path):
    img = Image.open(current_app.root_path + img_path)
    data = BytesIO()
    img.save(data, format="JPEG")
    return f"data:image/jpeg;base64,{base64.b64encode(data.getvalue()).decode('utf-8')}"

def check_date_of_expiration():
    while True:
        for user in User.query.all():
            if datetime.now().strftime("%d-%m-%Y") == user.data_di_scadenza and datetime.now().hour == 0:
                db.session.delete(user)
                db.session.commit()
        time.sleep(2.628e+6) # un mese

def init_db():
    db.drop_all()
    db.create_all()
    user = User(nome="admin", cognome="admin", data_di_nascita="yyyy-mm-dd", email="admin@example.com", ateneo="admin", suggerimenti="Aggiungerei un Bot Telegram per leggere i QRCode degli utenti")
    db.session.add(user)
    db.session.commit()