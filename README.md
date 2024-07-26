<div id="header" align="center">

![logo](https://github.com/user-attachments/assets/4357fe9b-a0d1-4821-8159-2aed8a91b085)

</div>

# BASIC

Track, storage and notify you about your server's internet traffic


# FUNCTONS

1. Monitoring `download speed` and `upload speed`
2. Notifying about peak of traffic usage
3. Storage traffic data in `sqlite3` in a local place


# NOTE
1. Default variables can be changed

```env
UPDATE_DELAY = 1  
#sleep time between reading

FOLDER = 'history'
# default folder for storage db files

TIMEZONE = 'Europe/Moscow'
# using timezone

TERMINAL_OUTPUT = False
# colored output of every reading item

ROW_LIMIT = 30
# max rows of terminal output 
```



# HOW TO USE

1. Clone repo to your server or your PC:
```bash
git clone  https://github.com/IvanIsak2000/network-speed.git
```
2. Install libs
``` bash
poetry shell && poetry install 
```

3. Launch file 
```bash
python3 main.py
```
