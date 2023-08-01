source env/bin/activate

python3 barman.py &
barman_pid=$!

python3 menestrel.py &
menestrel_pid=$!

python3 archiveuse.py &
archiveuse_pid=$!

wait $barman_pid
wait $menestrel_pid
wait $archiveuse_pid
