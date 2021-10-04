import argparse
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from databases import mongodb

ap = argparse.ArgumentParser()

ap.add_argument("-u", "--until", required=True, help="until")
ap.add_argument("-s", "--since", required=True, help="since")
ap.add_argument("-q", "--query", required=True, help="query")

args = vars(ap.parse_args())

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
driver = webdriver.Chrome(executable_path="chromedriver.exe", desired_capabilities=caps)

driver.get(
  "https://twitter.com/search?q=until%3A"+args['until']+"%20since%3A"+args['since']+"%20"+args['query']+"&src=typed_query&f=live")

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

i=0
with open("data.csv", "a") as data_file:
  while True:
    data = driver.execute_script('return document.data')
    if not data:
      driver.quit()
      break
    driver.execute_script('document.data = []')
    for item in data:
      for str_id, obj in item['globalObjects']['tweets'].items():
        id = mongodb.get_query_id(obj['full_text'])
        if id is not None:
          data_file.write("{},{},{},{},{}\n".format(str_id, id, datetime.datetime.strptime(obj['created_at'], '%a %b %d %H:%M:%S +0000 %Y').timestamp(), int(obj['favorite_count']), int(obj['reply_count'])))
          i = i + 1
          print(i)
    time.sleep(5)