import datetime
import serial
import re
import subprocess
import sqlite3 as sl
import time

VAR_PORT = 'COM3'
VAR_WEBSITE = "www.google.com"


def ping_the_web(host):
    """
    Ping a host to get ms latency
    Returns the ping in ms
    """

    packet = 69
    ping = subprocess.getoutput(f"ping -w {packet} {host}")
    return ping


def get_active_network():
    """
    Get the current active network
    return network name and connectivity type
    """
    # using the check_output() for having the network term retrieval
    interfaces = str(subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']))
    interfaces = interfaces.replace('xff', '').replace('x82', 'e').replace('\\r', '').replace('\\n', '') \
        .replace('\\', '').replace('x90', "BREAK").replace(' ', '')

    # decode it to strings
    result_network = re.search(r"Profil:(.*)BREAK", str(interfaces))

    return result_network.group(1)


def get_the_ping(website_to_check=VAR_WEBSITE):
    """
    This function returns one ping observation from the current network

    :param website_to_check: str
    :return: ping observation
    """
    # Get the active network
    try:
        active_network = get_active_network()
    except AttributeError:
        print('{}: No network'.format(datetime.datetime.now()))
        active_network = ''

    # Gather current datetime information and set the ping data variable
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Get ping data from network
    try:
        raw_ping = ping_the_web(website_to_check)
        regex_ping = r"Minimum = ([0-9]+)ms, Maximum = ([0-9]+)ms, Moyenne = ([0-9]+)ms"
        clean_ping = re.search(regex_ping, raw_ping)

        # Build csv response
        ping_results = [current_datetime, int(clean_ping.group(1)), int(clean_ping.group(2)),
                        int(clean_ping.group(3)), active_network]

    except AttributeError:
        # Build error csv response
        ping_results = [current_datetime, -1, -1, -1, active_network]
        print("Passed... No network connectivity")

    # Return the ping results
    return ping_results


def get_current_coordinates(port=VAR_PORT):
    """
    Gather coordinates of the current location

    :param port: names of the port to use in gathering coordinates
    :return: current timestamp & coordinates
    """

    # print("Get coordinates")

    s = serial.Serial(port, baudrate='4800', bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE)
    if not s.isOpen():
        s.open()
    # print('com3 is open', s.isOpen())

    # Flush input & output
    s.flushInput()
    s.flushOutput()

    current_coordinates = ""

    while current_coordinates == "":

        answer = s.readline()
        answer = str(answer)

        if answer.startswith("b'$GNGGA"):
            raw_coordinates = answer.replace("b'", "").split(',')
            latitude_value = raw_coordinates[2]
            latitude_type = raw_coordinates[3]
            longitude_value = raw_coordinates[4]
            longitude_type = raw_coordinates[5]
            gps_fix_status = raw_coordinates[6]

            date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            current_coordinates = [date, latitude_value, latitude_type, longitude_value, longitude_type, gps_fix_status]

    return current_coordinates


def write_in_database(table, data):
    con = sl.connect("train.db")
    cur = con.cursor()
    cur.execute("""INSERT INTO {} VALUES {}""".format(table, data))

    con.commit()


def gather_data():
    """
    This function runs the two functions to gather the location and the ping
    """

    # Gather run timestamp
    ts_gathering = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Creating the unique id
    unique_location_id = "L" + ''.join(filter(str.isdigit, ts_gathering))
    unique_ping_id = "P" + ''.join(filter(str.isdigit, ts_gathering))

    # Gather the location
    location = get_current_coordinates()
    data_to_insert = "('{}','{}','{}','{}','{}','{}',{})" \
        .format(unique_location_id, location[0], location[1], location[2], location[3], location[4], location[5])
    write_in_database("location", data_to_insert)

    # Gather the current ping status
    ping_status = get_the_ping()
    data_to_insert = "('{}','{}',{},{},{},'{}')" \
        .format(unique_ping_id, ping_status[0], ping_status[1], ping_status[2], ping_status[3], ping_status[4])
    write_in_database("ping", data_to_insert)

    print("Data inserted: job id -> " + str(ts_gathering))


if __name__ == '__main__':
    while True:
        time.sleep(1)  # Set a 1-second timer for each loop
        gather_data()
