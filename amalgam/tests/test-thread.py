import threading, time

class One(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def worker(self):
        while True:
            print("Thread {} {}".format(threading.current_thread().ident, self))
            time.sleep(1)

    def run(self):
        t = threading.Thread(target=self.worker)
        t.start()

        while True:
            print("Main thread running {}".format(self))
            time.sleep(1)

        t.join

if __name__ == "__main__":
    o = One()
    o.start()
    o.join()