# GOAL #

Run Python code in a Docker container remotely as shown in the diagram.

                                            +----------------------+
                                            |        +-----------+ |
                                            |       /           /| |
                                            |      /           / | |
      +-------+                             |     /           /  | |
      |       |         .-,(   ),-.         |    /           /   | |
      |       |      .-(           )-.      |   +-----------+    + |
      +-------+ --> (    Internet     ) ----+-> |           |   /  |
     /......./       '-(           ).-'     |   | python    |  /   |
    +-------+            '-(   ).-'         |   | container | /    |
                                            |   |           |/     |
    Development                             |   +-----------+      |
      computer                              |                      |
                                            |     Docker Server    |
                                            +----------------------+

## 1.Tools ##

- Pycharm
- Docker

## 2.Docker Server ##

The docker server runs debian.

- Follow guides to install docker on debian and check everything is working.
- Create a certificate folder and generate certificates by following the steps shown here
https://docs.docker.com/engine/security/https/
- Check that the */lib/systemd/system/docker.service* file contains the line `EnvironmentFile=-/etc/default/docker`
    - You can check both file are used by running the following commands:

    
        systemctl show --property=FragmentPath docker
        grep EnvironmentFile /usr/lib/systemd/system/docker.service

(see https://docs.docker.com/engine/admin/systemd/ for more informations)
- Modify the */etc/default/docker* file and modify the line DOCKER_OPTS="-D --tlsverify --tlscacert={PATH_TO_CERTIFICATE}
/ca.pem --tlscert={PATH_TO_CERTIFICATE}/server-cert.pem --tlskey={PATH_TO_CERTIFICATE}/server-key.pem"`
- Follow the instructions here https://www.campalus.com/enable-remote-tcp-connections-to-docker-host-running-ubuntu-15-04/
and create a */etc/systemd/system/docker-tcp.socket* with the content


    [Unit]
    Description=Docker Socket for the API
    [Socket]
    ListenStream=2375
    BindIPv6Only=both
    Service=docker.service
    [Install]
    WantedBy=sockets.target

- And enable the socket


    systemctl enable docker-tcp.socket
    systemctl enable docker.socket
    systemctl stop docker
    systemctl start docker-tcp.socket
    systemctl start docker

## 3.Container ##

The python container has to contains, of course, all python packages required for your program to run and **pydevd** for
debugging.

## 4.Pycharm ##

- First make a directory to contains the authentication certificates and store *ca.pem*, *key.pem* and *cert.pem*
previously generated.
- Open pycharm and in `Preferences/Build, Execution, Deployment/Docker` create a Docker configuration. The API url is
**https://{SERVER IP}:2375**, and the Certificates folder is the one you set before.

(you can change the port in the *docker-tcp.socket* file of the server)
- In `Preferences/Build, Execution, Deployment/Deployment` create a new configuration of type SFTP. The host is the IP
of the server, port is 22 (SSH), the root path is the path on the server where the files will be uploaded, and add your
credentials.
    - In `Mapppings` the Local path is the root folder path of your python project, the Deployment path is your project
    remote folder name.
- Add a Remote Python Interpreter of type Docker. Select the previously created Docker server, the image you have created
with all packages, and set the python path.

## 5.Run ##

- Create a run configuration with the script set as `/opt/project/{YOUR_SCRIPT}`, the working directory is `/opt/project`
and add in the container settings `-v {REMOTE_PROJECT_PATH}:/opt/project`. This mount the server project folder into the
container

## 6.Debug ##

- Add a Python Remote Debug configuration where the Local host name is your development computer host name and chose a
port (e.g. 50621)
- In your script import pydevd and add the line displayed in the pycharm configuration window (`pydevd.settrace(...)`)
- Launch this configuration first then run your script with the run configuration in the step 5. You will be able to debug
your code running in the container.

A popup can be displayed asking your help for mapping remote script with local
