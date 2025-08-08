import argparse


def main1():
    parser = argparse.ArgumentParser(prog='stock-manager')
    subparsers = parser.add_subparsers(dest='command')
    
    backup = subparsers.add_parser('backup')
    backup.add_argument('--output', default='../../assets/test_dump.sql')
    
    restore = subparsers.add_parser('restore')
    restore.add_argument('file')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        for _ in range(15):
            print('Database Here')
    elif args.command == 'restore':
        pass


def main2():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-p', '--print',
            type=str,
            help='Test Console Printing'
    )
    
    args = parser.parse_args()
    
    if args.print:
        for _ in range(15):
            print('Database Here')


if __name__ == '__main__':
    main2()
