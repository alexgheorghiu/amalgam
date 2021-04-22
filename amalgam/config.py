"""This is the file is the entry point for app's enviroment settings"""
import logging, os

def setup_logging():
    """Setup the logging for whole application"""
    stream_handler = logging.StreamHandler() # STDOUT loggin
    file_handler = logging.FileHandler(filename=os.environ.get("AMALGAM_LOG_FILE", 'amalgam.log'))
    logging.basicConfig(level=os.environ.get("AMALGAM_LOG_LEVEL", "INFO"), 
    format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
    handlers=[stream_handler, file_handler])


SQLALCHEMY_DATABASE = os.environ.get("AMALGAM_SQLALCHEMY_DATABASE", 'mysql')
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://amalgam:amalgam@localhost/amalgam?charset=utf8mb4' # https://stackoverflow.com/questions/47419943/pymysql-warning-1366-incorrect-string-value-xf0-x9f-x98-x8d-t
SQLALCHEMY_ECHO = False
SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 10, 'max_overflow': 5}

