import requests
import shutil
from PIL import Image, ImageDraw, ImageFont
import os, glob, sys , time
import numpy as np
import textwrap , requests
import pyqrcode
from datetime import datetime

# from PIL import Image
# image = Image.open(r"gambar.jpeg")
def square(image):
    width, height = image.size
    if width == height:
        return image
    offset  = int(abs(height-width)/2)
    print(offset,height,width)
    #(offset,height,width) 161 1280 958

    if width>height:
        image = image.crop([offset,0,width-offset,height])
    else:
        # image = image.crop([100,250,1001,1750]) #((left, top, right, bottom))
        image = image.crop([0,offset,width,height-offset]) #((left, top, right, bottom))
    # image.show()
    return image

def rounded_img(img):  
    height,width = img.size
    lum_img = Image.new('L', [height,width] , 0)
    
    draw = ImageDraw.Draw(lum_img)
    draw.pieslice([(0,0), (height,width)], 0, 360, 
                fill = 255, outline = "black") #outline = "white"
    img_arr =np.array(img)
    lum_img_arr =np.array(lum_img)
    final_img_arr = np.dstack((img_arr,lum_img_arr))
    image = Image.fromarray(final_img_arr)
    image.save('hasil.png')
    return image

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def delete_file(image_path):
    if os.path.isfile(image_path):
       os.remove(image_path)

def save_photo(npm):
    urls= r"https://semesterpendek.gunadarma.ac.id/akademik_foto.ashx?npm={}&file=C:\inetpub\wwwroot\umanOnline\app.ini&default=C:\inetpub\wwwroot\umanOnline\assets\images\foto_default.jpg".format(npm)
    response = requests.get(urls, stream=True)
    img = Image.open(BytesIO(response.content))
    width, height = img.size
    if height >= 100 and width >= 100:
        with open(f'photo/{npm}.jpg', 'wb') as handle:
            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)

def id_card():
    image = Image.open(r"gambar.jpeg")
    im2 = square(image)
    im3 = add_corners(im2, 70)
    im3.save('tr.png', 'PNG')
    im1 = Image.open(r"tr.png")

    #================== Resize =========================
    basewidth = 525
    wpercent = (basewidth/float(im1.size[0]))
    hsize = int((float(im1.size[1])*float(wpercent)))
    hsize = 525
    im1 = im1.resize((basewidth,hsize), Image.ANTIALIAS)
    #===================================================

    #================= Merge Image =========================================
    im2 = Image.open('depan.jpg') 
    im2.paste(im1,(358, 575), mask=im1)
    image_editable = ImageDraw.Draw(im2)
    fontData =ImageFont.truetype("fonts/Montserrat-Light.ttf", 30)
    fontNama = ImageFont.truetype("fonts/Cocogoose Pro-trial.ttf", 42)

    nama = "Muhammad Rizdalah Agisa"
    para = textwrap.wrap(nama, width=35)
    MAX_W, MAX_H = 1250, 2210
    current_h, pad = 1180, 10
    for line in para:
        w, h = image_editable.textsize(line, font=fontNama)
        image_editable.text(((MAX_W - w) / 2, current_h), line,(0, 0, 0), font=fontNama)
        current_h += h + pad

    # image_editable.text((250,1210), caption_new, (0, 0, 0), font=ImageFont.truetype("fonts/Cocogoose Pro-trial.ttf", 42))
    # image_editable.text((250,1210), "Muhammad Rizdalah Agisa", (0, 0, 0), font=ImageFont.truetype("fonts/Cocogoose Pro-trial.ttf", 42))
    image_editable.text((570,1367), "555555555555555", (0, 0, 0),font=fontData)
    image_editable.text((570,1430), "Jl.Siaga Darma VIII No.18", (0, 0, 0),font=fontData)
    image_editable.text((570,1490), "Jakarta Selatan", (0, 0, 0),font=fontData)
    image_editable.text((570,1552), "Anggota", (0, 0, 0),font=fontData)
    im2.save('final.jpg')
    im2.show() 
    #========================================================================

def download_image():
    url = "http://127.0.0.1:5000/get_image"
    data = requests.get(url , stream=True)
    with open('img.png', 'wb') as out_file:
        shutil.copyfileobj(data.raw, out_file)
    del data

def qr_code():
    url = pyqrcode.QRCode('http://www.eqxiu.com',error = 'H')
    url.png('test.png',scale=10)
    im = Image.open('test.png')
    im = im.convert("RGBA")
    logo = Image.open('logo.png')
    box = (135,135,235,235)
    im.crop(box)
    region = logo
    region = region.resize((box[2] - box[0], box[3] - box[1]))
    im.paste(region,box,mask=region)
    # im.show()
    im1 = im
    basewidth = 640
    wpercent = (basewidth/float(im1.size[0]))
    hsize = int((float(im1.size[1])*float(wpercent)))
    hsize = 640
    im1 = im1.resize((basewidth,hsize), Image.ANTIALIAS)

    im2 = Image.open('belakang.jpg') 
    im2.paste(im1,(300, 445), mask=im1)
    image_editable = ImageDraw.Draw(im2)
    fontData =ImageFont.truetype("fonts/Roboto/Roboto-Bold.ttf", 32)
    now = datetime.now() 
    tahun = int(now.strftime("%Y"))+1
    expire = now.strftime("%d-%m-")+str(tahun)
    image_editable.text((640,1116), expire, font=fontData, fill="#fff")
    im2.save("kartu_belakang.jpg")
    im2.show()
# id_card()

qr_code()