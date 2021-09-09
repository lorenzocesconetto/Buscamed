from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import EditProfileForm, LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email, send_email_confirmation_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(form.password.data):
            flash('Email ou senha inválidos.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Entrar', form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.cep = form.cep.data
        current_user.logradouro = form.logradouro.data
        current_user.complemento = form.complemento.data
        current_user.bairro = form.bairro.data
        current_user.municipio = form.municipio.data
        current_user.uf = form.uf.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('Obrigado por atualizar seus dados :)')
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.cep.data = current_user.cep
        form.logradouro.data = current_user.logradouro
        form.complemento.data = current_user.complemento
        form.bairro.data = current_user.bairro
        form.municipio.data = current_user.municipio
        form.uf.data = current_user.uf
        form.phone.data = current_user.phone
    return render_template('auth/edit_profile.html', title='Editar perfil', form=form)


@bp.route('/login_msg')
def login_msg():
    flash('Faça o login ou cadastre-se gratuitamente para realizar compras')
    return redirect(url_for('auth.login'))


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User(email=email,
                    name=form.name.data,
                    cep=form.cep.data,
                    logradouro=form.logradouro.data,
                    complemento=form.complemento.data,
                    bairro=form.bairro.data,
                    municipio=form.municipio.data,
                    uf=form.uf.data,
                    phone=form.phone.data
                    )
        # phone=form.phone.data, address=form.address.data
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        send_email_confirmation_email(user)
        flash('Parabéns, agora você pode aproveitar os melhores preços de farmácias!')
        login_user(user, remember=True)
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        flash('Você já está logado')
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
        flash('Verifique seu email para instruções de como redefinir sua senha.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Sua senha foi redefinida.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/email_confirmation/<token>')
def email_confirmation(token):
    user = User.verify_email_confirmation_token(token)
    if user and not user.confirmed:
        login_user(user)
        user.confirmed = True
        db.session.commit()
        flash('Obrigado por confirmar seu email :)')
        return redirect(url_for('main.index'))
    elif user and user.confirmed:
        flash('O email já foi confirmado anteriormente.')
    else:
        flash('Algo deu errado, o email de confirmação só é válido por 1(uma) hora.')
    return redirect(url_for('auth.login'))
