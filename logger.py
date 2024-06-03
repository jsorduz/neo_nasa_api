import logging

# Create the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler("nasa.log", mode="w")
file_handler.setLevel(logging.DEBUG)

# Create a stream handler for the command line
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# Define the log message format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Set the format for both handlers
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
