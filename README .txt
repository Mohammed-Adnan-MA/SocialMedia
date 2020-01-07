Requirements:
	- Python3
	- Flask
	- PostgreSQL

## Installation:
	- If you didn't, install Python3:
		https://realpython.com/installing-python/
	- Install PostgreSQL and add
	PostgreSQL's bin directory to your path, if you haven't done so already. Run psql and type the command `create
	database SocialMediaDB;` .    You can exit psql by typing `\q`.

	Then, you can then build and run the app as follows:
	
	```console:
	 python create.py
	 pip3 install -r requirements.txt
	 flask run
	```
	
	And finally, browse to [127.0.0.1:5000/]