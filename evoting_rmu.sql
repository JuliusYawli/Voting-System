-- Create the database
CREATE DATABASE IF NOT EXISTS `evoting_rmu`;
USE `evoting_rmu`;

-- Create students table
CREATE TABLE IF NOT EXISTS `students` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `student_id` VARCHAR(20) NOT NULL UNIQUE,
  `has_voted` BOOLEAN DEFAULT FALSE
);

-- Create admins table
CREATE TABLE IF NOT EXISTS `admins` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
);

-- Create elections table
CREATE TABLE IF NOT EXISTS `elections` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `start_time` DATETIME NOT NULL,
  `end_time` DATETIME NOT NULL,
  `status` ENUM('upcoming', 'ongoing', 'completed') DEFAULT 'upcoming'
);

-- Create candidates table
CREATE TABLE IF NOT EXISTS `candidates` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `election_id` INT NOT NULL,
  `votes` INT DEFAULT 0,
  FOREIGN KEY (`election_id`) REFERENCES `elections`(`id`) ON DELETE CASCADE
);

-- Create votes table
CREATE TABLE IF NOT EXISTS `votes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `student_id` INT NOT NULL,
  `candidate_id` INT NOT NULL,
  `election_id` INT NOT NULL,
  `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`candidate_id`) REFERENCES `candidates`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`election_id`) REFERENCES `elections`(`id`) ON DELETE CASCADE,
);

-- Insert demo data: 20 fake RMU students
INSERT INTO `students` (`name`, `email`, `student_id`, `has_voted`) VALUES
('John Mensah', 'john.mensah@rmu.edu.gh', 'RMU10001', FALSE),
('Abena Owusu', 'abena.owusu@rmu.edu.gh', 'RMU10002', FALSE),
('Kwame Asante', 'kwame.asante@rmu.edu.gh', 'RMU10003', FALSE),
('Akosua Agyemang', 'akosua.agyemang@rmu.edu.gh', 'RMU10004', FALSE),
('Kofi Boateng', 'kofi.boateng@rmu.edu.gh', 'RMU10005', FALSE),
('Ama Darko', 'ama.darko@rmu.edu.gh', 'RMU10006', FALSE),
('Evans Anguah', 'evans.anguah@rmu.edu.gh', 'RMU10007', FALSE),
('Adwoa Manu', 'adwoa.manu@rmu.edu.gh', 'RMU10008', FALSE),
('Kwesi Appiah', 'kwesi.appiah@rmu.edu.gh', 'RMU10009', FALSE),
('Efua Kumi', 'efua.kumi@rmu.edu.gh', 'RMU10010', FALSE),
('Emmanuel Tetteh', 'emmanuel.tetteh@rmu.edu.gh', 'RMU10011', FALSE),
('Grace Amoah', 'grace.amoah@rmu.edu.gh', 'RMU10012', FALSE),
('Daniel Adjei', 'daniel.adjei@rmu.edu.gh', 'RMU10013', FALSE),
('Sophia Mensah', 'sophia.mensah@rmu.edu.gh', 'RMU10014', FALSE),
('Michael Addo', 'michael.addo@rmu.edu.gh', 'RMU10015', FALSE),
('Priscilla Owusu', 'priscilla.owusu@rmu.edu.gh', 'RMU10016', FALSE),
('Samuel Boateng', 'samuel.boateng@rmu.edu.gh', 'RMU10017', FALSE),
('Victoria Asare', 'victoria.asare@rmu.edu.gh', 'RMU10018', FALSE),
('Joseph Ansah', 'joseph.ansah@rmu.edu.gh', 'RMU10019', FALSE),
('Elizabeth Agyei', 'elizabeth.agyei@rmu.edu.gh', 'RMU10020', FALSE);
('Abdul-Majeed Abdul-Aziz','abdul.aziz@st.rmu.edu.gh','RMU10021',FALSE);

-- Insert 1 admin with hashed password (admin123)
-- Using bcrypt hash for 'admin123'
INSERT INTO `admins` (`name`, `email`, `password_hash`) VALUES
('Admin User', 'admin@rmu.edu.gh', '$2b$12$1oE4z/zu8Z0JF0v1yZGX8.Rd.qja2rJJ1bCvQJFzSEMGUXcas7Y5y');
