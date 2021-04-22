import logging, os

def setup_logging():
    """Setup the logging for whole application"""
    stream_handler = logging.StreamHandler() # STDOUT loggin
    file_handler = logging.FileHandler(filename=os.environ.get("AMALGAM_LOG_FILE", 'amalgam.log'))
    logging.basicConfig(level=os.environ.get("AMALGAM_LOG_LEVEL", "INFO"), 
    format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
    handlers=[stream_handler, file_handler])