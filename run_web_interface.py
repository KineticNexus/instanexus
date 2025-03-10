#!/usr/bin/env python3
"""
InstaNexus Web Interface Entry Point
"""

import os
from dotenv import load_dotenv
from src.web_interface.app import create_app

def main():
    # Load environment variables
    load_dotenv()
    
    # Get port from environment or use default
    port = int(os.getenv('WEB_INTERFACE_PORT', 5000))
    
    # Create and run the application
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'False').lower() == 'true')

if __name__ == '__main__':
    main()