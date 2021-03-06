-- Instructions to create a database and user under MySQL 8
DROP DATABASE IF EXISTS amalgam;
CREATE DATABASE  amalgam CHARACTER SET utf8 COLLATE utf8_general_ci;

DROP USER IF EXISTS 'amalgam'@'localhost';
CREATE USER 'amalgam'@'localhost' IDENTIFIED BY 'amalgam';
GRANT ALL ON amalgam.* TO 'amalgam'@'localhost';

-- Instructions to create a database and user under MySQL 5.6
DROP DATABASE IF EXISTS amalgam;
CREATE DATABASE  amalgam CHARACTER SET utf8 COLLATE utf8_general_ci;

GRANT ALL PRIVILEGES ON  amalgam.* TO  amalgam@localhost IDENTIFIED BY 'amalgam' WITH GRANT OPTION;