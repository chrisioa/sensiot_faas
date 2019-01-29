HYPRIOTOS=./hypriotos-rpi64-v20180429-184538.img.zip
DEVICE=/dev/sdc

HOSTNAME:=howard
USER:=ktr
GECOS:=KTR
HOME:=/home/ktr
TIMESERVER:=0.de.pool.ntp.org
IMAGE:=chrisioa/multiarch_sensiot
NSQ_IMAGE:=unibaktr/nsq
SWARM_TOKEN:=SWMTKN-1-1i70vsdqdl7etgmad7vjstezz2qtyxxfpq9v8lk6vga64hwl5o-c2lwru0h5i0pm18cgk0u25ovh
SWARM_LEADER_IP:=192.168.1.215
DEVICE_ID:=${HOSTNAME}
BUILDING:=ERBA
ROOM:=WE5/05.035
ARCHITECTURE:=arm64v8

help:
	@echo 'Makefile targets to flash SD card for sensor devices'
	@echo 'Usage:'
	@echo '		make flash-sd		Flash SD card'
	@echo

flash-sd:
	-sed -e "s|{USER}|${USER}|g" cloud-init.template.yml > cloud-init.yml
	-sed -i -e "s|{GECOS}|${GECOS}|g" cloud-init.yml
	-sed -i -e "s|{HOME}|${HOME}|g" cloud-init.yml
	-sed -i -e "s|{HOSTNAME}|${HOSTNAME}|g" cloud-init.yml
	-sed -i -e "s|{TIMESERVER}|${TIMESERVER}|g" cloud-init.yml
	-sed -i -e "s|{IMAGE}|${IMAGE}|g" cloud-init.yml
	-sed -i -e "s|{NSQ_IMAGE}|${NSQ_IMAGE}|g" cloud-init.yml
	-sed -i -e "s|{SWARM_TOKEN}|${SWARM_TOKEN}|g" cloud-init.yml
	-sed -i -e "s|{SWARM_LEADER_IP}|${SWARM_LEADER_IP}|g" cloud-init.yml
	-sed -i -e "s|{DEVICE_ID}|${DEVICE_ID}|g" cloud-init.yml
	-sed -i -e "s|{BUILDING}|${BUILDING}|g" cloud-init.yml
	-sed -i -e "s|{ROOM}|${ROOM}|g" cloud-init.yml
	-sed -i -e "s|{ARCHITECTURE}|${ARCHITECTURE}|g" cloud-init.yml
	-cat cloud-init.yml
	#-curl -sLo ./flash https://raw.githubusercontent.com/hypriot/flash/master/Linux/flash
	#-chmod +x ./flash
	-sudo rm /tmp/hypriotos-rpi64-v20180429-184538.img
	-flash -u cloud-init.yml -d ${DEVICE} ${HYPRIOTOS}
	#-./flash -u cloud-init.yml -d ${DEVICE} https://github.com/DieterReuter/image-builder-rpi64/releases/download/v20180429-184538/hypriotos-rpi64-v20180429-184538.img.zip
	-rm -f ./cloud-init.yml
