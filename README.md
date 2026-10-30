# Semana 14 — Flasky

Continuação da Semana 13 de Taissa Pieri, PT3038084, p.taissa@aluno.ifsp.edu.br.

## Funcionalidades

- Cadastro, listagem, edição do nome/e-mail e exclusão com confirmação.
- Novos cadastros notificam flaskaulasweb@zohomail.com, o e-mail institucional e o e-mail digitado. Endereços repetidos recebem uma única notificação.
- Nome da aluna, prontuário e usuário constam no corpo HTML e texto da mensagem.
- SendGrid por HTTPS; os destinatários ficam no campo To.
- Edição e exclusão não enviam novas notificações. O histórico de e-mails é preservado mesmo quando o usuário é excluído ou renomeado.
- A confirmação de exclusão é uma página; a remoção só ocorre com POST e token CSRF válido.
- Sessão atualizada ao renomear e limpa ao excluir o usuário apresentado na saudação.

## Módulos

| Arquivo | Responsabilidade |
| --- | --- |
| config.py | Configurações por ambiente e identificação acadêmica |
| app/__init__.py | Fábrica da aplicação e extensões |
| app/models.py | User, Role e EmailEnviado |
| app/main/forms.py | Formulários de cadastro, edição e exclusão |
| app/main/views.py | Rotas e operações no banco |
| app/main/errors.py | Páginas de erro |
| app/email.py | Integração SendGrid |
| app/templates/ | Páginas e mensagens de e-mail |
| app/static/ | Estilos |
| migrations/ | Histórico de alterações do banco |
| tests/ | Testes automatizados com e-mail simulado |
| flasky.py | Entrada e comandos Flask |

## GitHub e PythonAnywhere — instalação separada

1. Crie um repositório chamado Semana-14-Flasky no GitHub.
2. Extraia este ZIP e envie o conteúdo da pasta Semana14_Flasky para a raiz do repositório. Não envie a pasta externa nem o ZIP.
3. No Bash do PythonAnywhere, execute uma linha de cada vez:

```bash
cd ~
git clone https://github.com/ptaissa-ai/Semana-14-Flasky.git
cd Semana-14-Flasky
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

4. Crie o arquivo .env em /home/taissapieri/Semana-14-Flasky. Pode copiar o .env privado da Semana 13 se o serviço de e-mail já funcionava. O arquivo deve conter:

```dotenv
FLASK_CONFIG=production
SECRET_KEY=SUA_CHAVE_SECRETA
API_URL=https://api.sendgrid.com/v3/mail/send
API_KEY=SUA_CHAVE_SENDGRID
API_FROM=SEU_REMETENTE_VERIFICADO
FLASKY_ADMIN=flaskaulasweb@zohomail.com
```

Gere uma chave secreta, se necessário, com:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Não envie .env, venv ou banco ao GitHub. API_FROM deve conter apenas o endereço verificado no SendGrid. O arquivo .env.example é um modelo sem credenciais.

5. Inicialize o banco e teste:

```bash
python -m flask --app flasky db upgrade
python -m flask --app flasky seed-roles
python -m flask --app flasky test
```

6. Na aba Web, a versão Python deve ser a mesma do venv. Ajuste Source code e Working directory para /home/taissapieri/Semana-14-Flasky, e Virtualenv para /home/taissapieri/Semana-14-Flasky/venv.
7. No arquivo WSGI da aba Web, use:

```python
import os
import sys
project = '/home/taissapieri/Semana-14-Flasky'
if project not in sys.path:
    sys.path.insert(0, project)
os.environ['FLASK_CONFIG'] = 'production'
from flasky import app as application
```

8. Se houver mapeamento /static/, ajuste o diretório para /home/taissapieri/Semana-14-Flasky/app/static. Clique Reload.
9. Teste um cadastro inédito, confira os e-mails, edite o cadastro e teste Cancelar e Confirmar exclusão. Repetir um nome já cadastrado não envia nova notificação.

Mudar os caminhos da aplicação existente na aba Web faz seu endereço atual passar a mostrar a Semana 14; a pasta e o repositório da Semana 13 permanecem preservados.

## Banco da Semana 13 (opcional)

A instalação separada começa com banco vazio. Para preservar os cadastros, antes da publicação faça backup do banco da Semana 13. Copie esse banco para instance/app.db da Semana 14, antes de executar db upgrade. A nova revisão acrescenta somente a coluna email, sem apagar os cadastros. Usuários anteriores ficam com e-mail não informado; ele poderá ser preenchido em Editar. Não execute db init nem stamp para esse fluxo: a base da Semana 13 já usa a migração inicial.

## Comportamento e limites

Aplicação acadêmica sem autenticação, como a base: visitantes podem editar/excluir qualquer cadastro e consultar o histórico. CSRF protege o envio dos formulários; não equivale a controle de acesso. Não use dados sensíveis nessa demonstração pública.

A API HTTP 202 indica aceitação pelo SendGrid, não confirmação de entrega. Confira o painel do provedor e spam. O cadastro é revertido se o envio não for aceito. Uma falha de rede após o aceite pode causar duplicação numa nova tentativa, comportamento herdado da Semana 13.

Não houve publicação nem envio real de mensagens durante a criação desta versão.

Referência funcional consultada: https://teixeif.pythonanywhere.com/ (cadastro, listagem, editar e excluir).
Base: https://github.com/ptaissa-ai/Semana-13-Flasky.

## Validação desta entrega

14 testes aprovados com o provedor simulado. Migrações verificadas em banco vazio e em banco da Semana 13 com usuário existente, preservado após a atualização.
