import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional

class OrderVisualization:
    """Class for visualizing order history and automation performance."""
    
    def __init__(self, config: Dict):
        """
        Initialize visualization with configuration.
        
        Args:
            config: Dictionary containing configuration settings
        """
        self.config = config
        self.history_path = os.path.join('data', 'orders', 'history.csv')
    
    def load_history(self) -> pd.DataFrame:
        """
        Load order history from CSV file.
        
        Returns:
            DataFrame containing order history
        """
        if not os.path.exists(self.history_path):
            print(f"History file not found: {self.history_path}")
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(self.history_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Error loading history: {str(e)}")
            return pd.DataFrame()
    
    def plot_order_success_rate(self, save_path: Optional[str] = None) -> None:
        """
        Plot the success rate of orders over time.
        
        Args:
            save_path: Optional path to save the plot image
        """
        df = self.load_history()
        if df.empty:
            print("No order history data available")
            return
        
        # Group by day and calculate success rate
        df['date'] = df['timestamp'].dt.date
        success_rate = df.groupby('date')['success'].mean().reset_index()
        success_rate['success_percentage'] = success_rate['success'] * 100
        
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=success_rate, x='date', y='success_percentage')
        plt.axhline(y=100, color='green', linestyle='--', alpha=0.7, label='Target')
        
        plt.title('Order Success Rate Over Time')
        plt.xlabel('Date')
        plt.ylabel('Success Rate (%)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def plot_items_by_frequency(self, top_n: int = 10, save_path: Optional[str] = None) -> None:
        """
        Plot the most frequently ordered items.
        
        Args:
            top_n: Number of top items to display
            save_path: Optional path to save the plot image
        """
        df = self.load_history()
        if df.empty:
            print("No order history data available")
            return
        
        # Count item occurrences
        item_counts = df['item_name'].value_counts().reset_index()
        item_counts.columns = ['item_name', 'count']
        
        # Get top N items
        top_items = item_counts.head(top_n)
        
        plt.figure(figsize=(12, 8))
        sns.barplot(data=top_items, x='count', y='item_name')
        
        plt.title(f'Top {top_n} Most Frequently Ordered Items')
        plt.xlabel('Order Count')
        plt.ylabel('Item Name')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def plot_order_quantity_vs_stock(self, save_path: Optional[str] = None) -> None:
        """
        Plot the relationship between order quantity and current stock.
        
        Args:
            save_path: Optional path to save the plot image
        """
        df = self.load_history()
        if df.empty:
            print("No order history data available")
            return
        
        plt.figure(figsize=(10, 8))
        sns.scatterplot(data=df, x='current_stock', y='quantity', hue='success', alpha=0.7)
        
        plt.title('Order Quantity vs. Current Stock')
        plt.xlabel('Current Stock')
        plt.ylabel('Order Quantity')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
    
    def generate_order_summary(self) -> Dict:
        """
        Generate a summary of order history.
        
        Returns:
            Dictionary containing summary statistics
        """
        df = self.load_history()
        if df.empty:
            return {"error": "No order history data available"}
        
        try:
            # Calculate summary statistics
            total_orders = df['order_id'].nunique()
            successful_orders = df[df['success']]['order_id'].nunique()
            success_rate = (successful_orders / total_orders) * 100 if total_orders > 0 else 0
            
            total_items = len(df)
            unique_items = df['item_name'].nunique()
            
            avg_quantity = df['quantity'].mean()
            total_quantity = df['quantity'].sum()
            
            # Get date range
            date_range = (df['timestamp'].max() - df['timestamp'].min()).days + 1
            
            return {
                "total_orders": total_orders,
                "successful_orders": successful_orders,
                "success_rate": success_rate,
                "total_items": total_items,
                "unique_items": unique_items,
                "avg_quantity_per_item": avg_quantity,
                "total_quantity_ordered": total_quantity,
                "date_range_days": date_range
            }
            
        except Exception as e:
            return {"error": f"Error generating summary: {str(e)}"}


def generate_report(config: Dict, output_dir: str = 'reports') -> None:
    """
    Generate a comprehensive report of order history with visualizations.
    
    Args:
        config: Configuration dictionary
        output_dir: Directory to save reports
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize visualization
    viz = OrderVisualization(config)
    
    # Generate summary
    summary = viz.generate_order_summary()
    
    # Create plots
    if "error" not in summary:
        viz.plot_order_success_rate(save_path=os.path.join(output_dir, 'order_success_rate.png'))
        viz.plot_items_by_frequency(save_path=os.path.join(output_dir, 'top_ordered_items.png'))
        viz.plot_order_quantity_vs_stock(save_path=os.path.join(output_dir, 'quantity_vs_stock.png'))
        
        # Generate HTML report
        html_content = f"""
        <html>
        <head>
            <title>Order Automation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #2c3e50; }}
                .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .metric {{ margin-bottom: 10px; }}
                .value {{ font-weight: bold; }}
                .images {{ margin-top: 30px; }}
                img {{ max-width: 100%; margin-bottom: 20px; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>Order Automation Report</h1>
            
            <div class="summary">
                <h2>Summary Statistics</h2>
                <div class="metric">Total Orders: <span class="value">{summary['total_orders']}</span></div>
                <div class="metric">Successful Orders: <span class="value">{summary['successful_orders']}</span></div>
                <div class="metric">Success Rate: <span class="value">{summary['success_rate']:.2f}%</span></div>
                <div class="metric">Total Items Ordered: <span class="value">{summary['total_items']}</span></div>
                <div class="metric">Unique Items: <span class="value">{summary['unique_items']}</span></div>
                <div class="metric">Average Quantity per Item: <span class="value">{summary['avg_quantity_per_item']:.2f}</span></div>
                <div class="metric">Total Quantity Ordered: <span class="value">{summary['total_quantity_ordered']}</span></div>
                <div class="metric">Date Range (days): <span class="value">{summary['date_range_days']}</span></div>
            </div>
            
            <div class="images">
                <h2>Order Success Rate Over Time</h2>
                <img src="order_success_rate.png" alt="Order Success Rate">
                
                <h2>Top Ordered Items</h2>
                <img src="top_ordered_items.png" alt="Top Ordered Items">
                
                <h2>Order Quantity vs. Current Stock</h2>
                <img src="quantity_vs_stock.png" alt="Order Quantity vs. Stock">
            </div>
        </body>
        </html>
        """
        
        # Write HTML report
        with open(os.path.join(output_dir, 'order_report.html'), 'w') as f:
            f.write(html_content)
        
        print(f"Report generated in {output_dir}")
    else:
        print(f"Could not generate report: {summary['error']}")


if __name__ == "__main__":
    # Example usage
    from utils.helpers import ConfigHandler
    config = ConfigHandler.load_config()
    generate_report(config) 