#Needs the following environment variables:
#	NAME - the application name in lowercase
#	ARCH - the architecture type, e.g 'amd64'
#	VERSION - the version
#	DOCKER_USER - the docker username
#	DOCKER_PASS - the docker password
#	DOCKER_REPO - the docker repository
VERSION=0.0.1
DOCKER_USER=chrisioa
NAME=multiarch_sensiot_faas
ARCH=arm32v7 arm64v8 amd64
QEMU_VERSION=v2.9.1
QEMU=arm

$(ARCH):
		@docker run --rm --privileged multiarch/qemu-user-static:register --reset
		@docker build --no-cache \
				--build-arg ARCH=$@ \
				--build-arg QEMU=aarch64 \
				--build-arg QEMU=$(strip $(call qemuarch,$@)) \
				--build-arg QEMU_VERSION=$(QEMU_VERSION) \
				--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
				--build-arg VERSION=${VERSION} \
				-t "${DOCKER_USER}/${NAME}:${VERSION}-$@" -f Dockerfile .
	
		
				
default: all
all: push


help:
	@echo 'Makefile targets to build and push Docker images'
	@echo
	@echo 'Usage:'
	@echo '	build			Builds the image for given ARCH'
	@echo '	push			Pushes the image to given DOCKER_REPO'
	@echo '	manifest		Creates manifest'
	@echo '	clean			Removes temporary folders'
	@echo
	

push: build
	#docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} ${DOCKER_REPO}
	docker push "${DOCKER_USER}/${NAME}:${VERSION}-${ARCH}"

build: 
	@$(foreach arch, $(ARCH), docker run --rm --privileged multiarch/qemu-user-static:register --reset \
		docker build --no-cache \
				--build-arg ARCH=$@ \
				--build-arg QEMU=aarch64 \
				--build-arg QEMU=$(strip $(call qemuarch,$@)) \
				--build-arg QEMU_VERSION=$(QEMU_VERSION) \
				--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%M:%SZ"` \
				--build-arg VERSION=${VERSION} \
				-t "${DOCKER_USER}/${NAME}:${VERSION}-$@" -f Dockerfile .)
	
	
manifest:
	@wget -O dockermanifest https://6582-88013053-gh.circle-artifacts.com/1/work/build/docker-linux-amd64
	@chmod +x dockermanifest
	@./dockermanifest manifest create ${DOCKER_USER}/${NAME}:$(VERSION) \
			$(foreach arch,$(ARCH), ${DOCKER_USER}/${NAME}:$(VERSION)-$(arch)) --amend
	@$(foreach arch,$(ARCH), ./dockermanifest manifest annotate \
			${DOCKER_USER}/${NAME}:$(VERSION) ${DOCKER_USER}/${NAME}:$(VERSION)-$(arch) \
			--os linux $(strip $(call convert_variants,$(arch)));)
	@./dockermanifest manifest push ${DOCKER_USER}/${NAME}:$(VERSION)
	@rm -f dockermanifest

# manifest:
# 	#docker login -u ${DOCKER_USER} -p ${DOCKER_PASS} ${DOCKER_REPO}
# 	wget https://github.com/estesp/manifest-tool/releases/download/v0.7.0/manifest-tool-linux-amd64
# 	chmod +x manifest-tool-linux-amd64
# 	./manifest-tool-linux-amd64 push from-spec manifests/${VERSION}-multiarch.yml

clean:
	rm -rf qemu-arm-static

# Convert qemu archs to naming scheme of https://github.com/multiarch/qemu-user-static/releases
define qemuarch
	$(shell echo $(1) | sed -e "s|arm32.*|arm|g" -e "s|arm64.*|aarch64|g" -e "s|amd64|x86_64|g")
endef
# Convert Docker manifest entries according to https://docs.docker.com/registry/spec/manifest-v2-2/#manifest-list-field-descriptions
define convert_variants
	$(shell echo $(1) | sed -e "s|amd64|--arch amd64|g" -e "s|i386|--arch 386|g" -e "s|arm32v5|--arch arm --variant v5|g" -e "s|arm32v6|--arch arm --variant v6|g" -e "s|arm32v7|--arch arm --variant v7|g" -e "s|arm64v8|--arch arm64 --variant v8|g" -e "s|ppc64le|--arch ppc64le|g" -e "s|s390x|--arch s390x|g")
endef

