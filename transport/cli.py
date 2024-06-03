from transport.transport import get
import sys

def cliget():
    token = sys.argv[1]
    get(token)
    
if __name__ == '__main__':
    cliget()