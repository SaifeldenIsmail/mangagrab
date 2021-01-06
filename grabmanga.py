import requests
import bs4
import time 
from fpdf import FPDF
import os
import subprocess
import PIL

p=requests.get('https://ww3.readdrstone.com/chapter/dr-stone-chapter-165').text

g=bs4.BeautifulSoup(p,features="lxml").find_all('option')
#chapter=g[1].text[-3:]
chapter=43
#
raw_website=requests.get(f'https://ww3.readdrstone.com/chapter/dr-stone-chapter-{chapter}'
).text
#
#
#
website=bs4.BeautifulSoup(raw_website,features="lxml")

chapter_tags=website.find_all('img',{'class':'mb-3 mx-auto js-page'})

chapter_images=[]

for tag in chapter_tags:
     
    g=tag['src']
    try: 
        split_string = g.split("url=", 1)
        chapter_images.append(split_string[1])


    except:
        chapter_images.append(g)
os.chdir('Documents/anime/Dr.stone')

chapter_directory='Dr.stone_chapter_{}/{}.jpg'
chapter_folder=f'Dr.stone_chapter_{chapter}'
page_number=0
subprocess.run(['mkdir',chapter_folder])
for link in chapter_images:

    

    subprocess.run(['wget','-O',chapter_directory.format(chapter,page_number),link])
    time.sleep(1)
    page_number+=1

image_list=os.listdir(chapter_folder)
image_list.sort(key=lambda x: int(x[:-4]))


pdf=FPDF()
pdf.set_auto_page_break(0)

for image in image_list:
    image_directory=f'{chapter_folder}/{image}'
    image_dimensions=PIL.Image.open(image_directory).size
    if image_dimensions[0]<image_dimensions[1]:
        pdf.add_page()
        pdf.image(name=image_directory, x = -5, y = -5, w =210 , h = 0, type = '', link = '')
    else:
        pdf.add_page('L')
        pdf.image(name=image_directory, x = 5, y = -0, w =285 , h = 0, type = '', link = '')


pdf.output(f'{chapter_folder}.pdf', 'F')


subprocess.run(['rm','-r',chapter_folder])
