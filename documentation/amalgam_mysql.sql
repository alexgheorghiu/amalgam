DROP DATABASE IF EXISTS amalgam;
CREATE DATABASE  amalgam CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE USER 'amalgam'@'localhost' IDENTIFIED BY 'amalgam';
GRANT ALL ON amalgam.* TO 'amalgam'@'localhost';

USE  amalgam;
