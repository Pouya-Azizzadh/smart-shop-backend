from rest_framework import generics, permissions

from .repositories import TransactionRepository
from .serializers import TransactionSerializer


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return TransactionRepository.list_for_user(self.request.user)
