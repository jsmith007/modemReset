#!/usr/bin/env python
import subprocess, json, requests, argparse, time, sys
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


hs100Script = "/Path/To/Script"
plugAddress = "IP.Addr.To.Plug"

def connected_to_internet(url='http://www.google.com/', timeout=5,test=False):
        if (test):
                logger.info("Testing connectivity to %s ", url)
        try:
                _ = requests.get(url, timeout=timeout)
                if (test):
                        logger.info("Connectivity Successful")
                return True
        except requests.ConnectionError:
                if (test):
                        logger.info("No internet connection available.")
                return False

def check_speed(test=False):
        if (test):
                logger.info("Checking connection speed")
        speedData = json.loads(subprocess.check_output(["speedtest-cli","--json"]))
        if (test):
                logger.info( "Ping time: %s ms", speedData["ping"])
                logger.info( "Speed: %s Mbps", speedData["download"]/1000000)
        if (speedData["ping"] > 100):
                return False
        if ((speedData["download"]/1000000) < 20):
                return False
        return True

def sendPowerCycle():
        # Errors: What dey do huh?

        # if plug has been on less than 5 minutes then probably dont powersycyle
        plugCheck = subprocess.check_output([hs100Script, "-i ", plugAddress, "check"]).rstrip().split("\t")[1]
        statusData = json.loads(subprocess.check_output([hs100Script, "-i ", plugAddress, "status"]))
        if (plugCheck == "ON" and statusData["system"]["get_sysinfo"]["on_time"] <= 300):
                logger.info( "Plug is on but for less than 5 minutes . Not power cycling")
                return
        # turn off power
        subprocess.call([hs100Script, "-i ", plugAddress,, "off"])
        # wait 30 seconds
        time.sleep(30)
        # turn on power
        subprocess.call([hs100Script, "-i ", plugAddress,, "on"])


def main():
        # args
        parser = argparse.ArgumentParser(description='Checks connectivity.')
        parser.add_argument('--test', dest='test', action='store_true',
                    help='Tests for connectivity but will not do power reset')
        parser.add_argument('--forceReset', dest='forceReset', action='store_true',
                    help='Does not perform connectivity checks, just do power reset')

        args = parser.parse_args()

        if (args.forceReset):
                logger.info("Forcing power cycle")
                sendPowerCycle()
                sys.exit(0)

        # check connectivity and speed
        connectGood = False
        speedGood = False
        try:
                connectGood = connected_to_internet(test=args.test)
        except:
                e = sys.exc_info()[0]
                connectGood = False

        try:
                if (connectGood):
                        speedGood = check_speed(test=args.test)
        except:
                e = sys.exc_info()[0]
                speedGood = False

        if (args.test):
                # prints the test results
                logger.info( "Connectivity Good: %s", connectGood)
                logger.info( "Speed Good: %s", speedGood)
        elif (not (connectGood or speedGood)):
                sendPowerCycle()

if __name__ == "__main__":
        main()
