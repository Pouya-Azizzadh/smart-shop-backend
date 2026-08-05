from rest_framework import generics, permissions

from .models import NFCTag
from .serializers import NFCTagSerializer


class NFCTagListView(generics.ListAPIView):
    queryset = NFCTag.objects.select_related("assigned_product").filter(is_active=True)
    serializer_class = NFCTagSerializer
    permission_classes = (permissions.IsAuthenticated,)
