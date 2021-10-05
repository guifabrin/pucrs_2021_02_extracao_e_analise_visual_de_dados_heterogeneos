import datetime
import sys
import threading
import time
from concurrent.futures.thread import ThreadPoolExecutor

from selenium import webdriver
from databases import mongodb
from datetime import date, timedelta

imported = 0
inserted = 0
futures = []
data = []


def date_range(start_date, finish_date):
    for n in range(int((finish_date - start_date).days)):
        yield start_date + timedelta(n)


def navigate(date_init, date_end, query):
    global imported
    global data
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
    driver.get(
        "https://twitter.com/search?q=until%3A" + date_end.strftime(
            "%Y-%m-%d") + "%20since%3A" + date_init.strftime("%Y-%m-%d") + "%20" + query + "&src=typed_query&f=live")

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
                id = mongodb.get_query_id(obj['full_text'])
                if id is not None:
                    data.append({
                        "i": str_id,
                        "q": id,
                        "d": datetime.datetime.strptime(obj['created_at'], '%a %b %d %H:%M:%S +0000 %Y').timestamp(),
                        "f": int(obj['favorite_count']),
                        "r": int(obj['reply_count'])
                    })
                    imported = imported + 1
        time.sleep(5)
    driver.quit()


def update_progress(progress):
    global imported, futures, inserted
    bar_length = 30
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1
    block = int(round(bar_length * progress))
    total_progress = progress * 100
    total_progress = total_progress if total_progress > 0 else 1
    text = "\rPercent: [{0}] {1}% {2} .. {3}".format("#" * block + "-" * (bar_length - block), total_progress, imported, inserted)
    sys.stdout.write(text)
    sys.stdout.flush()


def print_metrics():
    while True:
        total = len(futures)
        complete = len(list(filter(lambda b: b, map(lambda f: f.done(), futures))))
        if total > 0:
            update_progress(complete / total)
        time.sleep(0.3)


def insert_data():
    global inserted
    while True:
        if len(data) > 0:
            mongodb.store(data.pop())
            inserted += 1


threading.Thread(target=print_metrics, args=()).start()
threading.Thread(target=insert_data, args=()).start()

with ThreadPoolExecutor(max_workers=5) as executor:
    for query in ['brumadinho', 'mariana', 'petrobras', 'pandemia']:
        start_date = date(2010, 1, 1)
        finish_date = date(2021, 12, 31)
        for date_init in date_range(start_date, finish_date):
            date_end = date_init + timedelta(days=1)
            futures.append(executor.submit(navigate, date_init, date_end, query))
