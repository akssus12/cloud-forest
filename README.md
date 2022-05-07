## pip3 packages
Before pip3 install requirements.txt, try to below command for solving cv2 with noGUI environments(linux server)
apt-get update
apt-get install -y libsm6 libxext6 libxrender-dev
pip install opencv-python

## Manage common configuration in config.json
- MySQL configurations
- Mongo configurations
- Flask configurations
- OpenCV configurations

## Production mode
application.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

## Debugging mode(For testing)
application.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

## Do not use print() in server.py
When you try to check the value or results, you have to use logger
  - ex. logger.info(messages)
  - ex. logger.error(messages)

## DB Schema and command
CREATE DATABASE raonzena;
USE raonzena;

CREATE TABLE joininfo( 
	id INT PRIMARY KEY AUTO_INCREMENT, 
	joinid VARCHAR(100) NOT NULL, 
	joinem VARCHAR(100) NOT NULL, 
	joinpw VARCHAR(100) NOT NULL,
	stream VARCHAR(200) NULL,
) ENGINE=INNODB;

## Background Flask Webserver Running Command
nohup python3 -u server.py &
