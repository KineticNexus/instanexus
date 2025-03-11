# InstaNexus

An AI-powered Instagram bot that generates and posts historical content using Midjourney and OpenAI, with intelligent image analysis and selection.

## Features

- Automated content generation using AI
- Intelligent image analysis and selection
- Web interface for managing content
- Scheduled posting
- Analytics tracking
- Browser tools integration

## Components

1. Content Generation
   - OpenAI for text generation
   - Midjourney for image generation
   - Image analysis for selecting the best images

2. Instagram Bot
   - Automated posting
   - Session management
   - Error handling

3. Web Interface
   - Content management
   - Scheduling
   - Analytics dashboard

4. Browser Tools
   - Console logging
   - Network request tracking
   - Performance monitoring

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```
   OPENAI_API_KEY=your_openai_key
   MIDJOURNEY_API_KEY=your_midjourney_key
   INSTAGRAM_USERNAME=your_username
   INSTAGRAM_PASSWORD=your_password
   ```
4. Start the web interface:
   ```bash
   python src/web_interface/app.py
   ```
5. Start the browser tools server:
   ```bash
   ./start-browser-tools.bat
   ```

## Usage

1. Access the web interface at `http://localhost:5000`
2. Log in with your Instagram credentials
3. Generate content or schedule posts
4. Monitor analytics and performance

## Browser Tools Integration

The browser tools provide real-time monitoring and debugging capabilities:

- Console logging for debugging
- Network request tracking
- Performance monitoring
- Chrome extension integration

To test the browser tools:
1. Start the browser tools server
2. Install the Browser Tools Chrome Extension
3. Visit `/browser-tools-test` in the web interface

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
