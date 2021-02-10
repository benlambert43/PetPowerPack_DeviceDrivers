# PetPowerPack_DeviceDrivers

Device drivers for the client and server hardware devices used in hardware level communication between the base station (server) and the remote device (client). 

Python driver controls code injection via serial to modify the execution environment on the device. 

HC12 Radio communication is one way due to the limitations of switching SoftwareSerial input from GPS to HC12; cannot listen to both GPS and HC12 at once. 

Python environment is intended to be used with pipenv.

## Diagram:

![Diagram](https://github.com/benlambert43/PetPowerPack_DeviceDrivers/blob/main/diagram.jpg)
