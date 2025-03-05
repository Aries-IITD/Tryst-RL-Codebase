To setup the server, do: 
```
git clone https://github.com/smogon/pokemon-showdown.git server
```

You also need to have Node.js installed [many online guides exist for this]. Remember to add it to PATH.

```
./pokemon-showdown [port_no] --no-security
```
(Linux)

or 

```
node pokemon-showdown [port_no] --no-security
```
(Windows)

It doesn't matter what value you pick for port_no; 8000 is fine as a default.
Your server is now hosted locally.

To enable the ladder for the server, replace server/config/formats.ts with the one provided.

Enter localhost:<port_no> in your browser to view the battles/actually participate in one!
Add yourself as an administrator to your local server by editing server/config/usergroups.csv (or create it).
Simply add a line that is your username (you can create an account by visiting the site in your browser) followed by a , and ~.
For example my username is TheAbry, so my usergroups.csv looks like:
```
TheAbry,~
```
Then when you log in as this username you will be able to see all battles taking place on your server.

For the bot client, in the `client` folder create a venv and install all dependencies from `requirements.txt`.
Put the port number for your server in the websocket link in `client/env.txt`.
You can run 
```
python3 driver.py -h
```
to check all the command line arguments. You can change mode to battle against one of your AIs, or to wait on ladder for battles.
We have given 5 options for AIs: random, ai1, ai2, ai3, ai4. Random is pre-implemented, while ai1-ai4 can be implemented in `ai.py`.

If you get an error in running the driver.py after a crash, restart the server.


Poke-Env library is open source and available at https://github.com/hsahovic/poke-env/
