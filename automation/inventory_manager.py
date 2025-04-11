import pandas as pd
import logging
from typing import Dict, List
from datetime import datetime
import json
import os
from .warehouse_client import FakeStoreClient
from .report_generator import OrderReportGenerator

class InventoryManager:
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.store_client = FakeStoreClient(config)
        self.min_threshold = config['automation']['order_settings']['min_threshold']
        self.product_cache = {}
        self.report_generator = OrderReportGenerator()
        
    def update_product_cache(self):
        """Update local cache of available products"""
        products = self.store_client.get_all_products()
        self.product_cache = {str(p['id']): p for p in products}
        
        # Save cache to file
        cache_file = "data/cache/product_cache.json"
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(self.product_cache, f, indent=2)
            
        self.logger.info(f"Updated product cache with {len(products)} products")
        
    def process_predictions(self, predictions_df: pd.DataFrame) -> List[Dict]:
        """Process model predictions and create orders"""
        if not self.product_cache:
            self.logger.info("Product cache empty, updating cache...")
            self.update_product_cache()
        
        # Debug information about the DataFrame
        self.logger.info(f"DataFrame columns: {predictions_df.columns.tolist()}")
        self.logger.info(f"DataFrame shape: {predictions_df.shape}")
        self.logger.info(f"First few rows:\n{predictions_df.head()}")
        
        orders_to_place = []
        
        # Debug print the threshold
        self.logger.info(f"Current min_threshold: {self.min_threshold}")
        
        for _, row in predictions_df.iterrows():
            try:
                product_id = str(row['Item Code'])
                current_stock = float(row['Stock Left'])
                predicted_demand = float(row['Predicted Sales'])
                
                self.logger.info(f"Processing product {product_id}:")
                self.logger.info(f"  - Current stock: {current_stock}")
                self.logger.info(f"  - Predicted demand: {predicted_demand}")
                self.logger.info(f"  - Min threshold: {self.min_threshold}")
                
                if current_stock <= self.min_threshold:
                    # Get product details
                    product = self.product_cache.get(product_id)
                    if not product:
                        self.logger.warning(f"Product {product_id} not found in cache")
                        product = self.store_client.get_product(product_id)
                        if product:
                            self.product_cache[product_id] = product
                    
                    if product:
                        order_quantity = self._calculate_order_quantity(
                            current_stock=current_stock,
                            predicted_demand=predicted_demand
                        )
                        
                        self.logger.info(f"Adding order for {product_id}: Quantity={order_quantity}")
                        
                        orders_to_place.append({
                            'productId': product.get('id', product_id),
                            'quantity': order_quantity,
                            'predicted_demand': predicted_demand,
                            'unit_price': float(product.get('price', row.get('Price', 0))),
                            'title': product.get('title', row.get('Item Name', f"Product {product_id}"))
                        })
                    else:
                        self.logger.warning(f"Could not find product details for {product_id}")
            
            except Exception as e:
                self.logger.error(f"Error processing product {product_id}: {str(e)}")
                self.logger.error(f"Row data: {row.to_dict()}")
                continue
        
        self.logger.info(f"Total orders to place: {len(orders_to_place)}")
        return orders_to_place

    def _calculate_order_quantity(self, current_stock: int, predicted_demand: float) -> int:
        """Calculate optimal order quantity"""
        safety_margin = self.config['automation']['order_settings']['safety_stock_margin']
        suggested_quantity = int((predicted_demand * safety_margin) - current_stock)
        return max(1, suggested_quantity)

    def execute_orders(self, predictions_path: str) -> Dict:
        """Execute orders based on predictions"""
        try:
            # Load predictions
            self.logger.info(f"Loading predictions from: {predictions_path}")
            predictions_df = pd.read_csv(predictions_path)
            
            # Process predictions
            orders_to_place = self.process_predictions(predictions_df)
            
            if not orders_to_place:
                self.logger.warning("No orders to place - check min_threshold and stock levels")
                return {"status": "success", "message": "No orders required"}
            
            # Group orders into carts
            cart_data = {
                "userId": 1,
                "date": datetime.now().isoformat(),
                "products": [
                    {"productId": order['productId'], "quantity": order['quantity']}
                    for order in orders_to_place
                ]
            }
            
            self.logger.info(f"Placing order with cart data: {cart_data}")
            
            # Place order
            order_response = self.store_client.create_order(cart_data)
            
            if order_response:
                # Calculate total cost
                total_cost = sum(item['quantity'] * item['unit_price'] for item in orders_to_place)
                
                # Prepare report data with safer DataFrame lookup
                report_data = {
                    "cart_id": order_response.get('id', 'unknown'),
                    "orders": []
                }
                
                for item in orders_to_place:
                    product_id = str(item['productId'])
                    # Safely get current stock
                    current_stock = 'N/A'
                    matching_rows = predictions_df[predictions_df['Item Code'].astype(str) == product_id]
                    if not matching_rows.empty:
                        current_stock = matching_rows['Stock Left'].iloc[0]
                    
                    report_data['orders'].append({
                        **item,
                        "current_stock": current_stock
                    })
                
                report_data['total_cost'] = total_cost
                
                self.logger.info("Generating PDF report...")
                pdf_path = self.report_generator.generate_order_report(report_data)
                
                # Save order record
                self._save_order_record(orders_to_place, order_response)
                
                return {
                    "status": "success",
                    "cart_id": order_response.get('id'),
                    "items_ordered": len(orders_to_place),
                    "total_cost": total_cost,
                    "report_path": pdf_path
                }
            else:
                self.logger.error("Failed to get response from store client")
                return {"status": "error", "message": "Failed to place order"}
            
        except Exception as e:
            self.logger.error(f"Order execution failed: {str(e)}")
            self.logger.exception("Full traceback:")
            return {"status": "error", "message": str(e)}

    def _save_order_record(self, orders: List[Dict], response: Dict):
        """Save order details to file"""
        try:
            order_record = {
                "cart_id": response.get('id'),
                "timestamp": datetime.now().isoformat(),
                "orders": orders,
                "api_response": response
            }
            
            # Save to orders directory
            orders_dir = "data/orders"
            os.makedirs(orders_dir, exist_ok=True)
            
            filename = f"{orders_dir}/order_{order_record['cart_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(order_record, f, indent=2)
                
            self.logger.info(f"Order record saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save order record: {str(e)}")
