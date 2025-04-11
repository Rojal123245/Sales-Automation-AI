import requests
import logging
from typing import Dict, List
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json

class FakeStoreClient:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config['automation']['api']['base_url']
        self.session = requests.Session()
        self.custom_products = {}
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=config['automation']['api']['retry_attempts'],
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        self.session.mount('http://', HTTPAdapter(max_retries=retry_strategy))
        
        self.custom_products = {
            "BAGELS": {"id": 1001, "title": "Fresh Bagels", "price": 3.99, "category": "bakery"},
            "BATTERIES": {"id": 1002, "title": "AA Batteries", "price": 5.99, "category": "electronics"},
            "BLEACH": {"id": 1003, "title": "Bleach Cleaner", "price": 4.99, "category": "household"},
            "BLUEBERRIES": {"id": 1004, "title": "Fresh Blueberries", "price": 3.99, "category": "produce"},
            "BODY_LOTION": {"id": 1005, "title": "Body Lotion", "price": 7.99, "category": "personal_care"},
            "BUG_SPRAY": {"id": 1006, "title": "Insect Repellent", "price": 6.99, "category": "outdoor"},
            "BUTTER": {"id": 1007, "title": "Butter", "price": 4.99, "category": "dairy"},
            "CANNED_CORN": {"id": 1008, "title": "Canned Corn", "price": 1.99, "category": "canned_goods"},
            "CARROTS": {"id": 1009, "title": "Fresh Carrots", "price": 2.99, "category": "produce"},
            "CEREAL": {"id": 1010, "title": "Breakfast Cereal", "price": 4.99, "category": "breakfast"},
            "CHERRIES": {"id": 1011, "title": "Fresh Cherries", "price": 5.99, "category": "produce"},
            "CHOCOLATE_BAR": {"id": 1012, "title": "Chocolate Bar", "price": 2.99, "category": "snacks"},
            "COFFEE": {"id": 1013, "title": "Ground Coffee", "price": 8.99, "category": "beverages"},
            "COFFEE_MAKER": {"id": 1014, "title": "Coffee Maker", "price": 49.99, "category": "appliances"},
            "COLD_MEDICINE": {"id": 1015, "title": "Cold Medicine", "price": 7.99, "category": "pharmacy"},
            "COMB": {"id": 1016, "title": "Hair Comb", "price": 2.99, "category": "personal_care"},
            "COOKIES": {"id": 1017, "title": "Chocolate Chip Cookies", "price": 3.99, "category": "snacks"},
            "COOKWARE": {"id": 1018, "title": "Cookware Set", "price": 89.99, "category": "kitchen"},
            "COTTON_BALLS": {"id": 1019, "title": "Cotton Balls", "price": 2.99, "category": "personal_care"},
            "COTTON_SWABS": {"id": 1020, "title": "Cotton Swabs", "price": 3.49, "category": "personal_care"},
            "CROISSANTS": {"id": 1021, "title": "Fresh Croissants", "price": 4.99, "category": "bakery"},
            "DEODORANT": {"id": 1022, "title": "Deodorant", "price": 4.99, "category": "personal_care"},
            "DISH_SOAP": {"id": 1023, "title": "Dish Soap", "price": 3.99, "category": "household"},
            "DISHWARE": {"id": 1024, "title": "Dishware Set", "price": 49.99, "category": "kitchen"},
            "EARBUDS": {"id": 1025, "title": "Wireless Earbuds", "price": 29.99, "category": "electronics"},
            "EGGS": {"id": 1026, "title": "Fresh Eggs", "price": 3.99, "category": "dairy"},
            "EXTENSION_CORD": {"id": 1027, "title": "Extension Cord", "price": 9.99, "category": "electronics"},
            "FACIAL_TISSUE": {"id": 1028, "title": "Facial Tissues", "price": 3.49, "category": "household"},
            "FLOSS": {"id": 1029, "title": "Dental Floss", "price": 2.99, "category": "personal_care"},
            "FROZEN_PIZZA": {"id": 1030, "title": "Frozen Pizza", "price": 6.99, "category": "frozen"},
            "FROZEN_VEGETABLES": {"id": 1031, "title": "Frozen Vegetables", "price": 3.99, "category": "frozen"},
            "GIN": {"id": 1032, "title": "Gin", "price": 24.99, "category": "alcohol"},
            "GLASSWARE": {"id": 1033, "title": "Glassware Set", "price": 29.99, "category": "kitchen"},
            "HAIR_BRUSH": {"id": 1034, "title": "Hair Brush", "price": 5.99, "category": "personal_care"},
            "HAIR_TIE": {"id": 1035, "title": "Hair Ties Pack", "price": 3.99, "category": "personal_care"},
            "HAT": {"id": 1036, "title": "Baseball Cap", "price": 14.99, "category": "accessories"},
            "HEADPHONES": {"id": 1037, "title": "Over-ear Headphones", "price": 49.99, "category": "electronics"},
            "JELLY": {"id": 1038, "title": "Grape Jelly", "price": 3.49, "category": "condiments"},
            "LAPTOP": {"id": 1039, "title": "Laptop Computer", "price": 699.99, "category": "electronics"},
            "LAPTOP_BAG": {"id": 1040, "title": "Laptop Bag", "price": 34.99, "category": "accessories"},
            "LEMON": {"id": 1041, "title": "Fresh Lemons", "price": 0.99, "category": "produce"},
            "LETTUCE": {"id": 1042, "title": "Fresh Lettuce", "price": 2.49, "category": "produce"},
            "LIGHT_BULBS": {"id": 1043, "title": "LED Light Bulbs", "price": 8.99, "category": "household"},
            "LIME": {"id": 1044, "title": "Fresh Limes", "price": 0.79, "category": "produce"},
            "MAKEUP_REMOVER": {"id": 1045, "title": "Makeup Remover", "price": 6.99, "category": "personal_care"},
            "MATTRESS": {"id": 1046, "title": "Queen Mattress", "price": 599.99, "category": "furniture"},
            "MICROWAVE": {"id": 1047, "title": "Microwave Oven", "price": 89.99, "category": "appliances"},
            "MILK": {"id": 1048, "title": "Whole Milk", "price": 3.99, "category": "dairy"},
            "MOUTHWASH": {"id": 1049, "title": "Mouthwash", "price": 5.99, "category": "personal_care"},
            "MUFFINS": {"id": 1050, "title": "Fresh Muffins", "price": 4.99, "category": "bakery"},
            "MUGS": {"id": 1051, "title": "Coffee Mugs Set", "price": 19.99, "category": "kitchen"},
            "NAIL_CLIPPER": {"id": 1052, "title": "Nail Clipper", "price": 2.99, "category": "personal_care"},
            "NAIL_POLISH": {"id": 1053, "title": "Nail Polish", "price": 4.99, "category": "personal_care"},
            "OLIVE_OIL": {"id": 1054, "title": "Extra Virgin Olive Oil", "price": 8.99, "category": "cooking"},
            "ONIONS": {"id": 1055, "title": "Fresh Onions", "price": 1.99, "category": "produce"},
            "PAIN_RELIEVER": {"id": 1056, "title": "Pain Reliever", "price": 6.99, "category": "pharmacy"},
            "PAPER_TOWELS": {"id": 1057, "title": "Paper Towels", "price": 4.99, "category": "household"},
            "PASTA": {"id": 1058, "title": "Pasta", "price": 2.99, "category": "dry_goods"},
            "PEAS": {"id": 1059, "title": "Fresh Peas", "price": 2.49, "category": "produce"},
            "PERFUME": {"id": 1060, "title": "Perfume", "price": 49.99, "category": "personal_care"},
            "PHONE_CASE": {"id": 1061, "title": "Phone Case", "price": 14.99, "category": "electronics"},
            "PHONE_CHARGER": {"id": 1062, "title": "Phone Charger", "price": 12.99, "category": "electronics"},
            "PILLOW": {"id": 1063, "title": "Bed Pillow", "price": 19.99, "category": "bedding"},
            "PLUNGER": {"id": 1064, "title": "Toilet Plunger", "price": 7.99, "category": "household"},
            "RAZOR_BLADES": {"id": 1065, "title": "Razor Blades", "price": 14.99, "category": "personal_care"},
            "RICE": {"id": 1066, "title": "White Rice", "price": 4.99, "category": "dry_goods"},
            "RUM": {"id": 1067, "title": "Rum", "price": 19.99, "category": "alcohol"},
            "SHAMPOO": {"id": 1068, "title": "Shampoo", "price": 7.99, "category": "personal_care"},
            "SHAVING_CREAM": {"id": 1069, "title": "Shaving Cream", "price": 4.99, "category": "personal_care"},
            "SHOWER_CURTAIN": {"id": 1070, "title": "Shower Curtain", "price": 14.99, "category": "bathroom"},
            "SLOW_COOKER": {"id": 1071, "title": "Slow Cooker", "price": 39.99, "category": "appliances"},
            "SMARTPHONE": {"id": 1072, "title": "Smartphone", "price": 499.99, "category": "electronics"},
            "SOAP": {"id": 1073, "title": "Bar Soap", "price": 2.99, "category": "personal_care"},
            "SODA": {"id": 1074, "title": "Soda", "price": 1.99, "category": "beverages"},
            "SPAGHETTI": {"id": 1075, "title": "Spaghetti", "price": 2.49, "category": "dry_goods"},
            "SPINACH": {"id": 1076, "title": "Fresh Spinach", "price": 3.99, "category": "produce"},
            "SPORTS_DRINK": {"id": 1077, "title": "Sports Drink", "price": 2.49, "category": "beverages"},
            "STRAWBERRIES": {"id": 1078, "title": "Fresh Strawberries", "price": 4.99, "category": "produce"},
            "SUNBLOCK": {"id": 1079, "title": "Sunblock", "price": 8.99, "category": "personal_care"},
            "SUNGLASSES": {"id": 1080, "title": "Sunglasses", "price": 19.99, "category": "accessories"},
            "TABLET": {"id": 1081, "title": "Tablet", "price": 299.99, "category": "electronics"},
            "TEA": {"id": 1082, "title": "Tea Bags", "price": 4.99, "category": "beverages"},
            "TEQUILA": {"id": 1083, "title": "Tequila", "price": 29.99, "category": "alcohol"},
            "TOASTER": {"id": 1084, "title": "2-Slice Toaster", "price": 24.99, "category": "appliances"},
            "TOILET_BRUSH": {"id": 1085, "title": "Toilet Brush", "price": 6.99, "category": "household"},
            "TOMATO_SAUCE": {"id": 1086, "title": "Tomato Sauce", "price": 2.49, "category": "canned_goods"},
            "TOMATOES": {"id": 1087, "title": "Fresh Tomatoes", "price": 2.99, "category": "produce"},
            "TOWELS": {"id": 1088, "title": "Bath Towels", "price": 12.99, "category": "bathroom"},
            "TRASH_BAGS": {"id": 1089, "title": "Trash Bags", "price": 8.99, "category": "household"},
            "TUPPERWARE": {"id": 1090, "title": "Food Storage Containers", "price": 14.99, "category": "kitchen"},
            "VITAMINS": {"id": 1091, "title": "Multivitamins", "price": 12.99, "category": "pharmacy"},
            "VODKA": {"id": 1092, "title": "Vodka", "price": 19.99, "category": "alcohol"},
            "WHISKEY": {"id": 1093, "title": "Whiskey", "price": 34.99, "category": "alcohol"},
            "WINE": {"id": 1094, "title": "Red Wine", "price": 15.99, "category": "alcohol"}
        }
        
        # Track which products have been added to the API
        self.added_products = set()

    def add_product_to_api(self, product: Dict) -> Dict:
        """Add a product to the Fake Store API"""
        try:
            if str(product['id']) in self.added_products:
                return product

            response = self.session.post(
                f"{self.base_url}/products",
                json={
                    "title": product['title'],
                    "price": product['price'],
                    "category": product['category'],
                    "description": product.get('description', product['title']),
                    "image": product.get('image', "https://fakestoreapi.com/img/placeholder.jpg")
                }
            )
            response.raise_for_status()
            self.added_products.add(str(product['id']))
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to add product to API: {str(e)}")
            return None

    def get_all_products(self):
        """Get all products combining both API and custom products"""
        try:
            # First, ensure all custom products are added to the API
            for product in self.custom_products.values():
                self.add_product_to_api(product)

            # Get products from Fake Store API
            response = self.session.get(f"{self.base_url}/products")
            api_products = response.json() if response.status_code == 200 else []
            
            # Combine with custom products
            all_products = api_products + list(self.custom_products.values())
            return all_products
            
        except Exception as e:
            self.logger.error(f"Error fetching products: {str(e)}")
            # Return only custom products if API fails
            return list(self.custom_products.values())

    def get_product(self, product_id: str) -> Dict:
        """Get product details from API"""
        try:
            response = self.session.get(f"{self.base_url}/products/{product_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get product {product_id}: {str(e)}")
            # If API fails, try custom products
            return self.custom_products.get(product_id)

    def create_order(self, order_data: Dict) -> Dict:
        """Create a new order"""
        try:
            self.logger.info(f"Creating order with data: {order_data}")
            
            # For each product, ensure it exists in the API
            for product in order_data['products']:
                product_id = str(product['productId'])
                if product_id in self.custom_products:
                    self.logger.info(f"Adding custom product to API: {product_id}")
                    self.add_product_to_api(self.custom_products[product_id])

            response = self.session.post(
                f"{self.base_url}/carts",
                json=order_data
            )
            response.raise_for_status()
            order_response = response.json()
            self.logger.info(f"Order created successfully: {order_response}")
            return order_response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to create order: {str(e)}")
            self.logger.exception("Full traceback:")
            return None

    def get_order_status(self, cart_id: int) -> Dict:
        """Get cart/order status"""
        try:
            response = self.session.get(f"{self.base_url}/carts/{cart_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get cart status {cart_id}: {str(e)}")
            return None
