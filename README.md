# Library Daemon

## What is it?
Library Daemon is a Python program designed to pull a list of items checked out from your [Calgary Public Library](http://calgarypubliclibrary.com) account, generate an HTML report, and automatically send an email notification about soon-to-be-due items. It's especially designed to work on your smart phone. More features are planned for future releases.

## Installation & Setup

### Requirements
+ A webserver running at least Python 2.4.3 and PHP
+ SSH access to your web server
+ a basic knowledge of *nix systems and `crontab`

### Step 1: Installation

Once you've cloned this repo you're ready to set it up! Library Daemon is designed to be run on a webserver. I suggest you place it somewhere only accesible to you, and not the entire internet, for obvious security reasons. 

You'll want to upload everything as-is.

### Step 2: Configuration

Once you've done that you'll need to open `settings.cfg` in the `settings` folder and fill in the missing information. Be sure your Library Card # and password are correct. The email section is important too, so far I've only tested the notification emails with gmail's SMTP, so you'll need a gmail account for that to work. The other settings should be obvious.

### Step 3: Symlink the `www` directory

Assuming you placed the program outside of a web-readable directory (as you should have) you'll have to make a symlink to the `www` folder so you can view the output in your browser. The command would look something like this:

	$ ln -s /mywebserver/local/home/library/www /mywebserver/local/home/mywebsite.com/library
	
If that doens't make any sense, [Google 'symlinks'](http://www.google.ca/search?&q=symlinks) and try again. 

### Step 4: Test Run

If you've configured everything correctly you should be able run the program, like so:

	$ python library.py scrape
	
Running that command should start the process and output the resulting HTML to the `www` folder. Now just navigate there with your web browser and voila! If you like you can see the log file for details:

	$ cat logs/library_log

### Step 5: Configure `crontab`

In order to keep the listing up to date, you'll need to configure a `crontab` file on your webserver to have it run at regular intervals. How often is up to you, but you probably won't need it to run more then every few days. The line in your `crontab` could look something like this:

	* * */3 * * python /path/to/library/library.py scrape

Save that and you're done! Everything should work magically. If not, you can [contact me here](http://hami.sh/contact/).

## Why?
To be honest, I have a terrible time remembering to return books to the library. I sometimes rack up enought late fees in a month or two to cover the cost of a new book. This program aims to solve that problem. In addition, I really don't like using the Calgary Public Library website. It's archaic and poorly designed.; there is no mobile version either, so checking my account on the go is frustrating at best. 

_Library Daemon_ does not match the functionality of the full website in any way, nor does it try to. It simply provides an interface for viewing your checkouts that is both sexy and smart-phone friendly.

## Help
If you have any questions or comments please feel free to [get in touch with me](http://hami.sh/contact/). Thanks for checking out Library Daemon!

## Change Log
9/1/2011 - v1
- Initial release
