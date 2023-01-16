# Importing necessary libraries
import requests
import bs4

# Preparing base names
print("Initializing...")
tickers = []
missed_isins = []
base_url = 'https://de.wikipedia.org'
parser = 'html.parser'

# Get the DAX companies from Wikipedia
res = requests.get('https://de.wikipedia.org/wiki/DAX')
print("Webpage OK")
soup = bs4.BeautifulSoup(res.text, parser)
print("HTML dump OK")
table = soup.find('table', {'class': 'wikitable sortable'})
if table is not None:
    print("Table OK, starting scrape...")
    # Get the ticker for each company
    for row in table.find_all('tr')[1:]:
        link_cell = row.find_all('td')[0]
        link = base_url + link_cell.find('a').get('href')

        # Get the ISIN from the company's Wikipedia page
        company_res = requests.get(link)
        company_soup = bs4.BeautifulSoup(company_res.text, parser)
        isin_cell = company_soup.find('a', string='ISIN').find_parent('td')
        if isin_cell:
            isin = isin_cell.find_next_sibling('td').text.strip()
            if len(isin) > 12:
                isin = isin[:12]
            # Use the ISIN to get the ticker from eulerpool
            ticker_res = requests.get(f'https://www.eulerpool.com/aktie/{isin}')
            ticker_soup = bs4.BeautifulSoup(ticker_res.text, parser)
            ticker_box = ticker_soup.find('div', {
                'class': 'text-sm mr-3 inline-flex items-center w-fit justify-self-end cursor-pointer rounded-lg '
                         '-ml-2 px-2 py-1 bg-transparent hover:shadow'})
            if ticker_box is not None:
                ticker = ticker_box.text.strip()
                # Debugging/Tracker print
                print(f"Adding {ticker}")
                tickers.append(ticker)
            else:
                print(f"Skipping {isin}")
                missed_isins.append(isin)
else:
    print("Table not found")

if tickers is not None:
    # Write the tickers to a text file
    print("Scraping complete.")
    print("Formatting symbols...")
    with open('tickers.txt', 'w') as f:
        for ticker in tickers:
            if len(ticker) > 4:
                ticker = ticker[:len(ticker) - 3]
            print(f"Added {ticker}")
            f.write(ticker + '\n')
    print("Printing missed ISINs...")
    with open('missed_isins.txt', 'w') as g:
        for isin in missed_isins:
            print(f"Missed {isin}")
            g.write(isin + '\n')
else:
    print("Ticker list empty")