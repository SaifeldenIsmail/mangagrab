import time
import subprocess
import sys
import os
import requests
import bs4
from fpdf import FPDF
import PIL

def pick_option(options):
    for index, option in enumerate(options):
        print(f'{index}) {option.text}')
    valid_input=True
    while valid_input:
        choice=input("which manga were you searching for? ")
        try: 
            return options[int(choice)]
        except: 
            print('please pick a valid number. ')

def query(search):
    manga=requests.get(f'https://kissmanga.org/manga_list?q={search}&action=search').text
    manga_query=bs4.BeautifulSoup(manga,features='lxml')
    grab_top=manga_query.find_all('a',{'class':'item_movies_link'})
    option=pick_option(grab_top)
    rec=f'https://kissmanga.org{option["href"]}'
    return rec

def iterate(search,x):
    rec=query(search)
    chapter_link=f'{rec}/chapter_{x}'
    return chapter_link 

def recent_chapter(search):
    re=query(search)
    rec=requests.get(re).text
    rec_part=bs4.BeautifulSoup(rec,features='lxml').find_all('a')
    cc=[]
    for i in rec_part:
        try:
            if i['title'][:4]=='Read':
                cc.append(i)
        except:
            pass

    recent_part=cc[0]
    recent_part_link=recent_part['href']
    recent_link=f'https://kissmanga.org{recent_part_link}'
    chapter=recent_part.text.split(' ',1)[1].split('Chapter',1)[1]

    return recent_link,chapter

def grab_links(recent):
      
    raw_website=requests.get(recent.replace('manga','chapter',2).replace('chapter','manga',1)).text

    website=bs4.BeautifulSoup(raw_website,features="lxml")
    chapter_tags=website.find_all('div',{'id':'centerDivVideo'})
    image_tags=chapter_tags[0].find_all('img')
    image_links=[]

    for tag in image_tags:
        image_links.append(tag['src'])
    return image_links

def download_images(image_links,chapter):
    os.chdir('manga')
    chapter_directory=f'{sys.argv[1]}/{sys.argv[1]}_{chapter}'
    subprocess.run(['mkdir','-p',chapter_directory])
    i=0

    for link in image_links:
        subprocess.run(['wget','-O',f'{chapter_directory}/{i}.jpg',link])
        time.sleep(0.1)
        i+=1
    return chapter_directory

def convert_to_pdf(chapter_directory,chapter):
    image_list=os.listdir(chapter_directory)
    image_list.sort(key=lambda x: int(x[:-4]))
    dimensions= PIL.Image.open(f'{chapter_directory}/{image_list[2]}').size
    mmw=int(dimensions[0]/3.7795275591)
    mmh=int(dimensions[1]/3.7795275591)
    pdf=FPDF('P', 'mm', (mmw,mmh))
    pdf.set_auto_page_break(0)
    
    for image in image_list:
        image_directory=f'{chapter_directory}/{image}'
        image_dimensions=PIL.Image.open(image_directory).size
        if image_dimensions[0]<image_dimensions[1]:
            pdf.add_page()
            pdf.image(name=image_directory, x = -0, y = -0, w =mmw , h = 0, type = '', link = '')
        else:
            pdf.add_page('L')
            pdf.image(name=image_directory, x = 0, y = -0, w =mmh , h = 0, type = '', link = '')
    
    os.chdir(sys.argv[1])
    pdf.output(f'{sys.argv[1]}_chapter_{chapter}.pdf', 'F')
    
    subprocess.run(['rm','-r',f'{sys.argv[1]}_{chapter}'])
    os.chdir('../../')

#running code below

#try:
#except:
#    chapter=recent_chapter()
#
#image_links=grab_links(chapter)
#chapter_directory=download_images(image_links,chapter)
#convert_to_pdf(chapter_directory)
def main(recent_link,chapter):
    image_links=grab_links(recent_link)
    chapter_directory=download_images(image_links,chapter)
    convert_to_pdf(chapter_directory,chapter)


if len(sys.argv)==2:
    recent_link,chapter=recent_chapter(sys.argv[1])
    main(recent_link,chapter)

elif len(sys.argv)==3:
    chapter=sys.argv[2]
    recent_link=iterate(sys.argv[1],chapter)
    main(recent_link,chapter)

elif len(sys.argv)==4:

    for chapter in range(int(sys.argv[2]),int(sys.argv[3])+1):
        recent_link=iterate(sys.argv[1],chapter)
        main(recent_link,chapter)

else:
    print('updating list')


    




