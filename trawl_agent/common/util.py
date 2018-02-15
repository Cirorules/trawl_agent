import yaml
import os

TRAWL_AGENT_CONFIG = '/etc/sysconfig/trawl/trawl.yaml'
TRAWL_CONF_D = '/etc/sysconfig/trawl/conf.d/'


def confd_modules():
    files = os.listdir(TRAWL_CONF_D)
    mods = [os.path.splitext(x)[0] for x in files]

    return mods


def read_conf(mod):
    file = "{0}/{1}.yaml".format(TRAWL_CONF_D, mod)
    if os.path.isfile(file):
        with open(file) as f:
            config = yaml.safe_load(f)

        return config
    else:
        return None


class ReadAgentConf(object):
    def __init__(self):
        self.agent_file = TRAWL_AGENT_CONFIG

    def read_global(self):
        if os.path.isfile(self.agent_file):
            with open(self.agent_file) as f:
                config = yaml.safe_load(f)
        else:
            config = None

        return config

    def read_section(self, sect):
        if os.path.isfile(self.agent_file):
            with open(self.agent_file) as f:
                config = yaml.safe_load(f)

        return config[sect]

