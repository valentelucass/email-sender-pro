from app import app as application

# Este arquivo é necessário para o Vercel entender que esta é uma aplicação Python
# e usar o gunicorn para servir a aplicação

if __name__ == "__main__":
    application.run()
