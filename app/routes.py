from flask import render_template, redirect, flash, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, bcrypt, mail, Message
from app.forms import Sign_Up_Form, Sign_In_Form, Image_Form, Change_Pass_Form
from app.models import user
from datetime import datetime
from PIL import Image
import secrets, os, pyotp

@app.route('/')
def home_page():
    return render_template("index.html")

def save_image(image_info):
    random_hex = secrets.token_hex(8)
    _ , ext = os.path.splitext(image_info.filename)
    img_full_name = random_hex + ext
    save_path = os.path.join(app.root_path , "static/uploads" , img_full_name)

    image = Image.open(image_info)
    new_image = image.resize((340, 340))
    new_image.save(save_path)

    return img_full_name

@app.route('/sign-up', methods=["GET", "POST"])
def sign_up_page():
    form=Sign_Up_Form()
    
    if request.method == "POST":
        if form.validate_on_submit():
            user_info = user(
                             first_name=form.first_name.data,
                             last_name=form.last_name.data,
                             username=form.username.data,
                             email=form.email.data,
                             password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
                             date=datetime.now(),
                             profile_img=save_image(form.img.data)
                            )
            db.session.add(user_info)
            db.session.commit()
            login_user(user_info)
            msg = Message(body="Hello, A new account on our website has been created. Hope you like it!\n\n\nThank You, Best Regards.",
					     recipients=[f"{current_user.email}"],
                         subject="New account created!")
            mail.send(msg)
            flash("Successfully Created Account!", category="success")
            return redirect(url_for('home_page'))
        else:
            flash("Couldn't create account!", category="danger")
            return render_template('sign_up.html', form=form)
    if request.method == "GET":
        return render_template('sign_up.html', form=form)

@app.route('/account-page', methods=["GET", "POST"])
@login_required
def account_page():
    form=Image_Form()
    display_image=url_for('static', filename=f'uploads/{current_user.profile_img}')
    if request.method == "POST":
        if "remove" in request.form:
            current_user.profile_img = "default.png"
            db.session.commit()
            return redirect(url_for('account_page'))

        elif "upload_new" in request.form:
            if form.validate_on_submit():
                current_user.profile_img = save_image(form.img.data)
                db.session.commit()
                return redirect(url_for('account_page'))
            else:
                flash("Only '.png', '.jpg', '.jpeg' files are allowed!", category="danger")

    return render_template('account.html', display_image=display_image, form=form)

@app.route('/edit-acc', methods=["GET", "POST"])
@login_required
def edit_acc_page():
    form=Sign_Up_Form()
    cp_form=Change_Pass_Form()
    if request.method == "POST":
        if "submit" in request.form:
            if form.username.data != current_user.username:
                if user.query.filter_by(username=form.username.data).first():
                    flash("Username is already been used! Try something different!", category="danger")
                    return render_template('edit_account.html', form=form, cp_form=cp_form)
                else:
                    current_user.username=form.username.data
            if form.email.data != current_user.email:
                if user.query.filter_by(email=form.email.data).first():
                    flash("This email id is already been used! Try something different!", category="danger")
                    return render_template('edit_account.html', form=form, cp_form=cp_form)
                else:
                    current_user.email = form.username.data
            if form.first_name.data != current_user.first_name:
                    current_user.first_name = form.first_name.data
            if form.last_name.data != current_user.last_name:
                    current_user.last_name = form.last_name.data
            if request.form.get("bio") != current_user.bio:
                    current_user.bio = request.form.get("bio")

            db.session.commit()
            flash("Your account information was changed!", category="success")
            return redirect(url_for('edit_acc_page'))
        
        if "change_password" in request.form:
            if cp_form.validate_on_submit():
                current_password = bcrypt.check_password_hash(current_user.password, cp_form.old_password.data)
                new_password = bcrypt.check_password_hash(current_user.password, cp_form.new_password.data)
                if current_password:
                    if not new_password:
                        password = bcrypt.generate_password_hash(cp_form.new_password.data).decode('utf-8')
                        current_user.password = password
                        flash("Changed Password!", category="success")
                        return redirect(url_for('edit_acc_page'))
                    else:
                        flash("Please try a new password!", category="danger")
                else:
                    flash("Old password doesn't password!", category="danger")

            else:
                flash("Sorry error happend!", category="danger")
                return render_template('edit_account.html', form=form, cp_form=cp_form)
            
    return render_template('edit_account.html', form=form, cp_form=cp_form)

@app.route('/forgot-password', methods=["GET", "POST"])
@login_required
def forgot_pass_page():
    if request.method == "POST":
        if "email" in request.form:
            email=request.form.get('email')
            if email:
                totp = pyotp.TOTP('base32secret3232')
                otp = totp.now()
                session['otp']=otp
                msg = Message(subject="Reset Password",
                            recipients=[f"{email}"],
                            body=f"Hi Hrittika,\n\nIt seems you have forgotten your password. Here is your one time password. Please use it before it expires:\n\n{otp}\n\nIf you do not wish to change your password, feel free to ignore this message.\n\nCheers,\n\t- The Penzu Team")
                mail.send(msg)
                flash(f'Sent an otp to "{email}"! Plz verify to change password.', category="primary")
                return redirect(url_for('forgot_pass_page'))
        if "otp_submit" in request.form:
            otp_to_check = request.form.get("otp")
            if otp_to_check:
                if str(otp_to_check) == session.get('otp'):
                    return redirect(url_for('change_pass_page'))
                else:
                    flash("Otp didn't match!", category="danger")
                    return render_template("forgot_password.html")
    if request.method == "GET":
        return render_template("forgot_password.html")

@app.route('/change-password', methods=["GET", "POST"])
@login_required
def change_pass_page():
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_new_pass = request.form.get("confirm_new_pass")
        if new_password and confirm_new_pass:
            if len(new_password) >= 8:
                if new_password == confirm_new_pass:
                    password=bcrypt.generate_password_hash(confirm_new_pass)
                    current_user.password = password
                    db.session.commit()
                    flash("Changed Password! Signin again to enjoy!", category="info")
                    logout_user()
                    return redirect(url_for('sign_in_page'))
                else:
                    flash("Passwords don't match!", category="danger")
            else:
                flash("Password must be longer than or equal to 8!", category="danger")

    return render_template("change_password.html")

@app.route('/sign-in', methods=["GET", "POST"])
def sign_in_page():
    form=Sign_In_Form()

    if request.method == "POST":
        if form.validate_on_submit():
            attemted_user=user.query.filter_by(username=form.username.data).first()
            if attemted_user:
                password_match=bcrypt.check_password_hash(attemted_user.password, form.password.data)
                if password_match:
                    login_user(attemted_user)
                    flash(f"Successfully Signed-In as {current_user.username}", category="success")
                    return redirect(url_for('home_page'))
                else:
                    flash("Passwords don't match!", category="danger")
                    return render_template('sign_in.html', form=form)
            else:
                flash("Couldn't find any user with this username!", category="danger")
                return render_template('sign_in.html', form=form)
    if request.method == "GET":
        return render_template('sign_in.html', form=form)

@app.route('/sign-out')
def sign_out_page():
    logout_user()
    flash('Signed Out!', category="success")
    return redirect(url_for('home_page'))