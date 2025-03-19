import os
import yaml
from django.core.management.base import BaseCommand
from ...models import Product, Supplier


class Command(BaseCommand):
    help = 'Import products from a YAML file'

    def handle(self, *args, **kwargs):
        # Get the path to the YAML file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        yaml_file_path = os.path.join(base_dir, 'data', 'shop1.yaml')

        # Open and read the YAML file
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

            # Get or create the supplier from the shop data
            supplier = Supplier.objects.get_or_create(name=data['shop'])[0]

            # Create products for each item in the goods list
            for product in data['goods']:
                Product.objects.create(
                    name=product['name'],
                    supplier=supplier,
                    price=product['price'],
                    quantity=product['quantity'],
                    parameters=product['parameters']
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported products'))