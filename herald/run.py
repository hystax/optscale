import os
import subprocess


from herald.herald_server import server
from herald.herald_server.worker import worker


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
