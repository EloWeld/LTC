import collections, logging, bs4, requests, csv

from gsheets import Sheets

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('ltc')

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'timestamp',
        'block_num',
        'rate',
    ),
)

HEADERS = (
    'TIME',
    'BLOCK',
    'CURRENCY RATE',
)

class Client():

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 OPR/77.0.4054.298 (Edition Yx GX)',
            'Accept-Language': 'ru',
        }
        self.result = dict()

    def load_page(self, page: int = None):
        if page > 1:
            url = f'https://bitinfocharts.com/ru/top-100-richest-litecoin-addresses-{page}.html'
        else:
            url = 'https://bitinfocharts.com/ru/top-100-richest-litecoin-addresses.html'
        result = self.session.get(url=url)
        return result.text

    def parse_page(self, text : str):
        soup = bs4.BeautifulSoup(text, 'html.parser')
        container = soup.select_one('table.table.table-striped.abtb').select('tr')
        t = 0
        for block in container:
            t += 1
            self.parse_block(block)
            if t > 2:
                break

    def parse_block(self, block):
        #Article
        for link in block.select('a'):
            if link.parent.name != 'small':
                href = link.get('href')
                wallet = link.text
                print(href, wallet)
                self.result[wallet] = []
                txt = self.load_wallet(wallet)
                self.parse_wallet(txt, wallet)

    def load_wallet(self, addr):
        url = 'https://bitinfocharts.com/ru/litecoin/address/' + addr
        result = self.session.get(url=url)
        return result.text

    def parse_wallet(self, text : str, wallet: str):
        soup = bs4.BeautifulSoup(text, 'html.parser')
        self.result[wallet] = []
        table = soup.select('span.muted.utc')
        attemps = 0
        for tr in table:
            try:
                attemps += 1
                blocknum = tr.parent.select_one('a').text
                currency_sum = requests.get(f'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/{tr.text.split()[0]}/currencies/usd/ltc.json').json()["ltc"]
                self.result[wallet].append(ParseResult(tr.text, blocknum, currency_sum))
                if attemps > 2:
                    break
            except:
                pass

    def run_client(self):
        for page in range(1, 1 + 1):
            text = self.load_page(page=page)
            self.parse_page(text=text)
            print(f'PAGE {page} PARSED')

        print(f'Got {len(self.result)} elements')
        #Sheets
        gsheets = Sheets()
        gsheets.clear_sheets()
        for s in self.result.items():
            print(f'GSHEET {s[0]} SHEET')
            gsheets.write_matrix(s[1], s[0])
        print('Result saved in Google sheets')




def parse_ltc_wallets():
    parser = Client()
    parser.run_client()