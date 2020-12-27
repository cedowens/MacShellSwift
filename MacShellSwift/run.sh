echo Enter listening port for your MacC2 server:

read port

sed -e "s/443/$port/g" swiftshell-server.py

docker build -t macshellswift-docker .

docker volume create MacShellSwift

sudo docker run --rm --network="host" -v MacShellSwift:/mss -ti macshellswift-docker
