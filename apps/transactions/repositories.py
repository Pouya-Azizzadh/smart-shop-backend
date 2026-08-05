from .models import Transaction


class TransactionRepository:
    @staticmethod
    def create(**kwargs):
        return Transaction.objects.create(**kwargs)

    @staticmethod
    def get_by_idempotency_key(key):
        return Transaction.objects.filter(idempotency_key=key).first()

    @staticmethod
    def list_for_user(user):
        return Transaction.objects.filter(user=user).select_related("product")
