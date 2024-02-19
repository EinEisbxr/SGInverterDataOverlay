from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
import platform

class Scraper():
    def __init__(self, host_IP:str, driver_path:str="/usr/bin/chromedriver") -> None: 
        self.timestamps = []
        self.pv_leistung_values = []
        self.wirkleistung_values = []
        self.netzbezug_values = []
        self.data = None
        
        if platform.system() == "Linux":
            service = Service(driver_path)
        else:
            service = Service()
            

        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ['enable-logging'])
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        #options.add_argument("--headless")
        options.add_argument("--log-level=1")
        options.add_argument("--lang=en")
        

        self.driver = webdriver.Chrome(service=service, options=options)

        self.host_IP = host_IP

        self.website_initialized = False
        
        
    def get_onto_website(self):
        # Go to the website
        self.driver.get(f"http://{self.host_IP}")
        
        print("Waiting for website to load...")
        
        # After page is loaded, close the pop-up
        wait = WebDriverWait(self.driver, 60)
        close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'el-icon-close')))
        close_button.click()
        
        print("Website loaded.")

        self.driver.get(f"http://{self.host_IP}/#/devicemanager/deviceManager")
        
        self.website_initialized = True


    # Now you can use BeautifulSoup to parse the page source
    def get_data(self):
        while True:
            if self.website_initialized == False:
                raise Exception("Website not initialized. Please call get_onto_website() first.")

            time.sleep(0.5)
            spans1 = self.driver.find_elements(By.XPATH, "//span[@data-v-1a879c9b='']")

            data1 = [span.text for span in spans1]
            
            button = self.driver.find_element(By.XPATH, "//*[text()='Battery Information']")
            button.click()
            
            time.sleep(0.5)
            spans2 = self.driver.find_elements(By.XPATH, "//span[@data-v-1a879c9b='']")
            
            data2 = [span.text for span in spans2]
            
            data = data1 + data2
            
            print(data)
            
            formatted_data = [(data[i], data[i+1]) for i in range(0, len(data) - 1, 2)]

            remove_list = [('Realtime Values', 'Battery Information'), ('DC Info', 'Device Information')]
            
            filtered_data = [{item[0]: item[1]} for item in formatted_data if item not in remove_list]
            filtered_data = dict(item for item in formatted_data if item not in remove_list)
            self.data = filtered_data
            
            button = self.driver.find_element(By.XPATH, "//*[text()='Realtime Values']")
            button.click()
        