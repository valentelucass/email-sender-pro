# 📨 Email Sender Pro

Ferramenta web para envio de e-mails em massa de forma simples e eficiente. Desenvolvida para facilitar o disparo de comunicações personalizadas para listas de contatos.

## 🚀 Primeiros Passos

### Pré-requisitos
- Python 3.9 ou superior
- Conta no Gmail com autenticação em duas etapas ativada
- Pacotes listados em `requirements.txt`

### Instalação Local

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/email-sender-pro.git
   cd email-sender-pro
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   python app.py
   ```
   Acesse: http://localhost:8000

## 📝 Como Usar

### Estrutura da Planilha
Crie um arquivo Excel (.xlsx) com pelo menos as colunas:
- `Nome`: Nome do destinatário
- `E-mail`: Endereço de e-mail

Exemplo:

| Nome         | E-mail             |
|--------------|-------------------|
| João Silva   | joao@email.com    |
| Maria Santos | maria@email.com   |

### Configuração do Gmail

1. **Ative a autenticação em duas etapas**
   - Acesse: [Conta Google](https://myaccount.google.com/security)
   - Ative a verificação em duas etapas

2. **Gere uma senha de app**
   - Acesse: [Senhas de App](https://myaccount.google.com/apppasswords)
   - Selecione "Mail" e "Outro (personalizado)"
   - Digite um nome (ex: "Email Sender")
   - Clique em "Gerar" e copie a senha de 16 caracteres

3. **Configure no sistema**
   - E-mail: Seu endereço Gmail completo
   - Senha: A senha de 16 caracteres gerada
   - Servidor: `smtp.gmail.com`
   - Porta: `587`

### Enviando E-mails

1. **Preparação**
   - Acesse a interface web
   - Faça upload da planilha de contatos
   - Preencha as credenciais do Gmail

2. **Personalização**
   Use variáveis no corpo da mensagem:
   ```
   Olá {nome},
   
   Seu endereço de e-mail é: {email}
   
   Atenciosamente,
   Equipe
   ```

3. **Envio**
   - Revise as configurações
   - Clique em "Enviar"
   - Acompanhe o progresso na tela

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
email-sender-pro/
├── api/               # Endpoints da API
├── src/              # Código-fonte Python
├── web/              # Arquivos estáticos (HTML, CSS, JS)
├── app.py           # Aplicação principal
├── requirements.txt  # Dependências
└── vercel.json      # Configuração do Vercel
```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta_aqui
```

## 🔒 Segurança

- As credenciais de e-mail nunca são armazenadas
- Conexões SMTP usam TLS por padrão
- Recomenda-se usar uma conta dedicada para envio de e-mails

## ⚠️ Limitações

- Limite de 500 e-mails por dia (limitação do Gmail)
- Tamanho máximo de anexo: 25MB
- Recomenda-se testar com uma pequena lista antes de disparar para muitos contatos

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙋‍♂️ Suporte

Encontrou um problema ou tem sugestões? Por favor, abra uma issue no repositório.

---

Desenvolvido com ❤️ por [Seu Nome]

**Erro de Autenticação**
- Use Senha de App, não a senha normal
- Verifique se 2FA está ativo

**Emails não chegam**
- Verifique pasta de spam
- Teste com poucos destinatários primeiro

**Erro de Conexão**
- Verifique internet
- Alguns provedores bloqueiam SMTP

## 📄 Licença

Projeto de uso educacional e pessoal.

---

**⚠️ Uso Responsável**: Use apenas com listas próprias e consentimento dos destinatários. Respeite LGPD/GDPR.
