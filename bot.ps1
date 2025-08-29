# Change to the script's directory
Set-Location $PSScriptRoot

# Activate the virtual environment
& .\env\Scripts\Activate.ps1

# Start the bot processes and save their PIDs
$barman_process = Start-Process -NoNewWindow -FilePath "python3" -ArgumentList "bot.py barman" -PassThru
$barman_pid = $barman_process.Id

$menestrel_process = Start-Process -NoNewWindow -FilePath "python3" -ArgumentList "bot.py menestrel" -PassThru
$menestrel_pid = $menestrel_process.Id

$archiveuse_process = Start-Process -NoNewWindow -FilePath "python3" -ArgumentList "bot.py archiveuse" -PassThru
$archiveuse_pid = $archiveuse_process.Id 

$gambler_process = Start-Process -NoNewWindow -FilePath "python3" -ArgumentList "bot.py gambler" -PassThru
$gambler_pid = $gambler_process.Id 

# Wait for the processes to complete
Wait-Process -Id $barman_pid
Wait-Process -Id $menestrel_pid
Wait-Process -Id $archiveuse_pid
Wait-Process -Id $gambler_pid