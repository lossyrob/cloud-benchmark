#!/bin/bash

scp -oStrictHostKeyChecking=no -i ~/trellis.pem ~/tmp/gtcb/demo.jar ubuntu@$@:/home/ubuntu
scp -i ~/trellis.pem ~/tmp/gtcb/setup.sh ubuntu@$@:/home/ubuntu
ssh -i ~/trellis.pem ubuntu@$@ chmod a+x ./setup.sh
ssh -i ~/trellis.pem ubuntu@$@ ./setup.sh
