from flask import Flask, jsonify, render_template, request
from app.use_cases.example_use_case import ExampleUseCase
from app.gateways.database import UserRepository
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

user_repository = UserRepository()
example_use_case = ExampleUseCase(user_repository)

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

# ... other route
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = example_use_case.get_user(user_id)
    return jsonify({"id": user.id, "username": user.username, "email": user.email})

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    new_user = example_use_case.create_user(username, email)
    return jsonify({"id": new_user.id, "username": new_user.username, "email": new_user.email})

if __name__ == '__main__':
    app.run(debug=True)
