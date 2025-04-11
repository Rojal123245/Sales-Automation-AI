from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import logging
import os

class OrderReportGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        
    def generate_order_report(self, order_data: dict) -> str:
        """Generate a PDF report for an order"""
        try:
            # Create output directory if it doesn't exist
            output_dir = "reports/orders"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp and cart ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cart_id = order_data.get('cart_id', 'unknown')
            filename = f"{output_dir}/order_report_{cart_id}_{timestamp}.pdf"
            
            # Create the PDF document
            doc = SimpleDocTemplate(
                filename,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build the document content
            story = []
            
            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            story.append(Paragraph("Order Report", title_style))
            
            # Add order summary
            summary_style = self.styles['Normal']
            story.append(Paragraph(f"Order ID: {cart_id}", summary_style))
            story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", summary_style))
            story.append(Paragraph(f"Total Items: {len(order_data.get('orders', []))}", summary_style))
            story.append(Paragraph(f"Total Cost: ${order_data.get('total_cost', 0):.2f}", summary_style))
            story.append(Spacer(1, 20))
            
            # Create table for ordered items
            if order_data.get('orders'):
                table_data = [
                    ['Product', 'Current Stock', 'Ordered Quantity', 'Unit Price', 'Total Price', 'Predicted Demand']
                ]
                
                # Add data rows
                for item in order_data['orders']:
                    row = [
                        str(item.get('title', 'N/A')),
                        str(item.get('current_stock', 'N/A')),
                        str(item.get('quantity', 0)),
                        f"${float(item.get('unit_price', 0)):.2f}",
                        f"${float(item.get('quantity', 0) * float(item.get('unit_price', 0))):.2f}",
                        f"{float(item.get('predicted_demand', 0)):.1f}"
                    ]
                    table_data.append(row)
                
                # Create and style the table
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('TOPPADDING', (0, 1), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ]))
                
                story.append(table)
            
            # Add notes section
            story.append(Spacer(1, 30))
            story.append(Paragraph("Notes:", self.styles['Heading2']))
            story.append(Paragraph("* Predicted Demand is based on AI forecast for the next period", self.styles['Normal']))
            story.append(Paragraph("* Current Stock levels are as of the time of order placement", self.styles['Normal']))
            
            # Build the PDF
            doc.build(story)
            
            self.logger.info(f"Generated order report: {filename}")
            return filename
            
        except Exception as e:
            self.logger.error(f"Failed to generate order report: {str(e)}")
            raise
