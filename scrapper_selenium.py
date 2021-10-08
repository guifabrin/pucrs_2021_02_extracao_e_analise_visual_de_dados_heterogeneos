import argparse
import datetime
import os
import threading
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import mongodb
from datetime import timedelta

imported = 0
inserted = 0
fifo_tweets = []
finished = False


def date_range(date_a, date_b):
    for n in range(int((date_b - date_a).days)):
        yield date_a + timedelta(n)


def navigate(init, end, search):
    global imported, fifo_tweets
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
    driver.get(
        "https://twitter.com/search?q=until%3A" + end.strftime(
            "%Y-%m-%d") + "%20since%3A" + init.strftime("%Y-%m-%d") + "%20" + search + "&src=typed_query&f=live")

    driver.execute_script("""
              (function(xhr) {
                  document.data = []
                  var XHR = XMLHttpRequest.prototype;
                  var open = XHR.open;
                  var send = XHR.send;
                  var setRequestHeader = XHR.setRequestHeader;
                  XHR.open = function(method, url) {
                      this._method = method;
                      this._url = url;
                      this._requestHeaders = {};
                      this._startTime = (new Date()).toISOString();
                      return open.apply(this, arguments);
                  };
                  XHR.setRequestHeader = function(header, value) {
                      this._requestHeaders[header] = value;
                      return setRequestHeader.apply(this, arguments);
                  };
                  XHR.send = function(postData) {
                      this.addEventListener('load', function() {
                          var endTime = (new Date()).toISOString();
                          var myUrl = this._url ? this._url.toLowerCase() : this._url;
                          if(myUrl) {
                              if (postData) {
                                  if (typeof postData === 'string') {
                                      try {
                                          // here you get the REQUEST HEADERS, in JSON format, so you can also use JSON.parse
                                          this._requestHeaders = postData;
                                      } catch(err) {
                                          console.log('Request Header JSON decode failed, transfer_encoding field could be base64');
                                          console.log(err);
                                      }
                                  } else if (typeof postData === 'object' || typeof postData === 'array' || typeof postData === 'number' || typeof postData === 'boolean') {
                                          // do something if you need
                                  }
                              }
                              var responseHeaders = this.getAllResponseHeaders();
                              if ( this.responseType != 'blob' && this.responseText) {
                                  try {
                                      var arr = this.responseText;
                                      if(this._url.indexOf('adaptive.json')>-1){
                                        document.data.push(JSON.parse(arr))
                                      }
                                  } catch(err) {
                                      console.log("Error in responseType try catch");
                                      console.log(err);
                                  }
                              }

                          }
                      });
                      return send.apply(this, arguments);
                  };
              })(XMLHttpRequest);
              setInterval(()=>{
                  window.scrollTo(0,document.body.scrollHeight);
              }, 1000)
              """)
    time.sleep(5)
    while True:
        data = driver.execute_script('return document.data')
        if not data:
            break
        driver.execute_script('document.data = []')
        for item in data:
            for str_id, obj in item['globalObjects']['tweets'].items():
                mongo_db_id = mongodb.get_query_id(obj['full_text'])
                if id is not None:
                    fifo_tweets.append({
                        "i": str_id,
                        "q": mongo_db_id,
                        "d": datetime.datetime.strptime(obj['created_at'], '%a %b %d %H:%M:%S +0000 %Y').timestamp(),
                        "f": int(obj['favorite_count']),
                        "r": int(obj['reply_count'])
                    })
                    imported = imported + 1
        time.sleep(5)
    driver.quit()


def insert_data():
    global inserted, fifo_tweets
    while True:
        try:
            print("Inserted versus imported", inserted, imported)
            result = fifo_tweets
            fifo_tweets = []
            if len(result) > 0:
                mongodb.store_all(result)
                inserted += len(result)
        except Exception as ex:
            print("Error", ex)
        time.sleep(1)
        if finished:
            print("Finished")
            break


threading.Thread(target=insert_data, args=()).start()

ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True, help="query to search")
ap.add_argument("-s", "--since", required=True, help="since date")
ap.add_argument("-u", "--until", required=False, help="until date")

args = vars(ap.parse_args())
print("\n\nInit")
start_date = datetime.datetime.strptime(args['since'], '%Y-%m-%d').date()
delta = datetime.timedelta(days=1)
if args['until']:
    finish_date = datetime.datetime.strptime(args['until'], '%Y-%m-%d').date()
else:
    finish_date = start_date + delta
log_filename = "logs\\scrapper_" + args['query'] + ".txt"
if not os.path.exists(log_filename):
    log_file = open(log_filename, "a")
    log_file.write("")
    log_file.close()
lines = open(log_filename, "r").read().split('\n')
while start_date <= finish_date:
    date_init = start_date
    start_date += delta
    inserted = 0
    while True:
        if date_init.isoformat() in lines:
            print('Skipping ' + date_init.isoformat())
            break
        navigate(date_init, start_date, args['query'])
        if inserted == 0:
            log_file = open(log_filename, "a")
            log_file.write(date_init.isoformat() + "\n")
            log_file.close()
            break
finished = True
