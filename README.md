<div id="header" align="center">

![logo](https://github.com/user-attachments/assets/4357fe9b-a0d1-4821-8159-2aed8a91b085)


</div>

# BASIC

A simple application for visual representation of your network speed data.

![image](https://user-images.githubusercontent.com/79650307/228206989-09ae9056-8862-4dae-9315-92f843669a54.png)

# FUNCTONS

1. Representation of the `download speed` in the form of a dynamic graph
2. Representation of `upload speed` on a dynamic graph
3. Pretty-print log for terminal


# NOTE
1. Default variables can be changed!

```env
UPDATE_DELAY = 0.1
FOLDER = 'history'
TIMEZONE = 'Europe/Moscow'
TERMINAL_OUTPUT = True
ROW_LIMIT = 30
```

2. You can change plot speed (in second)
   
```env
UPDATE_DELAY = <time>
```
 
![speed_differency](https://user-images.githubusercontent.com/79650307/227700391-92cf1442-1802-4b5c-88db-dee86dbadb65.gif)



# HOW TO USE

1. Clone repo:
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
