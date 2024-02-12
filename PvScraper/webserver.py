import flask
import threading
import time

global app
app = flask.Flask(__name__)

global dataArray, currentdata

dataArray = []

currentdata = None  # Make currentdata a global variable


class WebServer:
    def __init__(self, scraper) -> None:
        global currentdata
        self.scraper = scraper
        currentdata = None  # Initialize currentdata here
        
        print("WebServer initialized.")
        
        tdata = threading.Thread(target=self.collect_data)
        tdata.start()
        
        app.run(host="0.0.0.0", debug=True)
        
    
    def collect_data(self):
        global currentdata
        t1 = threading.Thread(target=self.scraper.get_data, args=(None,))
        t1.start()
        
        while str(self.scraper.data) == "[('Realtime Values', 'Battery Information'), ('DC Info', 'Device Information')]" or self.scraper.data == None:
            time.sleep(0.2)
        
        count = 0
        while True:
            if count >= 2:
                count = 0
                dataArray.append(self.scraper.data)
                
            currentdata = self.scraper.data
            time.sleep(1)
            
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
        return flask.jsonify(dataArray)