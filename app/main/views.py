from flask import current_app, flash, redirect, render_template, url_for, session
from sqlalchemy.exc import IntegrityError
from . import main
from .forms import NameForm, EditUserForm, DeleteUserForm
from .. import db
from ..models import Role, User, EmailEnviado
from ..email import send_email, EmailConfigurationError, EmailDeliveryError

@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            session['name'] = existing_user.username
            session['known'] = True
            flash('Bem-vindo novamente! Esse usuário já está cadastrado.', 'info')
            return redirect(url_for('.index'))
        role = Role.query.filter_by(name='User').first()
        if role is None:
            flash('Funções não inicializadas. Execute: flask seed-roles', 'danger')
            return redirect(url_for('.index'))
        user = User(username=username, email=form.email.data.strip(), role=role)
        db.session.add(user)
        try:
            recipients = [current_app.config['STUDENT_EMAIL'], current_app.config['FLASKY_ADMIN'], form.email.data.strip()]
            sent_to, subject = send_email(
                recipients, 'Novo usuário cadastrado - Semana 14', 'mail/new_user',
                student_id=current_app.config['STUDENT_ID'],
                student_name=current_app.config['STUDENT_NAME'], user=user,
            )
            for address in sent_to:
                db.session.add(EmailEnviado(
                    destinatario=address, assunto=subject, usuario=username,
                    prontuario=current_app.config['STUDENT_ID'],
                    nome_aluno=current_app.config['STUDENT_NAME'],
                ))
            db.session.commit()
            session['name'] = username
            session['known'] = False
            flash('Usuário cadastrado e envio aceito para todos os destinatários.', 'success')
        except (EmailConfigurationError, EmailDeliveryError, IntegrityError):
            db.session.rollback()
            current_app.logger.exception('Falha no cadastro ou na notificação')
            flash('Cadastro não concluído. Verifique a configuração de e-mail e tente novamente.', 'danger')
        return redirect(url_for('.index'))
    elif form.is_submitted():
        flash('Confira o nome e o e-mail informados e envie novamente.', 'danger')
    return render_template(
        'index.html', form=form, name=session.get('name'),
        known=session.get('known', False),
        users=User.query.order_by(User.id.desc()).all(),
        total_users=User.query.count(), total_roles=Role.query.count(),
        total_emails=EmailEnviado.query.count(),
    )

@main.route('/emailsEnviados')
def emails_enviados():
    emails = EmailEnviado.query.order_by(EmailEnviado.id.desc()).all()
    return render_template('emails_enviados.html', emails=emails)


@main.route('/usuarios/<int:user_id>/editar', methods=['GET', 'POST'])
def edit_user(user_id):
    user = db.get_or_404(User, user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        duplicate = User.query.filter(User.username == form.username.data,
                                      User.id != user.id).first()
        if duplicate:
            form.username.errors.append('Esse nome já pertence a outro usuário.')
        else:
            previous_name = user.username
            user.username = form.username.data
            user.email = form.email.data.strip()
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                form.username.errors.append('Esse nome já pertence a outro usuário.')
            else:
                if session.get('name') == previous_name:
                    session['name'] = user.username
                flash('Usuário atualizado com sucesso.', 'success')
                return redirect(url_for('.index'))
    return render_template('edit_user.html', form=form, user=user)


@main.route('/usuarios/<int:user_id>/excluir', methods=['GET', 'POST'])
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    form = DeleteUserForm()
    if form.validate_on_submit():
        previous_name = user.username
        db.session.delete(user)
        db.session.commit()
        if session.get('name') == previous_name:
            session.pop('name', None)
            session.pop('known', None)
        flash('Usuário excluído com sucesso. O histórico de notificações foi preservado.', 'success')
        return redirect(url_for('.index'))
    return render_template('delete_user.html', form=form, user=user)
