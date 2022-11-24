from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Email, ValidationError, Optional
from campusdiffuso.models import User


class RegistrationForm(FlaskForm):
    name = StringField("Nome *", validators=[DataRequired(), Length(min=3, max=15)])
    surname = StringField("Cognome *", validators=[DataRequired(), Length(min=3, max=15)])
    date = DateField("Data di nascita (facoltativo)", validators=[Optional()])
    email = StringField("Email Universitaria *", validators=[DataRequired(), Email()])
    university = RadioField("Ateneo *", validators=[DataRequired()], choices=[('lasapienza', 'La Sapienza'), ('torvergata', 'Tor Vergata'), ('romatre', 'Roma Tre')])
    tips = TextAreaField("Suggerimenti (facoltativo)", validators=[Optional(), Length(max=500)], render_kw={"placeholder": "Suggerimenti..."})
    gdpr = BooleanField("Accettazione GDPR *", validators=[DataRequired()])
    terms_and_conditions = BooleanField("Accettazione Termini e Condizioni *", validators=[DataRequired()])
    submit = SubmitField("Ottieni QRCode")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("L'indirizzo email è già in uso. Si prega di sceglierne uno diverso.")