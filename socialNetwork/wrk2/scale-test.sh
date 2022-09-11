OUTPUT_DIR=outputs
mkdir -p $OUTPUT_DIR
for n in 1 2 3 4 5
do
    kubectl scale --all --replicas=$n --namespace=default deployment
    sleep 300
    ./wrk -D fixed -t 8 -c 16 -d 60 -L -s ./scripts/social-network/compose-post.lua http://localhost:8080/wrk2-api/post/compose -R 1000 > $OUTPUT_DIR/($n)_replicas.txt
    echo "Finished run with $n replicas"
    uptime
done