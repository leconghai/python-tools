import json
import sys


class Configs:
    DIR = sys.path[0]
    ROOT_DIR = f"{DIR}"
    config_topo_path = f"{ROOT_DIR}/configs/topology.json"
    json_topo = None
    config_aosp_pi3_path = f"{ROOT_DIR}/configs/aosp_pi3.json"
    json_feature = None

    @classmethod
    def get_topology(cls):
        if cls.json_topo is None:
            j_file = open(cls.config_topo_path, "r", errors='ignore', encoding="utf-8")
            cls.json_topo = json.load(j_file)
            j_file.close()
        return cls.json_topo

    @classmethod
    def get_aosp_pi3(cls):
        if cls.json_feature is None:
            j_file = open(cls.config_aosp_pi3_path, "r", errors='ignore', encoding="utf-8")
            cls.json_feature = json.load(j_file)
            j_file.close()
        return cls.json_feature
