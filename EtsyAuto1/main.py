# main.py
import sys
from datetime import datetime
from pathlib import Path
from config import Config
from logger import setup_logger
import pandas as pd

# Import the existing etsy_api_connector
from etsy_api_connector import EtsyAPIConnector
from filename_generator import FilenameGenerator
from file_database import FileDatabase

class EtsyAutomation:
    def __init__(self):
        # Set up logging
        Config.get_log_path().mkdir(parents=True, exist_ok=True)
        log_file = Config.get_log_path() / f"etsy_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        self.logger = setup_logger("main", log_file)
        self.logger.info("=" * 50)
        self.logger.info("Starting Etsy Automation")
        self.logger.info("=" * 50)
        
        # Initialize components
        self.etsy_client = EtsyAPIConnector()
        self.filename_generator = FilenameGenerator(self.logger)
        self.file_database = FileDatabase(self.logger)
    
    def run(self, days_back=None):
        """Main execution flow"""
        try:
            # Get orders with workflow SKUs
            orders = self.get_workflow_orders(days_back=days_back)
            
            if not orders:
                self.logger.info("No workflow orders found")
                return
            
            # Process orders
            results = self.process_orders(orders)
            
            # Generate reports
            self.generate_reports(results)
            
            self.logger.info("Automation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Automation failed: {e}")
            raise
    
    def get_workflow_orders(self, days_back=None):
        """Get orders and filter for workflow SKUs"""
        days_back = days_back or Config.DAYS_BACK_DEFAULT
    
        # Get all recent orders
        all_orders = self.etsy_client.get_recent_orders(days_back=days_back, limit=100)
    
        if not all_orders:
            return []
    
        # DEBUG: Print complete order structure
        print("\n=== DEBUG: Complete transaction data ===")
        for order in all_orders:
            print(f"\nOrder #{order.get('receipt_id')}:")
            print(f"  Has 'transactions' key: {'transactions' in order}")
            print(f"  Has 'transactions' key: {'transactions' in order}")
            
            # Try both capitalization
            transactions = order.get('transactions') or order.get('transactions')
            
            if transactions:
                print(f"  Number of transactions: {len(transactions)}")
                for idx, transaction in enumerate(transactions):
                    print(f"\n  Transaction {idx + 1}:")
                    print(f"    SKU: {transaction.get('sku', 'NO SKU FIELD')}")
                    print(f"    Title: {transaction.get('title', 'NO TITLE')[:60]}")
                    print(f"    All keys: {list(transaction.keys())}")
            else:
                print("  NO TRANSACTIONS FOUND")
                print(f"  Order keys: {list(order.keys())}")
            print("-" * 60)
        print("=== END DEBUG ===\n")
    
    # ... rest of the method stays the same
        # Filter for workflow SKUs
        workflow_orders = []
        for order in all_orders:
            order_items = []
            
            if 'transactions' in order:
                for transaction in order['transactions']:
                    sku = transaction.get('sku', '')
                    if sku in Config.WORKFLOW_SKUS:
                        order_items.append(transaction)
            
            if order_items:
                filtered_order = order.copy()
                filtered_order['transactions'] = order_items
                workflow_orders.append(filtered_order)
        
        self.logger.info(f"Found {len(workflow_orders)} orders with workflow SKUs")
        return workflow_orders
    
    def process_orders(self, orders):
        """Process orders and generate filename data"""
        all_orders = []
        needs_made = []
        file_locations = []
        
        for order in orders:
            customer_name = order.get('name', 'Unknown Customer')
            order_id = order.get('receipt_id', 'Unknown')
            
            for transaction in order.get('transactions', []):
                # Generate filename
                filename = self.filename_generator.generate_filename(transaction)
                
                if not filename:
                    continue
                
                # Check if file exists
                file_path = self.file_database.find_file(filename)
                
                order_data = {
                    'order_id': order_id,
                    'customer_name': customer_name,
                    'sku': transaction.get('sku', ''),
                    'generated_filename': filename,
                    'file_exists': file_path is not None,
                    'file_path': str(file_path) if file_path else 'NOT FOUND',
                    'quantity': transaction.get('quantity', 1),
                    'price': self.format_price(transaction.get('price', {})),
                    'personalization': self.extract_personalization(transaction.get('variations', []))
                }
                
                all_orders.append(order_data)
                
                if not file_path:
                    needs_made.append(order_data)
                else:
                    file_locations.append(order_data)
        
        return {
            'all_orders': all_orders,
            'needs_made': needs_made,
            'file_locations': file_locations
        }
    
    def extract_personalization(self, variations_list):
        """Extract and clean personalization text from variations"""
        for var in variations_list:
            if var.get('formatted_name') == 'Personalization':
                raw_value = var.get('formatted_value', '')
                # Clean the personalization using the same logic as filename generation
                return self.filename_generator.smart_capitalize_name(raw_value)
        return ''
    
    def format_price(self, price_data):
        """Format price from Etsy API format"""
        if isinstance(price_data, dict):
            amount = price_data.get('amount', 0)
            divisor = price_data.get('divisor', 100)
            return f"${amount / divisor:.2f}"
        return str(price_data)
    
    def generate_reports(self, results):
        """Generate Excel reports"""
        Config.get_output_path().mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = Config.get_output_path() / f"etsy_orders_{timestamp}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # All Orders sheet
            if results['all_orders']:
                df_all = pd.DataFrame(results['all_orders'])
                df_all.to_excel(writer, sheet_name='All Orders', index=False)
            
            # Needs Made sheet
            if results['needs_made']:
                df_needs = pd.DataFrame(results['needs_made'])
                df_needs.to_excel(writer, sheet_name='Needs Made', index=False)
            
            # File Locations sheet
            if results['file_locations']:
                df_files = pd.DataFrame(results['file_locations'])
                df_files.to_excel(writer, sheet_name='File Locations', index=False)
        
        self.logger.info(f"Reports generated: {output_file}")
        print(f"Reports saved to: {output_file}")


if __name__ == "__main__":
    automation = EtsyAutomation()
    automation.run(days_back=7)