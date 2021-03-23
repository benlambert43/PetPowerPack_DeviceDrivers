import threading
import arduinoConnection
import mysqlSetup
import time

if __name__ == "__main__":
    # Run setup once
    mysqlSetup.mysqlinitsetup()

    # creating thread
    t1 = threading.Thread(target=arduinoConnection.arduinoEngine)
    t1.daemon = True
    t1.start()


    # keep daemon threads alive
    while True:
        time.sleep(1)