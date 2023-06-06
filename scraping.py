from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import csv

# Setup Firefox options
firefox_options = Options()
firefox_options.add_argument("--headless")  # Ensure GUI is off

# This assumes the GeckoDriver is in your system PATH
webdriver_service = Service("geckodriver")
driver = webdriver.Firefox(service=webdriver_service, options=firefox_options)

# URL of the parent catalogue page
url = input("Ingresa el URL de la categoria (+?P=): ")
base_url = url
# base_url = "https://nissei.com/ar/camaras-y-filmadoras/camaras/reflex-mirrorless?p="

# Define a list to store the extracted data for each product
product_data = []

# Specify the file path for CSV output
csv_file = "Nissei.csv"

# Initialize page number
page = 1

# Iterate through each page until there are no more pages available
while True:
    # Construct the URL for the current page
    url = base_url + str(page)

    # Send a GET request to the current page
    driver.get(url)
    doc = BeautifulSoup(driver.page_source, "html.parser")

    # Get the links of individual product pages from the catalogue
    product_elements = doc.find_all(class_="product-item-info")
    product_links = []
    for element in product_elements:
        link = element.find("a")
        if link and "href" in link.attrs:
            product_links.append(link["href"])

    # Check if there are no product links on the current page
    if not product_links:
        break  # Exit the loop if there are no more pages with products

    # Iterate through each product page
    for product_url in product_links:
        driver.get(product_url)
        doc = BeautifulSoup(driver.page_source, "html.parser")

        # Use your own code here to extract data for the current product
        title = doc.find(class_="base").text
        price = doc.find(class_="price").text
        sku = doc.find(itemprop="sku").text

        bullets = doc.find_all(itemprop="description")
        bullets_text = ""
        for bullets_element in bullets:
            bullets_text += bullets_element.text.strip() + "\n"

        description_element = doc.find("div", {"data-content-type": "text"})
        description = description_element.text.strip() if description_element else ""

        image_links = doc.find_all('img')
        images = []
        for img_element in image_links:
            src = img_element.get('src')
            if src and src.startswith('https://nissei.com/media/catalog/product/'):
                images.append(src)

          # Store the extracted data as a dictionary
        product = {
            "Title": title,
            "Price": price,
            "SKU": sku,
            "Bullets": bullets_text,
            "Description": description,
            "Images": ", ".join(images)  # join all images into a single string separated by commas
        }

        # Add the product data to the list
        product_data.append(product)

    # Increment the page number to proceed to the next page
    page += 1

# Write the data to a CSV file
with open(csv_file, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["Title", "Price", "SKU", "Bullets", "Description", "Images"])
    writer.writeheader()
    writer.writerows(product_data)

# Close the browser window after scraping the data
driver.quit()

print("Data extraction and CSV export completed.")