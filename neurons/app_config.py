import json
import traceback
from abc import ABC
import bittensor as bt


class AppConfig(ABC):

    def __init__(self, config_path='application.json'):
        self.config_path = config_path
        self.value = self.default_app_config()
        try:
            self.load_app_config()
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()

    def default_app_config(self):
        bt.logging.info("start default_app_config")
        value = {
            "application": {
                "miner": {
                    "show_input": False,
                    "black_list_enable": True,
                    "blacklist_hotkeys": [],
                    "whitelist_hotkeys": [],
                    "custom_model": {
                        "active": True,
                        "num_input": [50]
                    },
                    "standard_model": {
                        "urls": []
                    },
                    "test_net": {
                        "enable_input_from_file": False,
                        "input_dir_path": "/root/head-tail-llm-detection",
                        "processed_dir_path": "/root/head-tail-llm-detection"
                    },
                    "num_make_incorrect": 0
                },
                "validator": {
                    "target_miner_uids": [-1],
                    "test_net": {
                        "enable_write_input_to_file": False,
                        "output_dir_path": "/root/head-tail-llm-detection"
                    }
                }
            },
            "redis": {
                "active": False,
                "verify_data": {
                    "urls": [
                        "http://69.67.150.21:8080/check-exists",
                        "http://103.219.170.221:8080/check-exists"
                    ]
                }
            },
            "50_50_standard_model": {
                "active": True
            }
        }
        return value

    def allow_show_input(self):
        try:
            return self.value['application']['miner']['show_input']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return True

    def enable_blacklist_validator(self):
        try:
            return self.value['application']['miner']['black_list_enable']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return False

    def get_blacklist_hotkeys(self):
        try:
            return self.value['application']['miner']['blacklist_hotkeys']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return []

    def get_whitelist_hotkeys(self):
        try:
            return self.value['application']['miner']['whitelist_hotkeys']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return []

    def get_miner_input_log_dir_path(self):
        try:
            return self.value['application']['miner']['miner_input_log_dir']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return '/root/llm-detection-model-embedding/sample_data'

    def get_miner_test_input_dir_path(self):
        try:
            return self.value['application']['miner']['test_net']['input_dir_path']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return '/root/head-tail-llm-detection'

    def get_miner_test_processed_dir_path(self):
        try:
            return self.value['application']['miner']['test_net']['processed_dir_path']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return '/root/head-tail-llm-detection'

    def enable_miner_get_input_from_file(self):
        try:
            return self.value['application']['miner']['test_net']['enable_input_from_file']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return False

    def get_server_urls(self):
        try:
            return self.value['application']['miner']['server']['urls']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return []

    def get_server_timeout(self):
        try:
            return self.value['application']['miner']['server']['timeout']
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
        return 15

    def load_app_config(self):
        bt.logging.info("start load_app_config")

        try:
            with open(self.config_path, 'r') as file:
                self.value = json.load(file)
        except Exception as e:
            bt.logging.error(e)
            traceback.print_exc()
            self.value = self.default_app_config()
        finally:
            bt.logging.info("finish load_app_config " + str(self.value))


if __name__ == '__main__':
    app_config = AppConfig('/Users/nannan/IdeaProjects/bittensor/llm-detection-model-embedding/application.json')
    print(app_config)
    print(app_config.value)
    print('allow_show_input', app_config.allow_show_input())
    print('enable_blacklist_validator', app_config.enable_blacklist_validator())
    print('get_blacklist_hotkeys', app_config.get_blacklist_hotkeys())
    print('get_whitelist_hotkeys', app_config.get_whitelist_hotkeys())
    print('get_miner_input_log_dir_path', app_config.get_miner_input_log_dir_path())
    print('get_miner_test_input_dir_path', app_config.get_miner_test_input_dir_path())
    print('get_server_url', app_config.get_server_urls())
    print('get_server_timeout', app_config.get_server_timeout())


    while True:
        ...
