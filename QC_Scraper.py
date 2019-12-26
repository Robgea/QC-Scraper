from bs4 import BeautifulSoup
import requests
import os
import sys
import shelve



def QC_page_finder():
    os.makedirs('QC', exist_ok = True)
    err_list = []
    base_url = 'https://questionablecontent.net'

    QC_tracker = shelve.open('QC_tracker', writeback = True)

    if 'page_count' in QC_tracker:

        page_count = QC_tracker['page_count']
        url = f'https://questionablecontent.net/view.php?comic={page_count - 1}'
        sys.stdout.write(f'Page count == {page_count}, URL == {url}.')
        sys.stdout.flush()

        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html5lib')
            img = soup.find_all(id = 'strip')
            next_link = img[0].parent.get('href')
            if next_link.endswith('#'):
                sys.stdout.write('No new comics since this was last run.')
                sys.stdout.flush()
                return 'DONE!'
            else: 
                sys.stdout.flush('Continuing from last comic.')
                sys.stdout.flush()
                url = f'{base_url}/{next_link}'
        except:
            sys.stdout.write('Not able to reach the QC server. Aborting operation!\n')
            sys.stdout.flush()
            return 'DONE!'

    else:

        url = 'https://questionablecontent.net/view.php?comic=1'
        page_count = 1

        try:
            test = requests.get(url)

        except:
            sys.stdout.write('Not able to reach the QC server. Aborting operation!\n')
            sys.stdout.flush()
            return 'DONE!'

    while not url.endswith('#'):

        try:

            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html5lib')
            
            img = soup.find_all(id = 'strip')
            img_info = img[0].get('src')
            next_link = img[0].parent.get('href')
            img_link = f'{base_url}{img_info[1:]}'
            
            if len(img) != 1:
                err_list.append(page_count)
                
            else:
                image = requests.get(img_link)
                sys.stdout.write('\n')
                sys.stdout.write(f'Downloading comic number {page_count}')
                sys.stdout.flush()
                comname = f'QC{str(page_count).zfill(4)}{img_link[-4:]}'
                imageFile = open(os.path.join('QC', os.path.basename(comname)), 'wb')
                for chunk in image.iter_content(100_000):
                    imageFile.write(chunk)
                imageFile.close()

        except:
            sys.stdout.write(f'Error in downloading comic number {page_count}. Saving progress and aborting process.\n')
            sys.stdout.flush()
            url = f'https://questionablecontent.net/view.php?comic={page_count}'
            QC_tracker['page_count'] = page_count
            QC_tracker['url'] = url
            QC_tracker.close()
            return 'Error!'
        
        url = f'{base_url}/{next_link}'
      
        page_count += 1

    QC_tracker['page_count'] = page_count
    QC_tracker['url'] = url
    QC_tracker.close()

    sys.stdout.write('All done!')
    sys.stdout.flush()

    if len(err_list) > 1 :
        sys.stdout.write(f'Errors were found downloading these comics: {err_list}')
        sys.stdout.flush()

def main():
    QC_page_finder()

if __name__ == '__main__':
    main()