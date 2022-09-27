kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name} {.spec.containers[*].name}{"\n"} {end}' |while read -r pod containers; 
do
     array=($containers);

     for container in "${array[@]}";
     do
         kubectl exec -i ${pod} -c "$container" --stdin --tty apt-get install linux-tools-common && apt-get install linux-tools-generic && perf record -- sleep 60
     done
done