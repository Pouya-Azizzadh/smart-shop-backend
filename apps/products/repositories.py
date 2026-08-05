from .models import Product


class ProductRepository:
    @staticmethod
    def get_by_id(product_id):
        return Product.objects.filter(pk=product_id).first()

    @staticmethod
    def get_by_sku(sku):
        return Product.objects.filter(sku=sku).first()

    @staticmethod
    def list_all():
        return Product.objects.all()
