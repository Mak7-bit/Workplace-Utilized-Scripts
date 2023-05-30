# Author: Maksim Dmitriev : GitHub: Mak7bit
# Date: 15/03/2024 - For Osmose Australia Pty Ltd
# script_to_download_reports.py - allows to access the CustomFleet website, log-in and download a selected report type for a vehicle
# Version: V.01 - updated to take in a list of triggers for Date/Time recording (Ingition Off instances)
#         




import requests
from bs4 import BeautifulSoup

# Define login credentials
username = 'sbrookes@logsys.com.au'
password = 'Osmose123'

# Define the login URL
login_url = 'https://customfleetv5.fleetlocate.com.au/signin?q=0'

# Define the report URL
report_url = 'https://customfleetv5.fleetlocate.com.au/report'

# Create a session object to persist the login session
session = requests.Session()

# Send a GET request to the login page to obtain the CSRF token
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

# Send a POST request to the login page with the credentials and CSRF token
data = {
    'username': username,
    'password': password,
    'csrf_token': csrf_token
}
response = session.post(login_url, data=data)

# Send a GET request to the report page to obtain the CSRF token
response = session.get(report_url)
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

# Send a POST request to the report page with the CSRF token to trigger the report download
data = {
    'csrf_token': csrf_token,
    'download_report': 'true'
}
response = session.post(report_url, data=data)

# Save the report file to disk
with open('report.pdf', 'wb') as f:
    f.write(response.content)\
    
 
