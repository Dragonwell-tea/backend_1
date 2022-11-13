#UMD market_backend  
##Run: flask run --port 5000 or click run button in pycharm or ur compile  
##Requirment(pycharm open the project, according to the compiler prompts will automatically add, some plug-ins may need to be manually configured)  
##Myversion  
Flask~=2.0.3  
Flask-Cors~=3.0.10  
Flask-SQLAlchemy~=2.5.1  
psycopg2-binary~=2.9.3  
schema~=0.7.5  
PyJWT~=2.3.0  
bcrypt~=3.2.2  
cryptography~=37.0.2  
##Database mysql, need to change to their own mysql account name and password. In config.py: SQLALCHEMY_DATABASE_URI = "mysql://root:root@localhost/marketplace"  
first root: ur mysql id  second root: ur password  
##(EXTRA: terminal run: pip install mysqlclient)  


