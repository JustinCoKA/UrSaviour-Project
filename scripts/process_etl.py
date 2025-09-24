import fitz
import re
import pymysql
import os

#1 Database set
DB_HOST = os.environ.get('DB_HOST')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_NAME = os.environ.ge('DB_NAME')

#2 Extract
def extract_text_from_pdf(file_path):
    try:
        doc = fitz.open(file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text")
        doc.close()
        print("Completed extracting text from pdf file")
        return full_text

    except Exception as e:
        print(e)
        return None

#3 Transform
def transform_data(text):
    pattern = re.compile(r"(.+?)\s+(.+?)\s+\$(\d+\.\d{2})\s+(.+?)\s+\$(\d+\.\d{2})")
    matches = pattern.findall(text)
    transformed_data = []
    for match in matches:
        try:
            transformed_data.append({
                "productName": match[0].strip(),
                "storeName": match[1].strip(),
                "basePrice": float(match[2]),
                "offerDetails": match[3].strip(),
                "price": float(match[4])
                })

        except (ValueError, IndexError) as e:
            print(e)
            continue

    print("Transformed data")
    return transformed_data

#4 Load data
def load_data_to_db(data):
    conn = None
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        print("Connected to database")

        cursor.execute("SELECT productId, productName FROM products")
        product_map = {p['productName']: p['productId'] for p in cursor.fetchall()}

        cursor.execute("SELECT storeId, storeName FROM stores")
        store_map = {s['storeName']: s['storeId'] for s in cursor.fetchall()}

        for item in data:
            if item['productName'] not in product_map:
                cursor.execute("INSERT INTO products (productName) VALUES (%s)", (item['productName'],))
                product_map[item['productName']] = cursor.lastrowid
                print(f"   -> new product added: {item['productName']}")

            if item['storeName'] not in store_map:
                cursor.execute("INSERT INTO stores (storeName) VALUES (%s)", (item['storeName'],))
                store_map[item['storeName']] = cursor.lastrowid
                print(f"   -> new store added: {item['storeName']}")

        conn.commit()

        cursor.execute("TRUNCATE TABLE storeOfferings")
        print("   -> StoreOfferings reseted")

        offerings_to_insert = []
        for item in data:
            productId = product_map.get(item['productName'])
            storeId = store_map.get(item['storeName'])

            if productId and storeId:
                offerings_to_insert.append((
                    productId,
                    storeId,
                    item['price'],
                    item['basePrice'],
                    item['offerDetails']
                ))

        sql = """
              INSERT INTO storeOfferings (productId, storeId, price, basePrice, offerDetails)
              VALUES (%s, %s, %s, %s, %s) 
              """
        cursor.executemany(sql, offerings_to_insert)
        conn.commit()

        print(f"✅ Step 4: {cursor.rowcount}, discount information loaded to DB")

    except Exception as e:
        print(e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Connection closed")

if __name__ == "__main__":
    local_pdf_path = '/Users/juhwanlee/Desktop/UrSaviour-Project/data/no.27week_special.pdf'

    extracted_text = extract_text_from_pdf(local_pdf_path)

    if extracted_text:
        transformed_data = transform_data(extracted_text)
        if transformed_data:
            load_data_to_db(transformed_data)







