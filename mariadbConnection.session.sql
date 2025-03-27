CREATE DATABASE kanisa;

USE kanisa;

CREATE TABLE admin (
    id VARCHAR(50) NOT NULL PRIMARY KEY,    
    name VARCHAR(50) NOT NULL,
    email VARCHAR(40) NOT NULL,
    phone_number VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE member (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zaq_number VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    jumuiya VARCHAR(150) NOT NULL,
    outstation VARCHAR(150) NOT NULL,
    center VARCHAR(150) NOT NULL,
    zone VARCHAR(150) NOT NULL
);

CREATE TABLE event (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    date_time DATETIME NOT NULL,
    venue VARCHAR(255) NOT NULL,
    concerned_parties TEXT
);