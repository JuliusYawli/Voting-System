# Voting-System
Overview
This project proposes the development of a secure, web-based voting system. The platform ensures that only verified users can vote, votes are accurately counted in real time, and no voter can cast more than one ballot. The system mimics real-world electoral processes and serves as a practical tool for learning secure web development practices.
 
Core Features
1. Voter Authentication
• Purpose: To verify each voter's identity before allowing them to vote.
• Implementation:
o One-Time Passwords (OTPs) sent via email or SMS.
o Secure token-based session management.
• Benefit: Prevents unauthorized access and enforces voter eligibility.
2. Vote Tally Dashboard
• Purpose: To display vote counts dynamically.
• Implementation:
o Real-time or near real-time updating dashboard with charts and statistics.
o Admin-restricted detailed analytics view.
• Benefit: Increases transparency and builds trust in the voting process.
3. Double Voting Prevention
• Purpose: To ensure each user votes only once.
• Implementation:
o Database flag to mark a user as "voted".
o Session and token validation to reject repeat submissions.
• Benefit: Maintains fairness and prevents vote inflation.
 
3. Technical Stack
• Frontend: HTML/CSS, JavaScript (React or Vue)
• Backend: Python (Flask)
• Database: MySQL
• Authentication: OTP-based or JWT (JSON Web Tokens)
• Security Measures:
o HTTPS encryption
o CSRF/XSS protection
o Input validation and sanitization
o Session timeout and secure cookie usage
