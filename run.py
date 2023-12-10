from app.adapters.controllers import app

app.secret_key = 'mOteKso2023!'

if __name__ == '__main__':
    app.run(debug=True)