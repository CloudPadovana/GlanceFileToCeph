#!/usr/bin/env python

import glance_store._drivers.rbd as rbd
import hashlib
import os.path
import sys

from argparse import ArgumentParser
from oslo_config import cfg

CONF = cfg.CONF
_STORE_OPTS = [
    cfg.ListOpt('stores', default=['file', 'http'],
                help="List of stores enabled. Valid stores are: "
                      "cinder, file, http, rbd, sheepdog, swift, "
                      "s3, vsphere"),
    cfg.StrOpt('default_store', default='file',
               help="Default scheme to use to store image data. The "
                    "scheme must be registered by one of the stores "
                    "defined by the 'stores' config option."),
    cfg.IntOpt('store_capabilities_update_min_interval', default=0,
               help="Minimum interval seconds to execute updating "
                    "dynamic storage capabilities based on backend "
                    "status then. It's not a periodic routine, the "
                    "update logic will be executed only when interval "
                    "seconds elapsed and an operation of store has "
                    "triggered. The feature will be enabled only when "
                    "the option value greater then zero.")
]

_STORE_CFG_GROUP = 'glance_store'

def main():
    try:
        parser = ArgumentParser(prog="rbd_client")

        parser.add_argument("-c", "--config_file",
                            metavar="<config_file>",
                            default="/etc/glance/glance-api.conf")

        parser.add_argument("-i", "--image_id",
                            metavar="<image_id>",
                            required=True)

        parser.add_argument("-f", "--image_file",
                            metavar="<image_file>",
                            required=True)

        arguments = parser.parse_args(sys.argv[1:])
        config_file = arguments.config_file
        image_id = arguments.image_id
        image_file = arguments.image_file

        if not os.path.isfile(image_file):
            raise Exception("the file %s doesn't exists!" % image_file)

        image_size = os.path.getsize(image_file)

        sys.argv[1:] = []

        # the configuration will be into the cfg.CONF global data structure
        cfg.CONF(default_config_files=[config_file])
        cfg.CONF.register_opts(_STORE_OPTS, _STORE_CFG_GROUP)

        store = rbd.Store(CONF)
        store.configure_add()
        result = store.add(image_id, open(image_file), image_size)

        """
        if image_size != result[1]:
            raise Exception("the file size mismatch (%s != %s)" % (image_size, result[1]))
        """
        print("url: %s" % result[0])
        print("image size: %s" % result[1])
        print("checksum: %s" % result[2])
    except KeyboardInterrupt as e:
        print("Shutting down synergyclient")
        sys.exit(1)
    except Exception as e:
        print("ERROR: %s" % e)
        sys.exit(1)


if __name__ == "__main__":
    main()
