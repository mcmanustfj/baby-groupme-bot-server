#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
import re
import sys

# i shamelessly copied just about everything except for most of the do_POST method
# HTTPRequestHandler class
class request_handler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):  # this entire method is unnecessary
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Send message back to client
        message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return
    # POST
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        message = "<html><body><h1>POST!</h1></body></html>" # just for testing
        self.wfile.write(bytes(message, "utf8"))

        jsonstring = str(self.data_string, "utf-8").strip() # Get POST data

        data = json.loads(jsonstring)  # turn it into a dict
        print(json.dumps(data, sort_keys=True, indent=4)) # just so you have something to look at in the console

        if "xkcd" in data["text"] and data["sender_type"] != "bot": # check for xkcd and avoid replying to self
            string = data["text"] # message body
            string.replace("xkcd","") # honestly this doesn't matter unless i want to do something else with it but i do it with most bot commands
            match = re.search("\d{1,4}", string) # search for a four digit number
            if match:                            # TODO search by name if there's no number?
                xkcdnum = match.group(0)         # how the fuck does regex even work?
                url = 'http://xkcd.com/'+xkcdnum # get the URL
                dataurl = url + '/info.0.json'   # URL for the json (thank you Randall Munroe <3)
                xkcdjson_raw = requests.get(dataurl)
                if xkcdjson_raw.status_code != 200:
                    xkcdjson_raw = requests.get('http://xkcd.com/info.0.json')
                    url = 'http://xkcd.com/'
                xkcdjson = json.loads(xkcdjson_raw.text)
                print(json.dumps(xkcdjson, sort_keys=True, indent=4))
                img = xkcdjson["img"] # TODO run this through the groupme image service api like they asked me to
                message = {"text" : url + '\n' + xkcdjson["safe_title"] + '\n' + 'Title Text:' + xkcdjson["alt"], 'bot_id' : '[get your own botid]', "attachments" : [{"type" : "image" , "url" : img}]}
                requests.post('https://api.groupme.com/v3/bots/post', data=json.dumps(message))
        return



def run():
    print('starting server...')

  # Server settings
    if sys.argv[1:]: # you can run this from the command line and the argument is the port to run the server on
        port = int(sys.argv[1])
    else:
        port = 8080 # defaults to 80 but that requires root access on some computers
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, request_handler)
    print('running server on port {}...'.format(port))
    httpd.serve_forever()


run()
