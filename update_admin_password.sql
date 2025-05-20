-- Update admin password to use bcrypt format
USE `evoting_rmu`;

-- Update the admin password hash to a bcrypt hash for 'admin123'
-- This is a valid bcrypt hash for 'admin123'
UPDATE `admins` 
SET `password_hash` = '$2b$12$8NpXMIBnXJdmjLnGT3xSLuHnMxRljGmMvJ5BoFTKqMFEHwUYsXcLG' 
WHERE `email` = 'admin@rmu.edu.gh';
