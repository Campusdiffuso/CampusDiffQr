from flask import render_template, flash, url_for, redirect
from campusdiffuso.users.forms import RegistrationForm
from campusdiffuso.users.utils import *
from campusdiffuso.models import User
from campusdiffuso import db
from flask import Blueprint

users = Blueprint("users", __name__)

@users.route("/", methods=["GET", "POST"])
@users.route("/register", methods=["GET", "POST"])
def register():
    # init_db()
    form = RegistrationForm()
    check = Checker(form)
    if form.validate_on_submit():
        if ( idx := check.universityIndex() ) != -1:
            if check.all(idx):
                user = User(
                    nome=form.name.data,
                    cognome=form.surname.data,
                    data_di_nascita=form.date.data,
                    email=form.email.data,
                    ateneo=form.university.data,
                    suggerimenti=form.tips.data
                )
                db.session.add(user)
                db.session.commit()

                token = user.generate_confirmation_token(form.email.data)
                confirm_url = url_for("users.confirm_email", token=token, _external=True)
                if user.email.endswith("studenti.uniroma1.it"):
                    html = render_template("verification_gmail.html", confirm_url=confirm_url)
                else:
                    html = render_template(
                        "verification_outlook.html",
                        confirm_url=confirm_url,
                        img_data=img_to_base64("/static/picture/campus-diffuso-green.jpg")
                    )
                subject = "Verifica Email - Campus Diffuso"
                send_email(user.email, subject, html)
                flash("Email di verifica inviata! (controlla lo spam)", "success")
                return redirect(url_for("users.register"))
            else:
                flash("Il nome e/o il cognome inseriti non corrispondono a quelli presenti nell'indirizzo email!", "danger")
        else:
            flash("L'indirizzo email inserito non è valido e/o l'ateneo inserito non corrisponde all'indirizzo email inserito!", "danger")
    return render_template("register.html", title="Register", form=form)

@users.route("/register/<token>", methods=["GET", "POST"])
def confirm_email(token):
    form = RegistrationForm()
    email = User.confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()
    if user is None:
        flash("Questo è un token non valido!", "warning")
        db.session.delete(user)
        db.session.commit()
    elif user.confermato:
        # flash("Indirizzo email già confermato", "info")
        flash("Grazie per aver confermato il tuo indirizzo email, a breve riceverai il tuo QRCode!", "success")
    else:
        user.confermato = True
        db.session.commit()

        qr = QRCodeMaker(user)
        qr_filename = qr.create()

        if user.email.endswith("studenti.uniroma1.it"):
            flash("ATTENZIONE: tieni premuto sul QRCode per salvarlo!", "info")
            return render_template("qrcode_gmail.html", img_data=img_to_base64(f"/static/media/{qr_filename}"))
        else:
            flash("Grazie per aver confermato il tuo indirizzo email, a breve riceverai il tuo QRCode!", "success")
            subject = f"Gentile {user.nome} hai ricevuto con successo il tuo personale QRCode di Campus Diffuso!"
            html = render_template("qrcode.html", img_data=[
                img_to_base64("/static/picture/campus-diffuso-green.jpg"),
                img_to_base64(f"/static/media/{qr_filename}")
            ])
            send_email(user.email, subject, html)
    db.session.close()
    return render_template("register.html", title="Confirm Token", form=form)
