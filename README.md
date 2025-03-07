First, clone this repository. This will download both the server to run it locally as well as the client and implementation files.

```
git clone https://github.com/Aries-IITD/Tryst-RL-Codebase.git server
```

You also need to have Node.js installed [many online guides exist for this]. Remember to add it to PATH.
Also, Python3 (preferably the latest version) is required.

```
./pokemon-showdown 7850 --no-security
```
(Linux)

or 

```
node pokemon-showdown 7850 --no-security
```
(Windows)

You can also choose the change the 7850 to another port number if you need to, but you will need to change client/env.txt if you do.
Your server is now hosted locally and running. To stop it hit Ctrl-C in the terminal and just type the command in again to run it again.

Enter `localhost:7850` in your browser to view the battles/actually participate in one! (or localhost:<port_no> if you changed it)
Add yourself as an administrator to your local server by editing `server/config/usergroups.csv`.
Simply add a line that is your username (you can create an account by visiting the site in your browser) followed by a , and ~.
For example my username is `TheAbry`, so my `usergroups.csv` looks like:
```
TheAbry,~
```
Then when you log in as this username you will be able to see all battles taking place on your server.

For the bot client, in the `client` folder create a venv and install all dependencies from `requirements.txt`.
```
pip install -r requirements.txt
```
Put the port number for your server in the link in `client/env.txt`. Change the second line to your assigned code.
You can run 
```
python3 driver.py -h
```
to check all the command line arguments. You can change the mode to battle against one of your AIs, or to wait on the ladder for battles.
We have given 5 options for AIs: random, ai1, ai2, ai3, ai4. Random is pre-implemented, while ai1-ai4 can be implemented in `ai.py`.

If you get an error for no module `poke_env`, try pip installing it separately using `pip install poke_env` or upgrading your pip then repeating the pip install steps again.
If you get an error in running the driver.py after a crash, restart the server.


Poke-Env library is open source and available at https://github.com/hsahovic/poke-env/
