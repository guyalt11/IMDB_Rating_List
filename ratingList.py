import sys
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Retrieve the name of a movie from the HTML
def retrieve_movie_name(movie):
    # Extract the movie title
    name = movie.find('h3', class_='ipc-title__text').contents
    return name[0]

# Scroll through the page to load all content
def scroll_page(driver):
    # Initial height of the page
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
	# Scrolling and waiting for 3 second to retrieve the new height
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) 
        new_height = driver.execute_script("return document.body.scrollHeight")

	# If the height hasn't changed, we've reached the bottom of the page
        if new_height == last_height:
            break
        last_height = new_height

# Function to launch the page using Selenium WebDriver and return the page content
def spawn_page(page):
    url = page
    options = webdriver.ChromeOptions()
    # Configure the Chrome options (headless mode, user agent, etc.)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36")  # User agent
    options.add_argument("--disable-extensions")  # Disable browser extensions
    options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    options.add_argument("--incognito")  # Open in incognito mode
    options.add_argument("--headless")  # Run without opening a browser window
	
    # Set up the WebDriver with ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url) # Open the page
    scroll_page(driver) # Scroll the page to load all content

    # Get the page's HTML content and parse it with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Return the pased content
    return soup

if __name__ == '__main__':
    # Check if the user ID is passed as a command-line argument
    if len(sys.argv) < 2:
        print("Please provide your IMDb user ID as an argument.")
        sys.exit(1)

    # Set the user's ID
    user_id = sys.argv[1]

    # printing to stdout the content in a JSON format
    print("{")

    # Loop through ratings from 10 to 1
    for rating in range(10,0,-1):
        print("\"Movies rated "+str(rating)+"\": [")
		
	# The URL for the current rating
        current_url = f"https://www.imdb.com/user/{user_id}/ratings/?sort=top_rated%2Cdesc&single_user_rating={rating},{rating}"

	# Get the BeautifulSoup object for the page
        soup = spawn_page(current_url)

	# Find all the movie entries on the page
        movies = soup.find_all('div', class_='ipc-metadata-list-summary-item__tc')

	# Get last movie to avoid a trailing comma
        last_movie = retrieve_movie_name(movies[-1])

	# Loop through the movies with the current rating and print it
        for movie in movies:
            movie_name = retrieve_movie_name(movie)
			# If it's not the last movie, add a comma after the name
            if movie_name != last_movie:
                print("\""+movie_name+"\",")
            else:
                print("\""+movie_name+"\"")
                
        print("]")

    print("}")
