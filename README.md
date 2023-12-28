To build and run our project, you will need python, pip, and PyMySQL library installed. 
If you already have these specifications then skip to the next steps “import dump file” in the next paragraph.

<< Language and Library Installation

The first step is to install python3. This can be done by visiting python.org. Note that to check which version of python you have installed, open the terminal or command line and type 
“python --version” or “python -V”.
Next you have to install pip. To do so you would type the following in the command line: “sudo apt install python3-pip”. Similarly, to check which version of pip you have installed, 
use the following command “pip --version”.
Now, you need to install the PyMySQL library. This can be done by either of the following in the command line: “pip install PyMySQL” or “pip install PyMySQL[rsa]”. Note that the latter includes the installation of cryptography which is needed if your MySQL was set up with sha256_password or caching_sha2_password. Then to check if you’ve correctly installed PyMySQL, use the command “pip list”. After running this command there should be a list on the screen. If the list has PyMySQL in it then you have successfully installed the library. Note that to check if you have successfully installed PyMySQL[rsa], the list should include both PyMySQL and cryptography.

<< Import Dump File

The next step is to import the given self-contained dump file, “Fanfiction_ForumDataDump.sql” . To do this open the dump file with your MySQL connection and then run/execute the whole script. Then to check if you have successfully created the database in your workbench, click the refresh button near Schema and find “fanfiction_forum”.

<< Run Application Code

The last step would be to run the application code. The application code can be run either using the command line or a python ide of your choice. If you are using the command line make sure you are in the directory where our python application file, “ZhuYLiuR_App_Code.py” , is. Note to navigate to the correct directory use the “cd” change directory command. Once you are in the correct directory, simply type “python ZhuYLiuR_App_Code.py” or “python3 ZhuYLiuR_App_Code.py” depending on which version of python you have. To start, make sure you have our sql file runned and get your username and password ready for your sql root account.
