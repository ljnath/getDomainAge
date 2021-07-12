
import argparse
import sys
from getDomainAge import app
from getDomainAge import GetDomainAge

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', nargs=1, help='Path to application config file')
    args = parser.parse_args()
    
    if not args.config:
        parser.print_help()
        sys.exit(1)
        
    config_file = args.config[0]
    
    get_domain_age = GetDomainAge(config_file)
    get_domain_age.run()