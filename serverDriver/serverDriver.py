import threading
import arduinoConnection
import mysqlSetup
import time

if __name__ == "__main__":
    mysqlSetup.mysqlinitsetup()

    # creating thread
    t1 = threading.Thread(target=arduinoConnection.arduinoEngine)
    t1.daemon = True
    # starting thread 1
    t1.start()
    while True:
        time.sleep(1)