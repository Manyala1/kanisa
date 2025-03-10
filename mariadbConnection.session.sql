CREATE DATABASE kanisa;

USE kanisa;

 TABLE admin (
    id VARCHAR(50) NOT NULL PRIMARY KEY,    
    name VARCHAR(50) NOT NULL,              -
    email VARCHAR(40) NOT NULL,
    phone_number VARCHAR(10) NOT NULL UNICREATEQUE 
);

CREATE TABLE member (
    zaq_number VARCHAR(50) PRIMARY KEY,
    outstation VARCHAR(100) NOT NULL,
    full_names VARCHAR(255) NOT NULL,
    phone_number VARCHAR(10)  NOT NULL
);

CREATE TABLE event (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    date_time DATETIME NOT NULL,
    venue VARCHAR(255) NOT NULL,
    concerned_parties TEXT
);
