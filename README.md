To setup the server, do: 
```
git clone https://github.com/smogon/pokemon-showdown.git server
```

You also need Node.js.

```
./pokemon-showdown [port_no] --no-security
```
(Linux)

or 

```
node pokemon-showdown [port_no] --no-security
```
(Windows)

Your server is now hosted locally.


For the bot client, in the `client` folder create a venv and install all dependencies from `requirements.txt`.

Put the port number in the websocket link in `client/env.txt`.


Poke-Env library is open source and available at https://github.com/hsahovic/poke-env/
