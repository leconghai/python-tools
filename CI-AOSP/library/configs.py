import json
import sys


class Configs:
    DIR = sys.path[0]
    ROOT_DIR = f"{DIR}"
    config_topo_path = f"{ROOT_DIR}/features/rpi_aosp/topology.json"
    json_topo = None

    @classmethod
    def get_topology(cls):
        if cls.json_topo is None:
            j_file = open(cls.config_topo_path, "r", errors='ignore', encoding="utf-8")
            cls.json_topo = json.load(j_file)
            j_file.close()
        return cls.json_topo

