#!/bin/bash
if [ ! $1 ];then
	echo "$0 <dir> <file> [memory use]"
	exit 1
fi
if [ ! $2 ];then
	echo "$0 $1 <file>"
	exit 1
fi
mem="1G"
if [ $3 ];then
	mem=$3
fi
echo "$1 $2 memory $mem will use"
echo "continue? (Enter or Ctrl+C)"
read -n 1
mksquashfs /mnt $1 $2 \
	-not-reproducible \
	-xattrs \
	-wildcards \
	-noappend \
	-progress \
	-mem $mem \
	-comp zstd \
	-e \
	var/cache/pacman/pkg \
	var/lib/pacman/sync \
	var/log \
	boot/efi \
	boot/grub \
	boot/initramfs-linux"*".img \
	boot/vmlinuxz-linux 2> backup.log
