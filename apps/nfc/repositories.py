from .models import NFCTag


class NFCTagRepository:
    @staticmethod
    def get_active_by_uuid(tag_uuid):
        return (
            NFCTag.objects.select_related("assigned_product")
            .filter(uuid=tag_uuid, is_active=True)
            .first()
        )

    @staticmethod
    def get_by_uuid(tag_uuid):
        return (
            NFCTag.objects.select_related("assigned_product")
            .filter(uuid=tag_uuid)
            .first()
        )
