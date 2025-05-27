import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-development-only'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.environ.get('DB_USER')}:"
        f"{os.environ.get('DB_PASSWORD')}@"
        f"{os.environ.get('DB_HOST')}:"
        f"{os.environ.get('DB_PORT')}/"
        f"{os.environ.get('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES = int(os.environ.get('OTP_EXPIRY_MINUTES', 10))
    OTP_EXPIRY_SECONDS = OTP_EXPIRY_MINUTES * 60
    
    # Twilio Configuration (SMS Fallback)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # EmailJS Configuration (Primary)
    EMAILJS_SERVICE_ID = os.environ.get('EMAILJS_SERVICE_ID')
    EMAILJS_TEMPLATE_ID = os.environ.get('EMAILJS_TEMPLATE_ID')
    EMAILJS_USER_ID = os.environ.get('EMAILJS_USER_ID')
    
    # Delivery Strategy
    OTP_DELIVERY_STRATEGY = os.environ.get('OTP_DELIVERY_STRATEGY', 'email_first')  # Options: 'email_first', 'sms_only', 'email_only'
    
    @property
    def emailjs_configured(self):
        """Check if EmailJS is properly configured."""
        return all([
            self.EMAILJS_SERVICE_ID,
            self.EMAILJS_TEMPLATE_ID,
            self.EMAILJS_USER_ID
        ])
    
    @property
    def twilio_configured(self):
        """Check if Twilio is properly configured."""
        return all([
            self.TWILIO_ACCOUNT_SID,
            self.TWILIO_AUTH_TOKEN,
            self.TWILIO_PHONE_NUMBER
        ])
    
    def get_otp_delivery_method(self, student):
        """
        Determine the best OTP delivery method based on configuration and student info.
        Falls back to SMS if email fails or isn't configured.
        """
        if self.OTP_DELIVERY_STRATEGY == 'sms_only':
            return 'sms' if (self.twilio_configured and student.phone_number) else None
        
        if self.OTP_DELIVERY_STRATEGY == 'email_only':
            return 'email' if (self.emailjs_configured and student.email) else None
        
        # Default 'email_first' strategy
        if self.emailjs_configured and student.email:
            return 'email'
        if self.twilio_configured and student.phone_number:
            return 'sms'
        return None

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Override any development-specific settings here

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Override any production-specific settings here

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
