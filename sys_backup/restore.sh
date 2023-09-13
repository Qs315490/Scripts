#!/bin/bash
if [ ! $1 ];then
	echo "$0 <file or device> <dir>"
	exit 1
fi
if [ ! $2 ];then
	echo "$0 $1 <dir>"
	exit 1
fi
unsquashfs -f $1 -d $2
