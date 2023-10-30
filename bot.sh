source env/bin/activate

python3 bot.py &
barman_pid=$!

python3 bot.py &
menestrel_pid=$!

python3 bot.py &
archiveuse_pid=$!

wait $barman_pid
wait $menestrel_pid
wait $archiveuse_pid
