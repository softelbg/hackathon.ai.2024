from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set up the WebDriver (make sure to specify the correct path to your WebDriver)
service = Service('path/to/chromedriver')  # Update this path
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL of the Product Hunt page
url = 'https://www.producthunt.com/'  # Replace with the actual URL

# Fetch the page
driver.get(url)

# Wait for the page to load (adjust the time as necessary)
time.sleep(5)

# Initialize an empty list to store products
products = []

# Search for the product divs by class and extract name and tagline
for post in driver.find_elements(By.CLASS_NAME, 'styles_titleItem__bCaNQ'):  # Adjust class
  name_tag = post.find_element(By.TAG_NAME, 'strong')  # Product name
  tagline_tag = post.find_element(By.CLASS_NAME, 'opacity-50')  # Product tagline

  if name_tag and tagline_tag:
    product_name = name_tag.text.strip()
    tagline = tagline_tag.find_element(By.XPATH, 'following-sibling::span').text.strip()

    # Check if the product matches "idea-validator"
    if "idea-validator" in product_name.lower():
      product_comments = []  # Initialize a list for comments

      # Extract comments if available (adjust selectors as necessary)
      comments_section = post.find_element(By.CLASS_NAME, 'styles_commentsSection__...')  # Adjust class
      if comments_section:
        comments = comments_section.find_elements(By.CLASS_NAME, 'styles_commentItem__...')
        for comment in comments:
          comment_text = comment.text.strip()
          product_comments.append(comment_text)

      # Extract nearby products (if they are structured in a specific section)
      nearby_products = []
      nearby_section = post.find_element(By.CLASS_NAME, 'styles_nearbyProducts__...')  # Adjust class
      if nearby_section:
        nearby = nearby_section.find_elements(By.CLASS_NAME, 'styles_nearbyItem__...')
        for item in nearby:
          nearby_name = item.find_element(By.TAG_NAME, 'strong').text.strip()
          nearby_products.append(nearby_name)

      # Store product details along with comments and nearby products
      products.append({
        'name': product_name,
        'tagline': tagline,
        'comments': product_comments,
        'nearby_products': nearby_products
      })

# Output the product list and comments
for product in products:
  print(f"Product: {product['name']}, Tagline: {product['tagline']}")
  print("Comments:")
  for comment in product['comments']:
    print(f"- {comment}")
  print("Nearby Products:")
  for nearby in product['nearby_products']:
    print(f"- {nearby}")

# Close the WebDriver
driver.quit()
