UMD market_backend
====
First  
-
Need to configure the `flask` environment. https://flask.palletsprojects.com/en/2.2.x/ <br>
---
Second  
-
`Before you run it`
Run these order in ur terminal
```Bash
pip install pymysql
pip install flask-sqlalchemy
pip install flask-migrate
```
`After that:`
```Bash
flask db init
flask db migrate
flask db upgrade
```
`At last:` Run: flask run --port 5000 or click run button in pycharm or ur compile.<br>
Requirment(pycharm open the project, according to the compiler prompts will automatically add, some plug-ins may need to be manually configured)<br>
`My version`<br>
Flask~=2.0.3  
Flask-Cors~=3.0.10  
Flask-SQLAlchemy~=2.5.1  
psycopg2-binary~=2.9.3  
schema~=0.7.5  
PyJWT~=2.3.0  
bcrypt~=3.2.2  
cryptography~=37.0.2 
---
Third  
-
DataBase(mysql)(You need to create a database locally called marketplace, The table is automatically created)<br>
Database mysql, need to change to their own mysql account name and password.<br>
In config.py: 
```Python
SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost/marketplace"
```
<br>
first root: ur mysql id  second root: ur password  
----



