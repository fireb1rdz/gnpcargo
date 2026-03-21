from abc import ABC, abstractmethod

class UserServiceInterface(ABC):
    @abstractmethod
    def create_user(self, tenant, data):
        pass

    @abstractmethod
    def update_user(self, user, data):
        pass

    @abstractmethod
    def delete_user(self, user):
        pass

    @abstractmethod
    def list_users(self, tenant):
        pass

    @abstractmethod
    def get_user(self, tenant, user_id):
        pass