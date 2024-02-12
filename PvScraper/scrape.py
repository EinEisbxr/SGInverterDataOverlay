from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
#from bs4 import BeautifulSoup
import time
from datetime import datetime
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service

class Scraper():
    def __init__(self, host_IP:str, driver_path:str="/usr/bin/chromedriver") -> None: 
        self.timestamps = []
        self.pv_leistung_values = []
        self.wirkleistung_values = []
        self.netzbezug_values = []
        self.data = None
        
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--headless")

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
    def get_data(self, params:list):
        while True:
            if self.website_initialized == False:
                raise Exception("Website not initialized. Please call get_onto_website() first.")

            wait = WebDriverWait(self.driver, 10)
            spans = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[@data-v-1a879c9b='']")))

            data = [span.text for span in spans]
            
            data = [span.text for span in spans]

            formatted_data = [(data[i], data[i+1]) for i in range(0, len(data), 2)]

            remove_list = [('', 'Setup-Assistent'), ('Deutsch', ''), ('Standard-Benutzer', ''), ('', 'WiNet-S'), ('', ''), ('', ''), ('', ''), ('Alle anzeigen', 'Stringwechselrichter'), ('PV-Wechselrichter für Wohngebäude', 'Wechselrichter für Energiespeicherung in Wohngebäuden'), ('Ladegerät', 'SH10RT(COM1-001)'), ('Echtzeitwerte', 'Batterieinformationen'), ('DC-Informationen', 'Geräteinformation'), ('Dauer Netzbetrieb', '-- h'), ('Tägliche PV-Stromerzeugung', '2.6 kWh'), ('Gesamte PV-Stromerzeugung', '9134.5 kWh'), ('Tagesproduktion', '-- kWh'), ('Ertrag gesamt', '-- kWh'), ('Gerätestatus', 'Normal')]

            filtered_data = [item for item in formatted_data if item not in remove_list]

            if params == None:
                filtered_data = [{item[0]: item[1]} for item in formatted_data if item not in remove_list]
                filtered_data = dict(item for item in formatted_data if item not in remove_list)
                self.data = filtered_data
            
            else:
                param_data = [item for item in filtered_data if item[0] in params]

                if len(param_data) == 0:
                    raise Exception("Parameter(s) not found on website.")

                param_data = [{item[0]: item[1]} for item in formatted_data if item not in remove_list]
                param_data = dict(item for item in formatted_data if item not in remove_list)

                self.data = param_data