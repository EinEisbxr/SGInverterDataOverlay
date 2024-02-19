import flask
import threading
import time
import datetime
from database_commands.database_commands import DataBase
import psutil
import os
import calendar

dataBase = DataBase()

global app
app = flask.Flask(__name__)

global dataArray, currentdata

dataArray = []

currentdata = None  # Make currentdata a global variable


class WebServer:
    def __init__(self, scraper) -> None:
        self.init_database()
        
        global currentdata
        self.scraper = scraper
        currentdata = None  # Initialize currentdata here
        
        print("WebServer initialized.")
        
        tdata = threading.Thread(target=self.collect_data)
        tdata.start()
        
        app.run(host="192.168.178.56", debug=False, threaded=True)
        
    def init_database(self):
        global database_path
        # create table to save values in
        year_folder = datetime.date.today().year
        current_path = os.getcwd()
        folder_path = os.path.join(current_path, f"PVFolder-{str(year_folder)}")
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        month_name = calendar.month_name[datetime.date.today().month]
        self.database_path = f"{folder_path}/PVData-{month_name}.db"
        database_path = self.database_path
        connection, cursor = dataBase.connect_database(self.database_path)
        dataBase.create_table(connection, cursor, "data_24h", """id INTEGER PRIMARY KEY AUTOINCREMENT, 
                              total_load_active_power FLOAT, total_dc_power FLOAT, device_status TEXT,
                              purchased_power FLOAT, total_export_active_power FLOAT, internal_air_temperature FLOAT,
                              battery_discharging_power FLOAT, battery_charging_power FLOAT, battery_temperature FLOAT,
                              battery_level FLOAT, battery_health FLOAT, timestamp""")
        
        current_day = datetime.date.today().day
        dataBase.create_table(connection, cursor, f"PVDayData_{current_day}", """id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        total_load_active_power FLOAT, total_dc_power FLOAT, device_status TEXT,
                        purchased_power FLOAT, total_export_active_power FLOAT, internal_air_temperature FLOAT,
                        battery_discharging_power FLOAT, battery_charging_power FLOAT, battery_temperature FLOAT,
                        battery_level FLOAT, battery_health FLOAT, timestamp""")
        
        dataBase.disconnect_database(connection)
        
    
    def collect_data(self):
        global currentdata
        
        # Init variables
        total_dc_power, total_load_active_power, total_export_active_power, purchased_power = 0, 0, 0, 0 
        
        # Connect to database
        conn, cur = dataBase.connect_database(self.database_path)
        
        # Start the scraper in a new thread
        t1 = threading.Thread(target=self.scraper.get_data)
        t1.start()
        
        # Wait for the scraper to get data
        while str(self.scraper.data) == "{'Realtime Values': 'Battery Information', 'DC Info': 'Device Information'}" or self.scraper.data == None or self.scraper.data == {}:
            time.sleep(0.4)

        
        count = 0
        while True:
            if count >= 5:
                try:
                    count = 0
                    
                    # Inverter Data
                    total_load_active_power = float(str(self.scraper.data["Total Load Active Power"]).replace(" kW", ""))
                    total_dc_power = float(str(self.scraper.data["Total DC Power"]).replace(" kW", ""))
                    device_status = str(self.scraper.data["Device Status"])
                    purchased_power = float(str(self.scraper.data["Purchased Power"]).replace(" kW", ""))
                    total_export_active_power = float(str(self.scraper.data["Total Export Active Power"]).replace(" kW", ""))
                    internal_air_temperature = float(str(self.scraper.data["Internal Air Temperature"]).replace("℃", "").replace("'", ""))
                    
                    # Battery Data
                    battery_discharging_power = float(str(self.scraper.data["Battery Discharging Power"]).replace(" kW", ""))
                    battery_charging_power = float(str(self.scraper.data["Battery Charging Power"]).replace(" kW", ""))
                    battery_temperature = float(str(self.scraper.data["Battery Temperature"]).replace("℃", "").replace("'", ""))
                    battery_level = float(str(self.scraper.data["Battery Level"]).replace(" %", ""))
                    battery_health = float(str(self.scraper.data["Battery Health"]).replace(" %", ""))
                    
                    # Timestamp
                    current_timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    
                    # Insert data into database
                    dataBase.insert_data(conn, cur, "data_24h", """total_load_active_power, total_dc_power, device_status,
                                         purchased_power, total_export_active_power, internal_air_temperature,
                                         battery_discharging_power, battery_charging_power, battery_temperature,
                                         battery_level, battery_health, timestamp""",
                                            (total_load_active_power, total_dc_power, device_status, purchased_power,
                                            total_export_active_power, internal_air_temperature, battery_discharging_power,
                                            battery_charging_power, battery_temperature, battery_level, battery_health, current_timestamp))
                    
                except Exception as e:
                    print(e)
                    time.sleep(1)

                
            currentdata = self.scraper.data
            
            count += 1
        
        
    @app.route('/')
    def index():
        return flask.render_template("overview.html")
    
    
    @app.route('/data')
    def data():
        global currentdata
        return flask.jsonify(currentdata)
    
    
    @app.route('/all_data')
    def all_data():
        dataArray = []
        conn, cur = dataBase.connect_database(database_path)
        data = dataBase.select_data(cur, "data_24h", "total_load_active_power, total_dc_power, purchased_power, total_export_active_power, timestamp")
        for row in data:
            dataArray.append({"Total Load Active Power": row[0], "Total DC Power": row[1], "Purchased Power": row[2], "Total Export Active Power": row[3], "Timestamp": row[4]})
        return flask.jsonify(dataArray)
    
    @app.route('/debug_values')
    def debug_values():
        cpu_temp = psutil.sensors_temperatures()['cpu_thermal'][0].current
        cpu_usage = psutil.cpu_percent()

        return flask.jsonify({"CPUTemp": cpu_temp, "CPUUsage": cpu_usage})