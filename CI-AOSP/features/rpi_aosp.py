import os
import sys
from time import sleep, time
import pexpect
from library.configs import Configs
from library.hardwares.relay import Reset_device
from library.hardwares.sdmux import switch_sd
from library.hardwares.serial import serial_ter
from library.terminal.tool_ssh import Ssh_raw

DIR = sys.path[0]
DIR_OUT = f"{DIR}/out"


class rpi_aosp():
    def __init__(self, board_id, server_id, log_path=None):
        board_conf = Configs().get_topology()["boards"][board_id]
        self.aosp_conf = Configs().get_aosp_pi3()
        self.name = board_conf["name"]
        self.ip_addr = board_conf["ip_addr"]
        self.account = board_conf["account"]
        if log_path is None:
            log_path = f"{DIR_OUT}/board_{board_id}/"
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log_reset = open(f'{log_path}/reset.txt', 'w+')
        log_serial = open(f'{log_path}/serial.txt', 'w+')
        log_sw = open(f'{log_path}/switch.txt', 'w+')
        self.reset = Reset_device(reset_id_js=board_conf["reset_device"], log_file=log_reset)
        self.switch = switch_sd(sdmux_id=board_conf["sdmux"], log_file=log_sw)
        self.server = Ssh_raw(Configs().get_topology()["servers"][server_id])
        self.serial_ter = serial_ter(serial_id=board_conf["serial"], log_file=log_serial).picocom_ter()
        # setup dhcp server
        print("setup dhcp server")
        self.reset.power_on()
        sleep(5)
        ter_tmp = self.server.create_ter(log_file=None)
        self.server.root_cmd(ter_tmp, "sudo systemctl restart isc-dhcp-server.service")
        sleep(1)
        ter_tmp.close()

    def build_kernel(self):
        print("build kernel for pi aosp:")
        log_path = f"{self.log_path}/build/"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log_server = open(f'{log_path}/kernel.txt', 'w+')
        server_ter = self.server.create_ter(log_server)
        # check docker and start command
        print("check docker and start container")
        server_ter.send_expect("docker ps", "aosp-server")
        server_ter.send_expect("docker-aosp", "aosp")
        # build kernel
        print("build kernel and dts")
        server_ter.send_expect("cdkernel", "pi3/kernel/rpi")
        cmd = f"scripts/kconfig/merge_config.sh arch/arm/configs/bcm2709_defconfig kernel/configs/android-base.config " \
              f"kernel/configs/android-recommended.config"
        server_ter.send_expect(cmd, "CONFIG_ENABLE_DEFAULT_TRACERS", timeout=20)
        sleep(2)
        server_ter.send_expect("make -j 6 zImage", "zImage is ready", timeout=60)
        server_ter.sendline("make dtbs")
        sleep(2)
        cmd = "cp arch/arm/boot/zImage $ANDROID_BUILD_TOP/device/rpiorg/rpi3 ; sync"
        server_ter.sendline(cmd)
        server_ter.prompt()
        sleep(2)
        # build bootimage
        print("build bootimage")
        server_ter.send_expect("cdaosp", "/pi3")
        server_ter.sendline("source build/envsetup.sh")
        sleep(5)
        server_ter.send_expect("lunch aosp_rpi3-eng", "OUT_DIR=out", timeout=-1)
        sleep(2)
        server_ter.send_expect("make bootimage -j 6", "build completed successfully", timeout=600)
        server_ter.sendline("sync")
        sleep(2)
        print("build kernel success")
        server_ter.close()
        log_server.close()

    def startup_config(self):
        print("config adb for board")
        log_path = f"{self.log_path}/startup_config/"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        print("reset power")
        self.reset.power_off()
        print("plug sdcard to board")
        self.switch.mode_dut()
        sleep(3)
        self.reset.power_on()
        print("wait eth link of board up")
        self.serial_ter.prompt()
        self.serial_ter.expect("eth0: link up", timeout=100)
        sleep(10)
        print("init server terminal")
        log_server = open(f'{log_path}/server.txt', 'w+')
        server_ter = self.server.create_ter(log_server)
        print("check adb setup")
        server_ter.sendline(f"ping -c 5 {self.ip_addr}")
        server_ter.sendline(f"adb connect {self.ip_addr}:5555")
        sleep(5)
        server_ter.prompt()
        server_ter.sendline("adb devices")
        sleep(2)
        server_ter.expect(f"{self.ip_addr}:5555")
        server_ter.sendline(f"adb -s {self.ip_addr}:5555 root")
        sleep(5)
        print("adb config success")
        server_ter.prompt()
        self.serial_ter.prompt()
        server_ter.close()
        log_server.close()

    def flash_all_image(self):
        print("flash image to pi board")
        log_path = f"{self.log_path}/flash_all_image/"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        print("init server terminal")
        log_server = open(f'{log_path}/server.txt', 'w+')
        server_ter = self.server.create_ter(log_server)
        path = self.aosp_conf['path']['root']
        print(f"move path: {path}")
        server_ter.sendline(f"cd {path}")
        server_ter.prompt()
        print("setup env")
        cmd = self.aosp_conf['setup_env']
        server_ter.sendline(f"{cmd['1']}")
        sleep(5)
        server_ter.sendline(f"{cmd['2']}")
        server_ter.expect("TARGET_PRODUCT=aosp_rpi3", timeout=500)
        server_ter.prompt()
        print("plug sdcard to server")
        self.switch.mode_host()
        print("check disk name")
        found = 0
        for disk in self.aosp_conf["list_sdcard"]:
            try:
                server_ter.sendline(f"sudo fdisk -l /dev/{disk}")
                i = server_ter.expect(["password", "sdmux HS-SD/MMC"], timeout=2)
                if i == 0:
                    server_ter.sendline(self.server.password)
                    server_ter.expect("sdmux HS-SD/MMC", timeout=2)
            except pexpect.ExceptionPexpect as ex:
                continue
            found = 1
            break
        if found == 1:
            print(f"Disk is: {disk}")
        else:
            print(f"can not found disk")
            raise ex
        sleep(10)
        print(f"flash image to /dev/{disk}")
        cmd = f"{self.aosp_conf['flash_script']} {disk}"
        print(cmd)
        try:
            server_ter.sendline(cmd)
            i = server_ter.expect(["password", "SUCCESS"], timeout=600)
            if i == 0:
                server_ter.sendline(self.server.password)
                server_ter.expect("SUCCESS", timeout=600)
        except pexpect.ExceptionPexpect as ex:
            server_ter.prompt()
            server_ter.close()
            log_server.close()
            raise ex
        server_ter.sendline("sync")
        sleep(5)
        print("flash image success")
        server_ter.close()
        log_server.close()
