from bs4 import BeautifulSoup
import requests
import os
import sys



def QC_page_finder():
    os.makedirs('QC', exist_ok = True)
    url = 'https://questionablecontent.net/view.php?comic=1'
    base_url = 'https://questionablecontent.net'

    err_list = []
    page_count = 1


    while not url.endswith('#'):

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



        
        url = f'{base_url}/{next_link}'
        

        page_count += 1

    print(f'Errors were found downloading these comics: {err_list}')



QC_page_finder()





