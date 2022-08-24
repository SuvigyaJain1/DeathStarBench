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
        # sudo apt-get install docker.io
        sudo apt-get install -y apt-transport-https ca-certificates curl 
        sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
        echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
        sudo apt-get update
        sudo apt-get install -y kubelet kubeadm kubectl
        sudo apt-mark hold kubelet kubeadm kubectl

        sudo apt-get remove docker docker-engine docker.io containerd runc
        sudo apt-get install gnupg lsb-release
        curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

        sudo apt-get update
        sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin  
        cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay 
br_netfilter
EOF

        sudo modprobe overlay
        sudo modprobe br_netfilter

        # Setup required sysctl params, these persist across reboots.
        cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

        # Apply sysctl params without reboot
        sudo sysctl --system
        sudo mkdir -p /etc/containerd
        containerd config default | sudo tee /etc/containerd/config.toml
        sudo systemctl restart containerd

        # To use the systemd cgroup driver in /etc/containerd/config.toml with runc, set
        # [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
        # ...
        # [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
        #     SystemdCgroup = true

        sudo kubeadm init --config kubeadm-config.yaml | sudo tee ~/join.txt
        
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
