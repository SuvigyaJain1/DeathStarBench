#!/bin/bash

if [ $# -ne 1 ];
then
    echo "Expected Usage: $0 <Node's public IP Address> "
else
    if [ $USER = "root" ];
    then
        echo "Root user detected. Create an account for a non-root user with sudo privileges and login using the new user"
        echo "sudo useradd <username>"
        echo "usermode -aG sudo <username>"
        echo "sudo su - <username>"
    else

        NODE_IP=$1

        sudo apt-get update && apt-get upgrade -y
        sudo apt-get install docker.io
        sudo apt-get install -y apt-transport-https ca-certificates curl 
        sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
        echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
        sudo apt-get update
        sudo apt-get install -y kubelet kubeadm kubectl
#        sudo apt-mark hold kubelet kubeadm kubectl

        # Changing C-group driver
        su -c "touch /etc/docker/daemon.json"
        su -c "echo '{ 
        "exec-opts": ["native.cgroupdriver=systemd"]
        }'| sudo cat > /etc/docker/daemon.json"
        sudo systemctl daemon-reload
        sudo systemctl restart docker
        sudo systemctl restart kubelet

        sudo usermod -aG docker $USER

        sudo kubeadm init --apiserver-advertise-address $NODE_IP --pod-network-cidr 192.168.0.0/16

        mkdir -p $HOME/.kube
        sudo cp  /etc/kubernetes/admin.conf $HOME/.kube/config
        sudo chown $(id -u):$(id -g) $HOME/.kube/config

        kubectl create -f https://projectcalico.docs.tigera.io/manifests/tigera-operator.yaml
        kubectl create -f https://projectcalico.docs.tigera.io/manifests/custom-resources.yaml

        echo "Finished Installation"
        watch kubectl get pods

        echo "Tokens and hash for adding worker nodes : (Token is only valid for 24 hours)"
        echo "Token: $(kubeadm token list | grep -v TOKEN | cut -d' ' -f1)"
        echo "Hash: sha256:$(openssl x509 -in /etc/kubernetes/pki/ca.crt -noout -pubkey | openssl rsa -pubin -outform DER 2>/dev/null | sha256sum | cut -d' ' -f1)"
    fi
fi
