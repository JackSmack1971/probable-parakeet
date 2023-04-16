from typing import List
from pathlib import Path
import threading
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from tkinter import Tk, Label, Entry, OptionMenu, Button, filedialog, messagebox
from tkinter.ttk import Progressbar


class ImageScraper:
    def __init__(self, website_url):
        self.website_url = website_url
        self.search_query = ""
        self.save_directory = ""
        self.num_images = 0
        self.num_pages = 0
        self.format_choice = ""
        self.size_choice = ""
        self.driver_path = os.getenv("CHROMEDRIVER_PATH")
        self.driver_options = None
        self.driver = None
        self.images = []
        self.progress = None
        self.root = None 
        self.search_query_input = None
        self.num_images_input = None
        self.num_pages_input = None
        self.format_choice_input = None
        self.size_choice_input = None 

    def get_search_query(self):
        self.search_query = self.search_query_input.get() 

    def get_save_directory(self):
        self.save_directory = filedialog.askdirectory() 

    def construct_search_url(self):
        self.driver_options = webdriver.ChromeOptions()
        self.driver_options.add_argument('--no-sandbox')
        self.driver_options.add_argument('--disable-dev-shm-usage')
        self.driver_options.headless = True 

        # generate URL for first page of search results
        url = f"{self.website_url}/search?q={self.search_query}&tbm=isch&tbs=isz:{self.size_choice}&ijn=0"
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.driver_options)
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        
    def find_images(self):
        # scrape images from each page of search results
        for page_num in range(self.num_pages):
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            self.images += soup.select('img')[:self.num_images]
            if page_num < self.num_pages - 1:
                # scroll down to the bottom of the page to load more images
                ActionChains(self.driver).move_to_element(self.driver.find_element(By.TAG_NAME, 'body')).send_keys(Keys.END).perform()
                # click "Next" button to navigate to next page of search results
                try:
                    next_button = self.driver.find_element(By.XPATH, '//button[@aria-label
            except:
                break 

async def download_image(self, image_url: str, image_path: Path):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                with open(image_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
    except Exception as e:
        print(f"Error downloading image: {e}") 

def start_download(self):
    num_threads = min(len(self.images), 10) # limit number of concurrent threads to avoid overwhelming server
    loop = asyncio.get_event_loop()
    futures = []
    for i, image in enumerate(self.images):
        image_url = image.get('src')
        image_extension = Path(image_url).suffix
        image_name = f"{self.search_query}_{i+1}{image_extension}"
        image_path = Path(self.save_directory) / image_name
        future = loop.create_task(self.download_image(image_url, image_path))
        futures.append(future) 

    for i, future in enumerate(asyncio.as_completed(futures)):
        try:
            await future
        except Exception as e:
            print(f"Error downloading image: {e}")
        print(f"Downloaded image {i+1}/{len(self.images)}")
        self.progress['value'] = (i+1) * 100 / len(self.images)
        self.root.update_idletasks() 

    self.progress.pack_forget()
    self.driver.quit() 

def handle_error(self, error_message):
    messagebox.showerror("Error", f"An error occurred: {error_message}") 

def validate_user_input(self):
    try:
        self.num_images = int(self.num_images_input.get())
        if self.num_images <= 0:
            raise ValueError("Number of images must be positive")
        allowed_formats = ['jpg', 'png', 'gif']
        if self.format_choice not in allowed_formats:
            raise ValueError(f"Image format must be one of: {', '.join(allowed_formats)}")
    except ValueError as e:
        raise ValueError(str(e)) 

def get_user_input(self):
    self.root = Tk()
    self.root.title("Image Gallery Scraper")
    self.root.geometry("400x300") 

    search_query_label = Label(self.root, text="Enter search query:")
    search_query_label.pack() 

    self.search_query_input = Entry(self.root)
    self.search_query_input.pack() 

    num_images_label = Label(self.root, text="Number of images:")
    num_images_label.pack() 

    self.num_images_input = Entry(self.root)
    self.num_images_input.pack() 

    num_pages_label = Label(self.root, text="Number of pages:")
    num_pages_label.pack() 

    self.num_pages_input = Entry(self.root)
    self.num_pages_input.pack() 

    format_options = ['jpg', 'png', 'gif']
    format_choice_label = Label(self.root, text="Image format:")
    format_choice_label.pack()
    self.format_choice_input = OptionMenu(self.root, StringVar(), *format_options)
    self.format_choice_input.pack() 

    size_options = ['icon', 'small', 'medium', 'large', 'huge']
    size_choice_label = Label(self.root, text="Image size:")
    size_choice_label.pack()
    self.size_choice_input = OptionMenu(self.root, StringVar(), *size_options)
    self.size_choice_input.pack() 

    search_button = Button(self.root, text="Search", command=self.validate_user_input_and_run)
    search_button.pack() 

    self.root.mainloop() 

    def validate_user_input_and_run(self):
        try:
            self.get_search_query()
            self.get_save_directory()
            self.num_pages = int(self.num_pages_input.get())
            self.format_choice = self.format_choice_input.get()
            self.size_choice = self.size_choice_input.get()
            self.validate_user_input() 

            self.construct_search_url()
            self.find_images() 

            self.progress = Progressbar(self.root, orient='horizontal', length=200, mode='determinate')
            self.progress.pack() 

            asyncio.run(self.start_download()) 

        except ValueError as e:
            self.handle_error(str(e)) 

def run(self): self.get_user_input() 

if name == "main": scraper = ImageScraper(website_url="https://www.examplegallery.com") scraper.run()
