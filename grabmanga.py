import requests
import bs4
import time 
from fpdf import FPDF
import os
import subprocess
import PIL

chapter=164
raw_website=requests.get(f'https://ww3.readdrstone.com/chapter/dr-stone-chapter-{chapter}'
).text
#
#
#
website=bs4.BeautifulSoup(raw_website,features="lxml")

chapter_tags=website.find_all('img',{'class':'mb-3 mx-auto js-page'})

chapter_images=[]

for tag in chapter_tags:
    chapter_images.append(tag['src'][0:65])

os.chdir('Documents/anime/Dr.stone')

chapter_directory=f'Dr.stone_chapter_{chapter}'

for link in chapter_images:

    subprocess.run(['wget','-P',chapter_directory,link,])
    time.sleep(2)

image_list=sorted(os.listdir(chapter_directory))


pdf=FPDF()
pdf.set_auto_page_break(0)

for image in image_list:
    image_directory=f'{chapter_directory}/{image}'
    image_dimensions=PIL.Image.open(image_directory).size
    if image_dimensions[0]<image_dimensions[1]:
        pdf.add_page()
        pdf.image(name=image_directory, x = -5, y = -5, w =210 , h = 0, type = '', link = '')
    else:
        pdf.add_page('L')
        pdf.image(name=image_directory, x = 5, y = -0, w =285 , h = 0, type = '', link = '')


pdf.output(f'{chapter_directory}.pdf', 'F')

subprocess.run(['rm','-r',chapter_directory])

