# Data Analyst Agent

A powerful API service that uses AI and data processing libraries to source, prepare, analyze, and visualize data. Built with Flask and designed to handle various data analysis tasks including web scraping, statistical analysis, and data visualization.

## Features

- **Web Scraping**: Automatically scrapes data from websites like Wikipedia
- **Statistical Analysis**: Performs correlation analysis, regression analysis, and more
- **Data Visualization**: Generates charts, plots, and graphs as base64-encoded images
- **Multi-format Support**: Handles both JSON and plain text question formats
- **Database Integration**: Supports DuckDB for large-scale data analysis
- **RESTful API**: Easy-to-use HTTP endpoints

## Quick Start (Windows)

### Prerequisites

- Python 3.8 or higher
- Windows operating system
- Internet connection

### Installation

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/shreyasaxena21/Data-Analyst-Agent
   cd data-analyst-agent
   ```

2. **Run the setup script**
   ```bash
   setup.bat
   ```
   This will:
   - Create a virtual environment
   - Install all required dependencies
   - Set up the application

3. **Set your OpenAI API Key (Optional)**
   ```bash
   set OPENAI_API_KEY=your_api_key_here
   ```

4. **Start the application**
   ```bash
   run.bat
   ```

The application will be available at `http://localhost:5000`

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv data_analyst_env

# Activate virtual environment
data_analyst_env\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## API Usage

### Health Check

```bash
curl http://localhost:5000/
```

### Data Analysis

Submit analysis tasks via POST request to `/api/`:

```bash
curl "http://localhost:5000/api/" -F "questions.txt=@questions.txt"
```

With additional files:
```bash
curl "http://localhost:5000/api/" -F "questions.txt=@questions.txt" -F "data.csv=@data.csv"
```

## Supported Question Types

### 1. Movie Analysis (Wikipedia Scraping)

Example questions.txt:
```
Scrape the list of highest grossing films from Wikipedia. It is at the URL:
https://en.wikipedia.org/wiki/List_of_highest-grossing_films

Answer the following questions and respond with a JSON array of strings containing the answer.

1. How many $2 bn movies were released before 2000?
2. Which is the earliest film that grossed over $1.5 bn?
3. What's the correlation between the Rank and Peak?
4. Draw a scatterplot of Rank and Peak along with a dotted red regression line through it.
```

Expected response format: `[1, "Titanic", 0.485782, "data:image/png;base64,iVBORw0KG..."]`

### 2. Court Data Analysis (DuckDB)

Example questions.txt (JSON format):
```json
{
  "Which high court disposed the most cases from 2019 - 2022?": "...",
  "What's the regression slope of the date_of_registration - decision_date by year in the court=33_10?": "...",
  "Plot the year and # of days of delay from the above question as a scatterplot with a regression line. Encode as a base64 data URI under 100,000 characters": "data:image/webp:base64,..."
}
```

## Testing

Run the test suite to verify functionality:

```bash
# Activate virtual environment first
data_analyst_env\Scripts\activate.bat

# Run tests
python test_api.py
```

## Deployment

### Using Docker

1. Build the image:
   ```bash
   docker build -t data-analyst-agent .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 -e OPENAI_API_KEY=your_key data-analyst-agent
   ```

### Using Cloud Platforms

The application is ready for deployment on:
- **Heroku**: Use the included `Dockerfile` or create a `Procfile`
- **Railway**: Connect your GitHub repo and deploy automatically
- **Google Cloud Run**: Deploy using the Docker container
- **AWS Lambda**: Can be adapted with Zappa or similar frameworks
- **Azure Container Instances**: Deploy using the Docker image

### Using ngrok (for local testing)

For temporary public access during development:

1. Install ngrok from https://ngrok.com
2. Start your local server: `python app.py`
3. In another terminal: `ngrok http 5000`
4. Use the provided ngrok URL for testing

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (optional, for advanced AI features)
- `PORT`: Port number (default: 5000)
- `FLASK_ENV`: Environment mode (development/production)

## Dependencies

- **Flask**: Web framework
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib**: Plotting and visualization
- **seaborn**: Statistical data visualization
- **requests**: HTTP library
- **beautifulsoup4**: Web scraping
- **scipy**: Scientific computing
- **duckdb**: In-process analytical database
- **openai**: OpenAI API client

## Project Structure

```
data-analyst-agent/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── setup.bat          # Windows setup script
├── run.bat            # Windows run script
├── test_api.py        # API test suite
├── Dockerfile         # Docker configuration
├── README.md          # This file
└── LICENSE           # MIT License
```

## API Response Formats

### Movie Analysis Response
```json
[1, "Titanic", 0.485782, "data:image/png;base64,iVBORw0KG..."]
```

### Court Data Response
```json
{
  "Which high court disposed the most cases from 2019 - 2022?": "Madras High Court",
  "What's the regression slope of...": 1.234567,
  "Plot the year and # of days...": "data:image/png;base64,..."
}
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (missing required files)
- `500`: Internal Server Error

Error response format:
```json
{
  "error": "Description of the error"
}
```

## Performance Considerations

- **Timeout**: API requests have a 3-minute timeout limit
- **Memory**: Large datasets are processed in chunks when possible
- **Caching**: Consider implementing caching for frequently requested data
- **Rate Limiting**: Implement rate limiting for production use

## Limitations

- Web scraping may be affected by website structure changes
- Large datasets may require additional memory optimization
- Some advanced features require OpenAI API key
- DuckDB queries depend on external data availability

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the test suite: `python test_api.py`
2. Review the logs for error messages
3. Ensure all dependencies are installed correctly
4. Verify your Python version (3.8+ required)

## Troubleshooting

### Common Issues

**"Python is not installed or not in PATH"**
- Install Python from https://python.org
- Make sure to check "Add Python to PATH" during installation

**"Module not found" errors**
- Run `pip install -r requirements.txt` in your virtual environment
- Ensure the virtual environment is activated

**API request timeouts**
- Large datasets may take time to process
- Increase timeout values if needed
- Check internet connection for web scraping tasks

**Port already in use**
- Change the port in app.py: `app.run(host='0.0.0.0', port=5001)`
- Or kill the process using the port

### Development Tips

- Use the test script to verify functionality after changes
- Enable Flask debug mode for development: `app.run(debug=True)`
- Monitor logs for detailed error information
- Test with sample data before using real datasets

