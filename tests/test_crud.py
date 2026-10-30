from tests import test_basics
import unittest
from app import db
from app.models import User, Role, EmailEnviado
from unittest.mock import patch
import re


class CrudTestCase(unittest.TestCase):
    tearDown = test_basics.BasicsTestCase.tearDown
    def setUp(self):
        test_basics.BasicsTestCase.setUp(self)
        user = User(username='Ana', email='ana@example.com',
                    role=Role.query.filter_by(name='User').first())
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

    # Only CRUD tests are inherited in this class; base tests run in their own module.
    def test_edit(self):
        with self.client.session_transaction() as sess:
            sess['name'] = 'Ana'
        with patch('app.main.views.send_email') as mail:
            response = self.client.post(f'/usuarios/{self.user_id}/editar',
                data={'username': 'Ana Maria', 'email': 'nova@example.com'}, follow_redirects=True)
            self.assertIn('Usuário atualizado', response.text)
            mail.assert_not_called()
        user = db.session.get(User, self.user_id)
        self.assertEqual((user.username, user.email), ('Ana Maria', 'nova@example.com'))
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['name'], 'Ana Maria')

    def test_edit_duplicate_and_invalid(self):
        db.session.add(User(username='Bia', role=Role.query.filter_by(name='User').first()))
        db.session.commit()
        for data in ({'username': 'Bia', 'email': 'b@example.com'},
                     {'username': '   ', 'email': 'a@example.com'},
                     {'username': 'Outro', 'email': 'invalido'}):
            self.client.post(f'/usuarios/{self.user_id}/editar', data=data)
            user = db.session.get(User, self.user_id)
            self.assertEqual((user.username, user.email), ('Ana', 'ana@example.com'))

    def test_delete_confirmation_and_history(self):
        db.session.add(EmailEnviado(destinatario='ana@example.com', assunto='Cadastro',
            usuario='Ana', prontuario='PT3038084', nome_aluno='Taissa Pieri'))
        db.session.commit()
        with self.client.session_transaction() as sess:
            sess['name'] = 'Ana'
        page = self.client.get(f'/usuarios/{self.user_id}/excluir')
        self.assertIn('Confirmar exclusão', page.text)
        self.assertIsNotNone(db.session.get(User, self.user_id))
        with patch('app.main.views.send_email') as mail:
            self.client.post(f'/usuarios/{self.user_id}/excluir')
            mail.assert_not_called()
        self.assertIsNone(db.session.get(User, self.user_id))
        self.assertEqual(EmailEnviado.query.count(), 1)
        with self.client.session_transaction() as sess:
            self.assertNotIn('name', sess)

    def test_missing_user(self):
        for action in ('editar', 'excluir'):
            self.assertEqual(self.client.get(f'/usuarios/999/{action}').status_code, 404)

    def test_csrf(self):
        self.app.config['WTF_CSRF_ENABLED'] = True
        for action in ('editar', 'excluir'):
            self.client.post(f'/usuarios/{self.user_id}/{action}',
                data={'username': 'Outro', 'email': 'novo@example.com'})
            self.assertEqual(db.session.get(User, self.user_id).username, 'Ana')
        page = self.client.get(f'/usuarios/{self.user_id}/excluir').text
        token = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page).group(1)
        response = self.client.post(f'/usuarios/{self.user_id}/excluir', data={'csrf_token': token})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(db.session.get(User, self.user_id))
