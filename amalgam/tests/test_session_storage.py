'''
Can I store objects, functions in session? 
'''
import threading
from flask import Flask, copy_current_request_context, session

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = 'my precious'

camara = {}

class Animal:
    def __init__(self, name):
        self.name = name


@app.route('/one')
def one():
    global camara
    @copy_current_request_context
    def x():
        camara['status'] = "done"      

    t = threading.Thread(target=x)
    t.start()
    return "One"



@app.route('/two')
def two():
    global camara    
    status = camara['status']
    return "Two: {}".format(status)



# start the server with the 'run()' method
if __name__ == '__main__':		
	app.run()