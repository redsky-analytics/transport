from transport import get
import sys

def cliget():
    token = sys.argv[1]
    cli(token)
    
if __name__ == '__main__':
    cliget()