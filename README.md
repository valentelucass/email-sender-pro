# 📧 Email Sender Pro

Sistema profissional de envio de emails em massa com interface web moderna.

## 🚀 Deploy Rápido no Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/seu-usuario/email-sender-pro)

## ✨ Funcionalidades

- **Interface Web Moderna**: Design responsivo com animações
- **Upload de Planilhas**: Arraste arquivos Excel (.xlsx)
- **Gmail Integration**: Suporte completo a Senha de App
- **Logs em Tempo Real**: Acompanhe o progresso visualmente
- **Personalização**: Templates com variáveis `{nome}` e `{email}`
- **Seguro**: Cada usuário usa suas próprias credenciais

## 📋 Como Usar

### 1. Prepare sua Planilha Excel
Crie um arquivo `.xlsx` com as colunas:

| Nome | E-mail |
|------|--------|
| João Silva | joao@email.com |
| Maria Santos | maria@email.com |

### 2. Configure Gmail
1. **Ative 2FA** na sua conta Google
2. **Gere Senha de App**:
   - Acesse: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Selecione "Mail" → "Outro (personalizado)"
   - Copie a senha de 16 caracteres
3. **Use no formulário**:
   - Gmail: `seuemail@gmail.com`
   - Senha de App: `abcd efgh ijkl mnop`
   - Servidor: `smtp.gmail.com`
   - Porta: `587`

### 3. Envie sua Campanha
1. Faça upload da planilha
2. Preencha credenciais Gmail
3. Personalize o template:
   ```
   Olá {nome},
   
   Esperamos que esteja bem!
   
   Atenciosamente,
   Equipe
   ```
4. Clique em "Enviar Campanha"

## 🛠️ Desenvolvimento Local

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd email_sender

# Instale dependências
pip install -r requirements.txt

# Execute
python app.py
```

Acesse: http://localhost:8000

## 📁 Estrutura

```
email_sender/
├── app.py              # Servidor Flask
├── vercel.json         # Configuração Vercel
├── requirements.txt    # Dependências
├── src/                # Core do sistema
│   ├── email_sender.py # Lógica de envio
│   ├── excel_reader.py # Leitura de planilhas
│   └── config.py       # Configurações
└── web/                # Interface
    ├── index.html      # Página principal
    ├── help.html       # Ajuda
    ├── main.js         # JavaScript
    └── styles.css      # Estilos
```

## 🔒 Segurança

- Headers de segurança (XSS, CSRF protection)
- Credenciais nunca são salvas
- CORS restrito para produção
- Validações rigorosas

## 📊 Limites Gmail

- **Conta Pessoal**: ~100 emails/dia
- **G Suite**: ~2000 emails/dia
- **Intervalo**: 2-5 segundos entre envios

## 🚨 Solução de Problemas

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
