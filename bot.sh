cd $(dirname "$0")

source env/bin/activate

python3 bot.py barman &
barman_pid=$!

python3 bot.py menestrel &
menestrel_pid=$!

python3 bot.py archiveuse &
archiveuse_pid=$!

cd ..

wait $barman_pid
wait $menestrel_pid
wait $archiveuse_pid
