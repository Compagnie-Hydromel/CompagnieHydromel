cd $(dirname "$0")

source env/bin/activate

case $1 in
    "format")
        python3 libs/format.py format
        ;;
    "check-format")
        python3 libs/format.py check
        ;;
    "test")
        python3 -m unittest tests/test_*.py
        ;;
    "migrate")
        python3 bot.py migrate
        ;;
    "rollback")
        depth=1
        if [ -n "$2" ]; then
            depth="$2"
        fi
        python3 bot.py rollback $depth
        ;;
    "interactive")
        python3 bot.py interactive
        exit
        ;;
esac
if [ -n "$1" ]; then
    exit $?
fi

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
