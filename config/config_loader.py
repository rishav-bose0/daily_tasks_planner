import os
import sys

import anyconfig


class ConfigReader:
    def __init__(self):
        self.config = {}
        self.config_file_dir = os.path.dirname(os.path.abspath(__file__))
        self.env_prefix = "env|"

    def get_config_file_path(self, file_name) -> str:
        return os.path.join(self.config_file_dir, file_name)

    def replace_env_values(self) -> None:
        for key, value in self.config.items():
            if isinstance(value, str) and value.startswith(self.env_prefix):
                value = value.strip(self.env_prefix)
                os_value = os.environ.get(value, None)
                if os_value is None:
                    sys.exit("No Environment variable available for : \"{0}\"".format(value))
                self.config[key] = os_value

    def read_config(self) -> dict:

        env_conf_file = self.get_config_file_path(os.environ.get('APP_ENV', "dev") + '.toml')
        default_conf_file = self.get_config_file_path('default.toml')

        self.config = anyconfig.load([default_conf_file, env_conf_file], ac_parser="toml",
                                     ac_merge=anyconfig.MS_DICTS_AND_LISTS)
        self.replace_env_values()
        return self.config
