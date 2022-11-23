# flowercare

A python script which reads the values of configured flowercare sensors periodically and sends them via mqtt.

## Basic features

* Fetch values either for one or multiple sensors in a configurable interval
* Read temperature, moisture, light, conductivity and battery values
* Send the data to one topic per sensor
* Configure a different interval either per sensor or per value of a sensor
* Resend the last fetched value if only other values are currently fetched for a sensor

## Basic setup

First we clone the repository, then we install some packages and register the system service.

### Clone repository

You can install the script to any directory you like. Only make sure to replace the path in the service file later!

```bash
git clone https://github.com/Tom-Hirschberger/flowercare.git
```

### Python packages

```bash
sudo pip3 install miflora
sudo pip3 install bluepy
sudo pip3 install paho-mqtt
sudo pip3 install json5
```

### System service

A service file to register the script as systemd service is included in this repository.  
**Make sure to replace the user and the paths with the ones in your setup!**

Copy the service file to systemd directory:

```bash
sudo cp flowercare.service /etc/systemd/system/
```

Register the service to autostart:

```bash
sudo systemctl enable flowercare.service
```

After you created the flowercare.json file (or a other named file if you replaced the name in the service file) you can control the service with the following commands:

Start:

```bash
sudo systemctl start flowercare.service
```

Stop:

```bash
sudo systemctl stop flowercare.service
```

Status:

```bash
sudo systemctl status flowercare.service
```

## Configuration

The configuration is structured in different parts: "general", "mqtt" an "sensors".

You will learn to find your sensors and how to configure the differnt sections. You can use the example configuration ([flowercare.json.example](./flowercare.json.example)) as a start.

### Find the addresses of your sensors

First we need to know the mac addresses of the sensors (basically the bluetooth hardware address). Credits to [https://tutorials-raspberrypi.de](https://tutorials-raspberrypi.de/raspberry-pi-miflora-xiaomi-pflanzensensor-openhab/).
Enable bluetooth on your divice and use the following command to search for your sensors:

```bash
sudo hcitool lescan
```

The output will look something like:

```bash
LE Scan ...
C4:7C:8D:66:1A:C3 (unknown)
C4:7C:8D:66:1A:C3 Flower care
D4:36:39:C7:DB:BD (unknown)
```

The ones with name "Flower care" are the ones we need the addresses of.

### General section

| Option  | Description | Type | Default
|-------- | ----------- | ---- | -------
| sleep | The time between intervals of fetching new values in seconds. Be careful with fetching the values to often. Fetching the values costs a lot of energy and the battery will be drained very quickly if the interval is to small. | Integer | 1800 |
| resendValueOnPartialSkip | It is possible to fetch values of sensors in different intervals than the general "beat" of the module. If no new values are fetched but you want to send a output via MQTT that contains all keys you can send the last fetched values instead. | Boolean | True |

### MQTT section

| Option  | Description | Type | Mandatory | Default |
|-------- | ----------- | ---- | --------- | ------- |
| clientName | The name that will be used to register this client to the MQTT broker. | String | true | None |
| host | The hostname or IP of the MQTT broker. | String | true | None |
| port | The network port of the MQTT broker. Usally 1883. | Integer | true | None |
| username | The username to connect to the MQTT broker. | String | false | None |
| password | The password to connect to the MQTT broker. | String | false | None |

### Sensors section

| Option  | Description | Type | Mandatory | Default |
|-------- | ----------- | ---- | --------- | ------- |
| topic | The MQTT topic the result object should be send to. | String | true | None |
| name | The name of the sensor. Currently this value will be used for debug output only. | String | true | None |
| mac | The bluetooth address of the sensor. | String | true | None |
| readTemperature | Should the temperature value be fetched? | Boolean | false | false |
| readMoisture | Should the moisture value be fetched? | Boolean | false | false |
| readLight | Should the light value be fetched? | Boolean | false | false |
| readConductivity | Should the conductivity value be fetched? | Boolean | false | false |
| readBattery | Should the battery value be fetched? | Boolean | false | false |
| interval | Normally all sensors get fetched after each sleep. You can change this behavior with this option. See the "inveral" section for all options | Integer or Dictionary | 1 |

#### interval

The interval to fetch the values of a sensor can either be a simple Integer (which it is in default with value 1) or a dictionary. If it is set to a interger all enabled values (read...) will be fetched each "interval" times.  

The dictionary can contain a differnt interval for each value. Meaning you can fetch i.e. the light value more often than i.e. the battery level.

| Option  | Description | Type | Mandatory | Default |
|-------- | ----------- | ---- | --------- | ------- |
| temperature | The interval of the temperature value. | Integer | false | 1 |
| moisture | The interval of the moisture value. | Integer | false | 1 |
| light | The interval of the light value. | Integer | false | 1 |
| conductivity | The interval of the conductivity value. | Integer | false | 1 |
| battery | The interval of the battery value. | Integer | false | 1 |


### Example

The following example contains all possible configuration options:

```json
{
    "general": {
        "sleep": 1800,
        "resendValueOnPartialSkip": true
    },
    "mqtt": {
        "clientName": "mirroreg-flowercare",
        "host": "10.1.1.1",
        "port": 1883,
        "username": "test",
        "password": "test123"
    },
    "sensors": [
        {
            "topic": "flowercare/flowerone",
            "interval": 1,
            "name": "flowerone",
            "mac": "AA:BB:CC:DD:EE:FF",
            "readTemperature": true,
            "readMoisture": true,
            "readLight": false,
            "readConductivity": false,
            "readBattery": true
        },
        {
            "topic": "flowercare/flowertwo",
            "interval": {
                "temperture": 1,
                "moisture": 2,
                "battery": 5
            },
            "name": "flowertwo",
            "mac": "AA:BB:CC:AA:BB:CC",
            "readTemperature": true,
            "readMoisture": true,
            "readBattery": true
        }
    ]
}
```
>>>>>>> main
