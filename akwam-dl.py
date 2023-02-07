import re, os
from requests import get

HTTP = 'https://'
YOUR_CHOICE = '\n[+] Your Choice: '
DL_URL_RGX = r'https?://(redirect\.khsm\.io/link/\d+)'

class Akwam:
    def __init__(self, url):
        url = get(url).url
        self.url = [url, url[:-1]][url[-1] == '/']
        self.search_url = self.url + '/search?q='
        self.cur_page = None
        self.qualities = {}
        self.results = None
        self.parsed = None
        self.dl_url = None
        self.type = 'movie'

    def select(self, choice, is_index=False):
        if is_index:
            choice = [*self.results.keys()][choice - 1]
        self.cur_url = self.results[choice]

    def parse(self, regex, no_multi_line=False):
        page = self.cur_page.content.decode()
        if no_multi_line:
            page = page.replace('\n', '')
        self.parsed = re.findall(regex, page)

    def load(self):
        self.cur_page = get(self.cur_url)
        self.parse(
            r'tab-content quality.*?a href="' + DL_URL_RGX + r'"',
            no_multi_line=True
        )
        i = 0
        for q in ['1080p', '720p', '480p']:
            if f'">{q}</' in self.cur_page.text:
                self.qualities[q] = self.parsed[i]
                i += 1

    def search(self, query, page=1):
        query = query.replace(' ', '+')
        self.cur_page = get(f'{self.search_url}{query}&section={self.type}&page={page}')
        self.parse(rf'({self.url}/{self.type}/\d+/.*?)"')
        self.results = {
            url.split('/')[-1].replace('-', ' ').title(): url \
                for url in self.parsed[::-1]
        }

    def fetch_episodes(self):
        self.cur_page = get(self.cur_url)
        self.parse(rf'({self.url}/episode/\d+/.*?)"')
        self.results = {
            url.split('/')[-1].replace('-', ' ').title(): url \
                for url in self.parsed[::-1]
        }
    
    def get_direct_url(self, quality='720p', fix_asia=False):
        print('\n>> Solving shortened URL...')
        self.cur_page = get(HTTP + self.qualities[quality])
        print(HTTP + self.qualities[quality])
        self.parse(r'(akwam.[a-z]+/download/.*?)"')

        # if fix_asia:
        #     self.parsed[0] = self.parsed[0].replace('.asia', '.cz')

        print('>> Getting Direct URL...')
        self.cur_page = get(HTTP + self.parsed[0])
        self.parse(r'([a-z0-9]{4,}\.akwam\.[a-z]+/download/.*?)"')

        self.dl_url = HTTP + self.parsed[0]

    def download(self):
        os.system(f'start "" "{self.dl_url}"')
    
    def show_results(self):
        if not self.results:
            print('>> Found Nothing!')
            return

        print(f'>> Choose {self.type.title()}:\n')
        for n, name in enumerate(self.results):
            print(f'  [{n + 1}] {name}')
    
    def show_episodes(self):
        print('>> Choose Episode:\n')
        for n, episode in enumerate(self.results):
            print(f'  [{n + 1}] {episode}')

    def show_qualities(self):
        print('>> Choose Quality:\n')
        for n, quality in enumerate(self.qualities):
            print(f'  [{n + 1}] {quality}')

def main():
    while True:
        print(
    '''
     █████╗ ██╗  ██╗██╗    ██╗ █████╗ ███╗   ███╗      ██████╗ ██╗   v1.2
    ██╔══██╗██║ ██╔╝██║    ██║██╔══██╗████╗ ████║      ██╔══██╗██║       
    ███████║█████╔╝ ██║ █╗ ██║███████║██╔████╔██║█████╗██║  ██║██║       
    ██╔══██║██╔═██╗ ██║███╗██║██╔══██║██║╚██╔╝██║╚════╝██║  ██║██║       
    ██║  ██║██║  ██╗╚███╔███╔╝██║  ██║██║ ╚═╝ ██║      ██████╔╝███████╗  
    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝     ╚═╝      ╚═════╝ ╚══════╝  
                                                    www.github.com/elmoiv
                
    '''
        )

        print('>> Resolving Akwam URL...\n')
        API = Akwam('https://on.akwam.cx/')

        _type = input('[+] Select Type:\n [1] Movies\n [2] Series\nType: ')
        API.type = ['movie', 'series'][int(_type) - 1]
        
        query = input('\n[+] Search for: ')
        print(f'\n>> Searching for "{query}"...\n')
        API.search(query)
        API.show_results()
        if not API.results:
            input('\n[!] Press Enter to Try Again or Ctrl+C to exit:')
            os.system('CLS')
            continue
        result = input(YOUR_CHOICE)
        API.select(int(result), True)

        if API.type == 'series':
            print('\n>> Getting Episodes...\n')
            API.fetch_episodes()
            API.show_episodes()
            result = input(YOUR_CHOICE)
            API.select(int(result), True)

        print('\n>> Fetching Qualities...\n')
        API.load()

        API.show_qualities()
        result = input(YOUR_CHOICE)

        # try:
        API.get_direct_url([*API.qualities.keys()][int(result) - 1])
        # except:
        #     print('\n>> Server Down, Trying different method...')
        #     API.get_direct_url([*API.qualities.keys()][int(result) - 1], True)

        print('\n>> Your Direct URL:', API.dl_url)

        if not input('\n[+] Press Enter to download or anything to skip: '):
            API.download()
        
        try:
            input('\n[!] Press Enter to Try Again or Ctrl+C to exit:')
        except KeyboardInterrupt:
            exit(0)
        os.system('CLS')

if __name__ == '__main__':
    main()
