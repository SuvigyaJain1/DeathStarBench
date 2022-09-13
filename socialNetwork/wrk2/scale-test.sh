OUTPUT_DIR=outputsIstio
mkdir -p $OUTPUT_DIR
for n in 1
do
    kubectl scale --all --replicas=$n --namespace=default deployment
    sleep 60
    ./wrk -D fixed -t 8 -c 16 -d 60 -L -s ./scripts/social-network/compose-post.lua http://localhost:31111/wrk2-api/post/compose -R 600 > $OUTPUT_DIR/compose/{$n}_replicas.txt
    ./wrk -D fixed -t 8 -c 16 -d 60 -L -s ./scripts/social-network/read-user-timeline.lua http://localhost:31111/wrk2-api/user-timeline/read -R 1200 > $OUTPUT_DIR/read/{$n}_replicas.txt
    echo "Finished run with $n replicas"
    uptime
done