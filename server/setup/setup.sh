#!/bin/bash

sudo mkdir /mnt/block
sudo mount /dev/xvdf /mnt/block
java -Xmx2G -jar demo.jar &