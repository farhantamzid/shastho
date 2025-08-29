-- Schema for regulatory dashboard metrics (MySQL)
CREATE DATABASE IF NOT EXISTS shastho_regulatory;
USE shastho_regulatory;

-- Overall stats shown at the top (single row)
CREATE TABLE IF NOT EXISTS regulatory_stats (
  id INT PRIMARY KEY AUTO_INCREMENT,
  total_cases INT NOT NULL,
  new_cases_today INT NOT NULL,
  active_outbreaks INT NOT NULL,
  regions_affected INT NOT NULL,
  hospitals_reporting INT NOT NULL,
  alerts INT NOT NULL
);

-- List of regions
CREATE TABLE IF NOT EXISTS regions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL UNIQUE
);

-- Diseases summary
CREATE TABLE IF NOT EXISTS diseases (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL UNIQUE,
  cases INT NOT NULL,
  trend ENUM('increasing','stable','decreasing') NOT NULL,
  risk_level ENUM('low','medium','high') NOT NULL
);

-- Recent outbreaks
CREATE TABLE IF NOT EXISTS outbreaks (
  id INT PRIMARY KEY AUTO_INCREMENT,
  disease VARCHAR(255) NOT NULL,
  region VARCHAR(255) NOT NULL,
  cases INT NOT NULL,
  status VARCHAR(50) NOT NULL,
  trend VARCHAR(50) NOT NULL,
  start_date DATE NOT NULL,
  severity ENUM('Low','Medium','High') NOT NULL
);

-- Region specific summary
CREATE TABLE IF NOT EXISTS region_summary (
  id INT PRIMARY KEY AUTO_INCREMENT,
  region VARCHAR(255) NOT NULL,
  total_cases INT NOT NULL,
  active_outbreaks INT NOT NULL,
  population_affected VARCHAR(20) NOT NULL,
  hospital_capacity VARCHAR(10) NOT NULL
);

-- Primary diseases per region (1..n labels)
CREATE TABLE IF NOT EXISTS region_primary_diseases (
  id INT PRIMARY KEY AUTO_INCREMENT,
  region VARCHAR(255) NOT NULL,
  disease VARCHAR(255) NOT NULL
);

-- Monthly trends for charts (7 months for a few diseases)
CREATE TABLE IF NOT EXISTS monthly_trends (
  id INT PRIMARY KEY AUTO_INCREMENT,
  disease VARCHAR(255) NOT NULL,
  month_index INT NOT NULL, -- 1..12
  cases INT NOT NULL
);


