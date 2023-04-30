import sys
from time import sleep


from features.rpi_aosp.rpi_aosp import rpi_aosp

DIR = sys.path[0]
DIR_OUT = f"{DIR}/../logfile/"
# restart service
# sudo service ser2net restart
# sudo systemctl restart isc-dhcp-server.service
# sudo systemctl status isc-dhcp-server.service

if __name__ == '__main__':
    board_rpi_aosp = rpi_aosp(board_id="1", server_id="153")

    while 1:
        mode = ""
        print("all,flash,setup,kernel")
        mode = input("enter mode:")
        match mode:
            case "flash":
                board_rpi_aosp.flash_all_image()
            case "setup":
                board_rpi_aosp.startup_config()
            case "all":
                board_rpi_aosp.flash_all_image()
                board_rpi_aosp.startup_config()
            case "on":
                board_rpi_aosp.reset.power_on()
            case "off":
                board_rpi_aosp.reset.power_off()
            case "kernel":
                board_rpi_aosp.build_kernel()
                board_rpi_aosp.flash_all_image()
                board_rpi_aosp.startup_config()
            case "q":
                print("quit program")
                break
            case _:
                print("wrong mode")
        sleep(1)
