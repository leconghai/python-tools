import sys

from library.configs import Configs
from library.hardwares.relay import Relay
from library.hardwares.sdmux import SDmux
from library.hardwares.serial import Serial


class Reset_device(Relay):
    def __init__(self, reset_id_js, log_file=sys.stdout):
        reset_devices = Configs().get_topology()["reset_devices"][reset_id_js]
        relay = Configs().get_topology()["relays"][reset_devices["relay"]]
        server = Configs().get_topology()["servers"][relay["server"]]
        super().__init__(server, relay["name"], log_file)
        self.port = reset_devices["port"]

    def power_reset(self):
        self.p_off(self.port)
        self.p_on(self.port)

    def power_off(self):
        self.p_off(self.port)

    def power_on(self):
        self.p_on(self.port)


class switch_sd(SDmux):
    def __init__(self, sdmux_id, log_file=sys.stdout):
        sdmux_conf = Configs().get_topology()["sdmux"][sdmux_id]
        server = Configs().get_topology()["servers"][sdmux_conf["server"]]
        super().__init__(server, sdmux_conf["device"], log_file)


class serial_ter(Serial):
    def __init__(self, serial_id, log_file=sys.stdout):
        serial_conf = Configs().get_topology()["serials"][serial_id]
        server = Configs().get_topology()["servers"][serial_conf["server"]]
        super().__init__(server, log_file)
        self.device = serial_conf["device"]
        self.port = serial_conf["port"]

    def picocom_ter(self):
        return self.picocom(self.device)

    def telnet_com(self):
        return self.telnet(self.port)
