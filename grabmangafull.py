from time import sleep
from subprocess import run
import sys
import argparse
from os import chdir, listdir
from requests import get
from bs4 import BeautifulSoup
from fpdf import FPDF
from PIL import Image 

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
    manga=get(f'https://kissmanga.org/manga_list?q={search}&action=search').text
    manga_query=BeautifulSoup(manga,features='lxml')
    grab_top=manga_query.find_all('a',{'class':'item_movies_link'})
    option=pick_option(grab_top)
    rec=f'https://kissmanga.org{option["href"]}'
    return rec

def iterate(rec,x):
    chapter_link=f'{rec}/chapter_{x}'
    return chapter_link 

def recent_chapter(rec):
    rec_part=BeautifulSoup(get(rec).text,features='lxml').find_all('a')
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
      
    raw_website=get(recent.replace('manga','chapter',2).replace('chapter','manga',1)).text

    website=BeautifulSoup(raw_website,features="lxml")
    chapter_tags=website.find_all('div',{'id':'centerDivVideo'})
    image_tags=chapter_tags[0].find_all('img')
    image_links=[]

    for tag in image_tags:
        image_links.append(tag['src'])
    return image_links

def download_images(image_links,chapter):
    chdir('manga')
    chapter_directory=f'{args.manga}/{args.manga}_{chapter}'
    run(['mkdir','-p',chapter_directory])
    i=0

    for link in image_links:
        run(['wget','-O',f'{chapter_directory}/{i}.jpg',link])
        sleep(0.1)
        i+=1
    return chapter_directory

def convert_to_pdf(chapter_directory,chapter):
    image_list=listdir(chapter_directory)
    image_list.sort(key=lambda x: int(x[:-4]))
    dimensions= Image.open(f'{chapter_directory}/{image_list[2]}').size
    mmw=int(dimensions[0]/3.7795275591)
    mmh=int(dimensions[1]/3.7795275591)
    pdf=FPDF('P', 'mm', (mmw,mmh))
    pdf.set_auto_page_break(0)
    
    for image in image_list:
        image_directory=f'{chapter_directory}/{image}'
        image_dimensions=Image.open(image_directory).size
        if image_dimensions[0]<image_dimensions[1]:
            pdf.add_page()
            pdf.image(name=image_directory, x = -0, y = -0, w =mmw , h = 0, type = '', link = '')
        else:
            pdf.add_page('L')
            pdf.image(name=image_directory, x = 0, y = -0, w =mmh , h = 0, type = '', link = '')
    
    chdir(args.manga)
    pdf.output(f'{args.manga}_chapter_{chapter}.pdf', 'F')
    
    run(['rm','-r',f'{args.manga}_{chapter}'])
    chdir('../../')

def main(recent_link,chapter):
    image_links=grab_links(recent_link)
    chapter_directory=download_images(image_links,chapter)
    convert_to_pdf(chapter_directory,chapter)



parser=argparse.ArgumentParser()

parser.add_argument('--manga','-m',required=True)

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--through','-t',nargs=2,type=int)
group.add_argument('--single','-s',nargs='*')
group.add_argument('--recent','-r',action='store_true')

args = parser.parse_args()


if args.single:

    rec=query(args.manga)
    for single_chapter in args.single:
        chapter=single_chapter
        recent_link=iterate(rec,chapter)
        main(recent_link,chapter)

if args.through:

    rec=query(args.manga)
    for chapter in range(args.through[0],args.through[1]+1):
        recent_link=iterate(rec,chapter)
        main(recent_link,chapter)

if args.recent:
    rec=query(args.manga)
    recent_link,chapter=recent_chapter(rec)
    main(recent_link,chapter)

