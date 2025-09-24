import boto3
import pandas as pd
import random
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime


def lambda_handler(event, context):
    #Create S3 client
    s3 = boto3.resource('s3')
    bucket_name = 'ursaviour-data-group03-20250608'
    bucket = s3.Bucket(bucket_name)

    #Setting Bucket and file name
    file_key = 'foundational-dataset/foundational_dataset_v1.csv'
    local_filename = '/tmp/temp_master_list.csv'

    #File download
    try:
        bucket.download_file(file_key, local_filename)
        print(f'file downloaded: s3://{bucket_name}/{file_key} -> {local_filename}')

    except Exception as e:
        print(f"failed to download {file_key}: {e}")
        return {'statusCode': 500, 'body': str(e)}


    # CSV file load to DataFrame
    df = pd.read_csv(local_filename)

    # Randomly select 30 discount item
    num_items_to_discount = 30
    discount_sample = df.sample(n = num_items_to_discount)

    #Type of discount
    discount_list = (['10% OFF'] * 9 +
                      ['30% OFF'] * 9 +
                      ['Half Price'] * 9 +
                      ['Big deal'] * 3 )

    random.shuffle(discount_list)

    discounted_products = []
    product_list = discount_sample.to_dict(orient='records')

    for i in range(len(product_list)):
        product = product_list[i]
        discount_type = discount_list[i]

        original_price = product['base_price']

        if discount_type == '10% OFF':
            final_price = original_price * 0.9
        elif discount_type == '30% OFF':
            final_price = original_price * 0.7
        elif discount_type == 'Half Price':
            final_price = original_price * 0.5
        elif discount_type == 'Big deal':
            final_price = original_price * 0.3

        product['discount_type'] = discount_type
        product['final_price'] = round(max(0, final_price), 2)

        discounted_products.append(product)

    current_week = datetime.now().isocalendar()[1]
    output_csv_filename = f'/tmp/no.{current_week}week_special.csv'
    pdf_filename = f'/tmp/no.{current_week}week_special.pdf'

    results_df = pd.DataFrame(discounted_products)
    results_df.to_csv(output_csv_filename, index=False, encoding='utf-8-sig')
    print(f"applied discounte type products has been saved to {output_csv_filename}")

    #Create PDF file
    pdf_table_data = [['Product Name', 'Store', 'Original Price', 'Discount Type', 'Final Price']]

    for product in discounted_products:
        pdf_table_data.append([
            product['product_name'],
            product['store_name'],
            f"${product['base_price']:.2f}",
            product['discount_type'],
            f"${product['final_price']:.2f}"
        ])

    #Using ReportLab generate PDF docu
    doc = SimpleDocTemplate(pdf_filename)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(f"UrSaviour Weekly Speiclas - No.{current_week}", styles['h1'])
    table = Table(pdf_table_data)

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
       ])
    table.setStyle(style)

    elements.append(title)
    elements.append(table)

    doc.build(elements)

    print(f"built pdf file {pdf_filename}")
    print("Completed All tasks")

    bucket.upload_file(output_csv_filename, f'data/no.{current_week}week_special.csv')
    bucket.upload_file(pdf_filename, f'data/no.{current_week}week_special.pdf')

    print("All tasks completed and uploaded to S3")

    return {
        'statusCode': 200,
        'body': 'Process Completed successfully'
    }