 
make ARCH=arm32v7
make ARCH=arm64v8
make ARCH=amd64
 
make ARCH=arm32v7 push
make ARCH=arm64v8 push
make ARCH=amd64 push

make manifest
