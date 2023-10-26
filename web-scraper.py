import requests
from bs4 import BeautifulSoup

# fetch input url
url = input("Enter URL to scrape: (OR empty for default) ")
if not url:
    url = 'https://m365internals.com/2021/11/30/lateral-movement-with-managed-identities-of-azure-virtual-machines/'

# fetch HTML markup
response = requests.get(url)

if response.status_code == 200:
    # iterate and print preformatted code blocks.
    soup = BeautifulSoup(response.text, 'html.parser')
    code_segments = soup.find_all('code')
    for code_segment in code_segments:
        print("-----------------------------------------")
        print(code_segment.get_text())
        print("-----------------------------------------")
else:
    print('Failed to retrieve the webpage. Status code:', response.status_code)
