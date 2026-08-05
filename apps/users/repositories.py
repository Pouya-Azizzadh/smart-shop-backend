from django.contrib.auth import get_user_model

User = get_user_model()


class UserRepository:
    @staticmethod
    def get_by_id(user_id):
        return User.objects.filter(pk=user_id).first()

    @staticmethod
    def get_by_username(username):
        return User.objects.filter(username=username).first()

    @staticmethod
    def deduct_wallet_balance(user, amount):
        user.wallet_balance -= amount
        user.save(update_fields=["wallet_balance"])
        return user

    @staticmethod
    def refresh_from_db(user):
        user.refresh_from_db()
        return user
