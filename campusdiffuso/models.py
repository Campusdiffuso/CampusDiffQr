from itsdangerous import URLSafeTimedSerializer
from dateutil.relativedelta import relativedelta
from flask import current_app
from campusdiffuso import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "campusdiffuso"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(20), nullable=False)
    cognome = db.Column(db.String(20), nullable=False)
    data_di_nascita = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    ateneo = db.Column(db.String(40), nullable=False)
    suggerimenti = db.Column(db.String(500), nullable=True)
    data_di_rilascio = db.Column(db.String(40), nullable=False, default=datetime.now().strftime("%d-%m-%Y"))
    data_di_scadenza = db.Column(db.String(40), nullable=False, default=(datetime.now() + relativedelta(years=6)).strftime("%d-%m-%Y"))
    confermato = db.Column(db.Boolean, nullable=False, default=False)

    def generate_confirmation_token(self, email):
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def confirm_token(token, expiration=86400): # 24 h
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
        except:
            return False
        return email

    def __repr__(self):
        return f"User('{self.nome}', '{self.cognome}', '{self.data_di_nascita}', '{self.email}', '{self.ateneo}', '{self.suggerimenti}')"