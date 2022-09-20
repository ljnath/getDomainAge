
import argparse
import os
import sys

from getDomainAge import GetDomainAge, app

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', nargs=1, help='Complete path to application config file')
    args = parser.parse_args()

    DEFAULT_CONFIG_FILE = 'config.json'
    
    if not args.config and not os.path.exists(DEFAULT_CONFIG_FILE):
        parser.print_help()
        sys.exit(1)

    config_file = args.config[0] if args.config else DEFAULT_CONFIG_FILE

    get_domain_age = GetDomainAge(config_file)
    get_domain_age.run()
