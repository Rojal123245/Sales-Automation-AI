import os
import time
import logging
import requests
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

class WarehouseAutomation:
    """Class for automating interactions with warehouse ordering systems."""
    
    def __init__(self, config: Dict):
        """
        Initialize the warehouse automation with configuration.
        
        Args:
            config: Dictionary containing configuration settings
        """
        self.config = config
        self.warehouse_config = config.get('automation', {}).get('warehouse', {})
        self.base_url = self.warehouse_config.get('base_url')
        self.timeout = self.warehouse_config.get('timeout', 30)
        self.retry_attempts = self.warehouse_config.get('retry_attempts', 3)
        
        # Load credentials from .env file
        load_dotenv(config.get('automation', {}).get('credentials', {}).get('env_file', '.env'))
        self.username = os.getenv('WAREHOUSE_USERNAME')
        self.password = os.getenv('WAREHOUSE_PASSWORD')
        self.api_key = os.getenv('WAREHOUSE_API_KEY')
        
        # Initialize web driver only when needed
        self.driver = None
    
    def _initialize_driver(self) -> None:
        """Set up and initialize the Selenium WebDriver."""
        logger.info("Initializing Chrome WebDriver")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.timeout)
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
            raise
    
    def login(self) -> bool:
        """
        Log in to the warehouse system.
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        if not self.driver:
            self._initialize_driver()
        
        try:
            logger.info("Attempting to login to warehouse system")
            login_url = f"{self.base_url}/login"
            self.driver.get(login_url)
            
            # Wait for login form to load
            username_input = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_input = self.driver.find_element(By.ID, "password")
            
            # Enter credentials
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            
            # Submit form
            login_button = self.driver.find_element(By.ID, "login-button")
            login_button.click()
            
            # Wait for successful login (could be a dashboard element or similar)
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
            )
            
            logger.info("Successfully logged in to warehouse system")
            return True
            
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"Login failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return False
    
    def place_order(self, items: List[Dict]) -> Tuple[bool, str]:
        """
        Place an order for a list of items.
        
        Args:
            items: List of dictionaries containing item details
                  (item_code, name, quantity, etc.)
        
        Returns:
            Tuple[bool, str]: (Success status, Order ID or error message)
        """
        # Check if items is empty
        if not items:
            logger.warning("No items to order")
            return False, "No items to order"
        
        # Try API-based ordering first, if it fails fall back to UI automation
        api_success, api_result = self._place_order_api(items)
        if api_success:
            return True, api_result
        
        # Fall back to UI automation
        return self._place_order_ui(items)
    
    def _place_order_api(self, items: List[Dict]) -> Tuple[bool, str]:
        """
        Attempt to place an order using the warehouse API.
        
        Args:
            items: List of dictionaries containing item details
        
        Returns:
            Tuple[bool, str]: (Success status, Order ID or error message)
        """
        logger.info("Attempting to place order via API")
        
        order_endpoint = f"{self.base_url}{self.warehouse_config.get('order_endpoint')}"
        
        payload = {
            "items": items,
            "order_date": time.strftime("%Y-%m-%d"),
            "priority": "normal"
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    order_endpoint, 
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 201:  # Created
                    order_id = response.json().get("order_id")
                    logger.info(f"Order successfully placed via API. Order ID: {order_id}")
                    return True, order_id
                else:
                    logger.warning(f"API order failed: {response.status_code} - {response.text}")
                    # If unauthorized, don't retry
                    if response.status_code in (401, 403):
                        return False, f"Authentication failed: {response.status_code}"
            
            except requests.exceptions.RequestException as e:
                logger.error(f"API order attempt {attempt+1} failed: {str(e)}")
                # Wait before retrying
                time.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error("All API order attempts failed")
        return False, "API ordering failed after multiple attempts"
    
    def _place_order_ui(self, items: List[Dict]) -> Tuple[bool, str]:
        """
        Place an order using the UI automation as a fallback.
        
        Args:
            items: List of dictionaries containing item details
        
        Returns:
            Tuple[bool, str]: (Success status, Order ID or error message)
        """
        if not self.driver:
            self._initialize_driver()
            
        # Ensure we're logged in
        if not self.login():
            return False, "Failed to log in to warehouse system"
        
        try:
            logger.info("Placing order via UI automation")
            
            # Navigate to the order page
            self.driver.get(f"{self.base_url}/orders/new")
            
            # Wait for the order form to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "order-form"))
            )
            
            # For each item, add it to the order
            for item in items:
                # Click add item button
                add_item_button = self.driver.find_element(By.ID, "add-item-button")
                add_item_button.click()
                
                # Wait for the item form row to appear
                WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "item-row"))
                )
                
                # Find the last item row (the one we just added)
                item_rows = self.driver.find_elements(By.CLASS_NAME, "item-row")
                current_row = item_rows[-1]
                
                # Fill in the item details
                item_code_input = current_row.find_element(By.NAME, "item_code")
                item_code_input.send_keys(item.get("item_code", ""))
                
                quantity_input = current_row.find_element(By.NAME, "quantity")
                quantity_input.send_keys(str(item.get("quantity", 0)))
            
            # Submit the order
            submit_button = self.driver.find_element(By.ID, "submit-order")
            submit_button.click()
            
            # Wait for confirmation page or order ID
            order_id_element = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.ID, "order-confirmation"))
            )
            
            # Extract the order ID
            order_id = order_id_element.text.strip()
            logger.info(f"Order successfully placed via UI. Order ID: {order_id}")
            
            return True, order_id
            
        except (TimeoutException, NoSuchElementException) as e:
            error_msg = f"UI order placement failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during UI order placement: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        finally:
            # Take a screenshot on error for debugging
            if self.driver:
                try:
                    self.driver.save_screenshot("error_screenshot.png")
                except Exception:
                    pass
    
    def close(self) -> None:
        """Close the WebDriver and clean up resources."""
        if self.driver:
            logger.info("Closing WebDriver")
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None 