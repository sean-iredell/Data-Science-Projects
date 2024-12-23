College Basketball Team Data Analysis This project analyzes college basketball team performance by leveraging data from two sources:

NCAA Stats: Game-by-game team data obtained via Selenium web scraping. NCAA API: Rankings, points, and records for college basketball. The analysis compares teams participating in multi-team events (MTEs) to those that do not, examining performance before, during, and after MTEs. Key metrics include points scored and offensive efficiency, with predictions generated using a machine learning model.

Data Collection:

Web scraping of detailed game data using Selenium.
API integration for rankings and records.
Analysis:

Machine learning predictions for points scored.
Offensive efficiency comparisons between MTE and non-MTE teams.
Visualization:

Graphical representations of offensive efficiency across time.
Setup:

Selenium Web Scraper Install Chrome Browser: Version 131.0.6778.140 (Official Build) (arm64) or newer. Download ChromeDriver: Version 131.0.6778.139 or compatible. Use python src/get_data.py

NCAA API Access (https://github.com/henrygd/ncaa-api):

Ensure Docker is installed on your machine.
Start the NCAA API container using Docker: docker run --rm -p 3000:3000 henrygd/ncaa-api
The API will be accessible at: http://localhost:3000
To fetch rankings for Division 1 Men's Basketball, use: curl http://localhost:3000/rankings/basketball-men/d1
Save the JSON results for further processing.
Prepare the raw data for analysis by running: python src/clean_data.py

Perform analysis and create visualizations: python src/analyze_and_visualize.py
Generated visuals will be saved in the results/images folder.

The analysis evaluates offensive efficiency and scoring performance for: Teams participating in MTEs versus non-MTE teams. Performance before, during, and after MTEs. Use the results to understand how MTE participation impacts team performance.
