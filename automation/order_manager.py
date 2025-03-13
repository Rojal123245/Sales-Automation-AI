import os
import pandas as pd
import logging
from typing import Dict, List, Tuple
from .warehouse import WarehouseAutomation

# Configure logging
logger = logging.getLogger(__name__)

class OrderManager:
    """Class for managing the inventory ordering process."""
    
    def __init__(self, config: Dict):
        """
        Initialize the order manager with configuration.
        
        Args:
            config: Dictionary containing configuration settings
        """
        self.config = config
        self.order_settings = config.get('automation', {}).get('order_settings', {})
        self.min_threshold = self.order_settings.get('min_threshold', 10)
        self.max_delay_days = self.order_settings.get('max_delay_days', 7)
        
        # Initialize warehouse automation
        self.warehouse = WarehouseAutomation(config)
    
    def determine_items_to_order(self, inventory_data: pd.DataFrame) -> List[Dict]:
        """
        Analyze inventory data to determine which items need to be ordered.
        
        Args:
            inventory_data: DataFrame containing current inventory data
        
        Returns:
            List of dictionaries with items to order and quantities
        """
        logger.info("Determining items that need to be ordered")
        items_to_order = []
        
        if inventory_data.empty:
            logger.warning("Inventory data is empty")
            return []
        
        try:
            # Define required columns
            required_cols = ['Item Name', 'Item Code', 'Stock Left', 'Sales', 'Predicted Sales']
            
            # Validate and preprocess the data
            processed_data = self._preprocess_inventory_data(inventory_data, required_cols)
            
            if processed_data.empty:
                logger.warning("No valid data after preprocessing")
                return []
            
            # Process each item
            for _, row in processed_data.iterrows():
                # Skip if we have enough stock
                if row['Stock Left'] > self.min_threshold:
                    continue
                
                # Calculate how much to order based on predicted sales
                predicted_sales = row.get('Predicted Sales', 0)
                current_stock = row['Stock Left']
                
                # Order enough to cover predicted sales for max_delay_days plus a buffer
                days_to_cover = self.max_delay_days
                daily_sales_rate = predicted_sales / 30  # Assuming prediction is for a month
                quantity_to_order = int(daily_sales_rate * days_to_cover) + 5  # Add buffer of 5 units
                
                # Ensure we order at least a minimum quantity (e.g., 10 units)
                quantity_to_order = max(quantity_to_order, 10)
                
                items_to_order.append({
                    'item_code': row['Item Code'],
                    'item_name': row['Item Name'],
                    'quantity': quantity_to_order,
                    'current_stock': current_stock,
                    'predicted_sales': predicted_sales
                })
        
        except Exception as e:
            logger.error(f"Error determining items to order: {str(e)}")
        
        logger.info(f"Found {len(items_to_order)} items that need to be ordered")
        return items_to_order
    
    def _preprocess_inventory_data(self, data: pd.DataFrame, required_cols: List[str]) -> pd.DataFrame:
        """
        Validate and preprocess inventory data.
        
        Args:
            data: Raw inventory data
            required_cols: List of required columns
            
        Returns:
            Processed DataFrame with all required columns
        """
        processed_data = data.copy()
        
        # Check for missing required columns
        missing_cols = [col for col in required_cols if col not in processed_data.columns]
        
        if missing_cols:
            logger.warning(f"Missing columns in inventory data: {missing_cols}")
            
            # Try to fix missing columns if possible
            for col in missing_cols:
                if col == 'Item Code' and 'Item Name' in processed_data.columns:
                    # Generate item codes from item names
                    logger.info("Generating Item Code from Item Name")
                    processed_data['Item Code'] = processed_data['Item Name'].str.replace(' ', '_').str.upper()
                
                elif col == 'Stock Left' and 'Total Stock' in processed_data.columns:
                    # Use Total Stock as Stock Left if available
                    logger.info("Using Total Stock as Stock Left")
                    processed_data['Stock Left'] = processed_data['Total Stock']
                
                elif col == 'Predicted Sales' and 'Sales' in processed_data.columns:
                    # Use Sales as Predicted Sales if needed
                    logger.info("Using Sales as Predicted Sales")
                    processed_data['Predicted Sales'] = processed_data['Sales'] * 1.1  # Add 10% to current sales
                
                else:
                    # Cannot fix this column, data may be unusable
                    logger.error(f"Cannot generate column '{col}' from available data")
                    return pd.DataFrame()  # Return empty DataFrame
        
        # Convert columns to appropriate types
        try:
            # Ensure numeric columns are numeric
            numeric_cols = ['Stock Left', 'Sales', 'Predicted Sales']
            for col in numeric_cols:
                if col in processed_data.columns:
                    processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')
            
            # Replace NaN values with appropriate defaults
            if 'Stock Left' in processed_data.columns:
                processed_data['Stock Left'].fillna(0, inplace=True)
            if 'Sales' in processed_data.columns:
                processed_data['Sales'].fillna(0, inplace=True)
            if 'Predicted Sales' in processed_data.columns:
                processed_data['Predicted Sales'].fillna(0, inplace=True)
            
            # Check again for required columns after preprocessing
            final_missing_cols = [col for col in required_cols if col not in processed_data.columns]
            if final_missing_cols:
                logger.error(f"Still missing required columns after preprocessing: {final_missing_cols}")
                return pd.DataFrame()  # Return empty DataFrame
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error preprocessing inventory data: {str(e)}")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    def place_orders(self, items_to_order: List[Dict]) -> List[Dict]:
        """
        Process the list of items to order and place orders with the warehouse.
        
        Args:
            items_to_order: List of dictionaries with items to order
        
        Returns:
            List of dictionaries with order results
        """
        if not items_to_order:
            logger.info("No items to order")
            return []
        
        logger.info(f"Preparing to place orders for {len(items_to_order)} items")
        order_results = []
        
        try:
            # Place the order
            success, order_id_or_error = self.warehouse.place_order(items_to_order)
            
            # Record the result
            result = {
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success': success,
                'order_id': order_id_or_error if success else None,
                'error': None if success else order_id_or_error,
                'items': items_to_order
            }
            
            order_results.append(result)
            
            # Log the result
            if success:
                logger.info(f"Successfully placed order {order_id_or_error} for {len(items_to_order)} items")
            else:
                logger.error(f"Failed to place order: {order_id_or_error}")
                
        except Exception as e:
            logger.error(f"Error during order placement: {str(e)}")
            order_results.append({
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'success': False,
                'order_id': None,
                'error': str(e),
                'items': items_to_order
            })
        finally:
            # Ensure WebDriver is closed
            self.warehouse.close()
        
        return order_results
    
    def save_order_history(self, order_results: List[Dict], output_path: str = None) -> None:
        """
        Save the order history to a CSV file.
        
        Args:
            order_results: List of dictionaries with order results
            output_path: Path to save the history (default: data/orders/history.csv)
        """
        if not order_results:
            return
        
        if output_path is None:
            output_path = os.path.join('data', 'orders', 'history.csv')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            # Create a flattened DataFrame for storage
            flattened_results = []
            for result in order_results:
                for item in result['items']:
                    flattened_results.append({
                        'timestamp': result['timestamp'],
                        'success': result['success'],
                        'order_id': result['order_id'],
                        'error': result['error'],
                        'item_code': item['item_code'],
                        'item_name': item['item_name'],
                        'quantity': item['quantity'],
                        'current_stock': item['current_stock'],
                        'predicted_sales': item.get('predicted_sales', 0)
                    })
            
            # Convert to DataFrame
            df = pd.DataFrame(flattened_results)
            
            # Check if file exists to append or create new
            if os.path.exists(output_path):
                existing_df = pd.read_csv(output_path)
                df = pd.concat([existing_df, df], ignore_index=True)
            
            # Save to CSV
            df.to_csv(output_path, index=False)
            logger.info(f"Order history saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving order history: {str(e)}")
    
    def run_ordering_process(self, inventory_data: pd.DataFrame) -> Tuple[bool, List[Dict]]:
        """
        Run the complete ordering process: determine items to order, place orders, and save history.
        
        Args:
            inventory_data: DataFrame containing current inventory data
        
        Returns:
            Tuple[bool, List[Dict]]: Success status and list of order results
        """
        logger.info("Starting the ordering process")
        
        # Step 1: Determine which items need to be ordered
        items_to_order = self.determine_items_to_order(inventory_data)
        
        if not items_to_order:
            logger.info("No items need to be ordered")
            return True, []
        
        # Step 2: Place the orders
        order_results = self.place_orders(items_to_order)
        
        # Step 3: Save the order history
        self.save_order_history(order_results)
        
        # Check if any orders were successful
        success = any(result['success'] for result in order_results)
        
        return success, order_results 