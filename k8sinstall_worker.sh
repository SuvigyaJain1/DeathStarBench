#!/bin/bash

if [ $# -ne 3 ];
then
    echo "Expected Usage: ./k8sinstall_worker.sh <Master node address> <Token> <Hash>"
else
    MASTER_IP=$1
    TOKEN=$2
    HASH=$3

    sudo apt-get update && apt-get upgrade -y
    sudo apt-get install docker.io
    sudo apt-get install -y apt-transport-https ca-certificates curl
    sudo apt-get install sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
    echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt-get update
    sudo apt-get install -y kubelet kubeadm kubectl
    sudo apt-mark hold kubelet kubeadm kubectl

    touch /etc/docker/daemon.json
    echo '{ 
    "exec-opts": ["native.cgroupdriver=systemd"]
    }'| cat > /etc/docker/daemon.json
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    sudo systemctl restart kubelet

    kubeadm join $MASTER_IP --token $TOKEN --discovery-token-ca-cert-hash $HASH
fi