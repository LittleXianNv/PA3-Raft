# PA3-Raft
We use python version 3.7.4 for this code to implement fs533 as a flat file system

# To start servers, run the following code:
python serverStart.py

# To start a client and do corresponding implementations:

1. To add a local file to fs533 with the given fs533 name:

    python client.py put localfilename fs533filename

2. To fetch a fs533 file to the local machine:

    python client.py get fs533filename localfilename

3. To delete a file from fs533:

    python client.py remove fs533filename

4. To list all files in fs533:

    python client.py ls

5. To list all machines of the servers that contain a copy of the file:

    python client.py locate fs533filename
