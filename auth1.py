import pdfkit
import requests

def save_webpage_as_pdf(url, local_filename):
    # Send a GET request to the URL
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Use pdfkit to convert HTML content to PDF
        pdfkit.from_string(response.text, local_filename)
        print("Webpage saved as PDF successfully.")
    else:
        print("Failed to save the webpage as PDF.")

# Example usage
url = 'http://localhost:3000/calendar_events'
local_filename = 'google.pdf'
save_webpage_as_pdf(url, local_filename)
