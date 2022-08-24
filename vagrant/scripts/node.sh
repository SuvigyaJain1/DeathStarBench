sudo apt-get update && apt-get upgrade -y
sudo apt-get install docker.io -y
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

sudo touch /etc/docker/daemon.json
echo '{ 
"exec-opts": ["native.cgroupdriver=systemd"]
}'| sudo tee /etc/docker/daemon.json

sudo swapoff -a
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl restart kubelet
