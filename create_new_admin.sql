-- Create a new admin user with a properly hashed password
USE `evoting_rmu`;

-- First, delete the existing admin (to avoid duplicate email)
DELETE FROM `admins` WHERE `email` = 'admin@rmu.edu.gh';

-- Insert a new admin with a bcrypt hash for 'admin123'
-- This hash was generated using bcrypt directly
INSERT INTO `admins` (`name`, `email`, `password_hash`) VALUES
('Admin User', 'admin@rmu.edu.gh', '$2b$12$8NpXMIBnXJdmjLnGT3xSLuHnMxRljGmMvJ5BoFTKqMFEHwUYsXcLG');
