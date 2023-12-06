from app.entities.models import User
from app.gateways.database import UserRepository

class ExampleUseCase:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_user(self, user_id):
        user = self.user_repository.get_user_by_id(user_id)
        return user

    def create_user(self, username, email):
        new_user = User(id=None, username=username, email=email)
        self.user_repository.save_user(new_user)
        return new_user