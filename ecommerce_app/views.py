from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
import json
import logging
import os
import reportlab
from django.conf import settings
from django.http import FileResponse
import time

# Function to read data from a JSON file
def read_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            logging.info("Successfully read data from the file.")
            return data
    except FileNotFoundError:
        logging.error("File not found. Please provide a valid file path.")
    except json.JSONDecodeError:
        logging.error("Error decoding JSON. Please check the file format.")

# Function to calculate total sales per product, best-selling product, and total revenue per category
def calculate_totals(data):
    product_sales = {}
    category_revenue = {}

    best_selling_product = {"product_name": None, "total_sales": 0}

    for sale in data:
        product_name = sale.get('product_name')
        category = sale.get('category')
        quantity = sale.get('quantity')
        sale_price = sale.get('sale_price')

        # Calculate total sales per product
        product_sales[product_name] = product_sales.get(product_name, 0) + quantity

        # Determine the best-selling product
        if quantity > best_selling_product["total_sales"]:
            best_selling_product["product_name"] = product_name
            best_selling_product["total_sales"] = quantity

        # Calculate total revenue per category
        category_revenue[category] = category_revenue.get(category, 0) + (quantity * sale_price)

    return product_sales, best_selling_product, category_revenue

# Function to generate a human-readable report
def generate_report(product_sales, best_selling_product, category_revenue):
    report = "E-commerce Data Processing Report\n\n"

    report += "Total Sales per Product:\n"
    for product, sales in product_sales.items():
        report += f"{product}: {sales} units\n"

    report += f"\nBest Selling Product: {best_selling_product['product_name']} with {best_selling_product['total_sales']} units\n"

    report += "\nTotal Revenue per Category:\n"
    for category, revenue in category_revenue.items():
        report += f"{category}: ${revenue:.2f}\n"

    return report

# View function to process data and render a template
def process_data(request):
    file_path = 'ecommerce_data.json'
    data = read_data(file_path)

    if data:
        product_sales, best_selling_product, category_revenue = calculate_totals(data)
        report = generate_report(product_sales, best_selling_product, category_revenue)
        logging.info("Report generation complete.")
        return render(request, 'frontend/report.html', {
            'product_sales': product_sales,
            'best_selling_product': best_selling_product,
            'category_revenue': category_revenue,
        })
    else:
        logging.error("Unable to proceed with data processing due to errors.")
        return HttpResponse("Error processing data. Check the logs for details.")

# View function to download the report
def download_report(request):
    temp_file_path = 'temp_report.txt'
    try:
        with open(temp_file_path, 'r') as file:
            response = HttpResponse(file.read(), content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=temp_report.txt'
            return response
    except FileNotFoundError:
        return HttpResponse("Report file not found.")

    # Wait for any file operations to complete (adjust the sleep duration as needed)
    time.sleep(2)

    try:
        os.remove(temp_file_path)
    except PermissionError:
        return HttpResponse("Failed to remove the temporary report file due to a permission error.")
