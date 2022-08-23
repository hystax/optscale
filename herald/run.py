import os
from herald_server import server
from herald_server.worker import worker
import subprocess


def main():
    subprocess.run("printf '%s\n%s\n' 'O QueueLA=100' 'O RefuseLA=100'"
                   " >> /etc/mail/sendmail.cf", shell=True, check=True)
    subprocess.run("service sendmail start", shell=True, check=True)
    service_name = os.environ['HERALD_SERVICE']
    if service_name == 'api':
        server.main()
    elif service_name == 'engine':
        worker.main()


if __name__ == '__main__':
    main()
