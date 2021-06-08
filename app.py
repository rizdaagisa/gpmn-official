from flask import Flask, jsonify, request, send_file
from datetime import datetime
import shutil
import requests
from PIL import Image, ImageDraw, ImageFont
import os, glob, sys , time,re
import numpy as np
import textwrap
import pyqrcode


base = "https://gpmn-official.herokuapp.com/"
base2 = "https://gpmn-official.com/"
app = Flask(__name__)
back_card = '/static/back'
front_card = '/static/front'
profile_img = '/static/profile'
qr_img = '/static/qrcode'

app.config['back_card'] = back_card
app.config['front_card'] = front_card
app.config['profile_img'] = profile_img
app.config['qr_img'] = qr_img

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

path = os.path.dirname(__file__)
b= os.listdir(path)
print(path)
print(b)

path = path.replace("\\","/")
# os.environ['LD_LIBRARY_PATH'] = os.getcwd()

def download_imagee(img):
    url = base2+"assets/ktp/"+img
    data = requests.get(url , stream=True)
    with open(img, 'wb') as out_file:
        shutil.copyfileobj(data.raw, out_file)
        os.path.join(app.config['UPLOAD_FOLDER'], filename)
    # shutil.move(img, "static/profile/"+img)
    del data
    # return True

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

def kartu_belakang(id):
    try:
        url = pyqrcode.QRCode('http://localhost/profile.php?id='+id, error = 'H')
        url.png('qrcode.png',scale=8)
        im = Image.open('qrcode.png')
        shutil.copy('qrcode.png', 'static/qrcode/'+id+'.png')
        im = im.convert("RGBA")
        logo = Image.open('logo.png')
        box = (140,140,240,240)
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
        im2.save("static/back/"+id+".jpg")
        print("success","static/back/"+id+".jpg")
        # im2.show()
        return True
    except Exception as e:
        print(e)
        return False
    
def kartu_depan(result):
    try:
        nama = result['nama']
        alamat = result['alamat']
        id = result['no_anggota']
        status_anggota = result['status_anggota']
        kota = result['kota']
        foto = result['foto']

        download_imagee(foto)
        image = Image.open(foto)
        im2 = square(image)
        im3 = add_corners(im2, 45)
        im3.save("static/profile/"+id +'.png', 'PNG')
        os.remove(foto)
        im1 = Image.open("static/profile/"+id+".png")

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

        # nama = "Muhammad Rizdalah Agisa"
        para = textwrap.wrap(nama, width=35)
        MAX_W, MAX_H = 1250, 2210
        current_h, pad = 1180, 10
        for line in para:
            w, h = image_editable.textsize(line, font=fontNama)
            image_editable.text(((MAX_W - w) / 2, current_h), line,(0, 0, 0), font=fontNama)
            current_h += h + pad

        # image_editable.text((250,1210), caption_new, (0, 0, 0), font=ImageFont.truetype("fonts/Cocogoose Pro-trial.ttf", 42))
        # image_editable.text((250,1210), "Muhammad Rizdalah Agisa", (0, 0, 0), font=ImageFont.truetype("fonts/Cocogoose Pro-trial.ttf", 42))
        image_editable.text((570,1367), id, (0, 0, 0),font=fontData)
        image_editable.text((570,1430), alamat, (0, 0, 0),font=fontData)
        image_editable.text((570,1490), kota, (0, 0, 0),font=fontData)
        image_editable.text((570,1552), "Anggota "+status_anggota, (0, 0, 0),font=fontData)
        im2.save("static/front/"+id+".jpg")
        print("success",base+"static/front/"+id+".jpg")
        # im2.show()
        #========================================================================
        return True
    except Exception as e:
        print(e)
        return False


@app.route('/get_image') #://example.com/get_image?type=1
def get_image():
    if request.args.get('type') == '1':
           filename = 'logo.png'
    else:
       filename = 'logo.png'
    # filename = 'logo.png'
    return send_file(filename, mimetype='image/gif')

@app.route('/download')
def download_image():
    url = "http://127.0.0.1:5000/get_image"
    data = requests.get(url , stream=True)
    with open('img.png', 'wb') as out_file:
        shutil.copyfileobj(data.raw, out_file)
    del data

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
       result = request.get_json(force=True)
       nik = result['nik']
       nama = result['nama']
       no_anggota = result['no_anggota']

       f = request.files['file']
       f.save(secure_filename(f.filename))
       return 'file uploaded successfully'

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'GET':
        return "mau ngapain bro?"

    if request.method == 'POST':
        result = request.get_json(force=True)
        print(result)
        depan = kartu_depan(result)
        belakang = kartu_belakang(result['no_anggota'])
        if((depan == True) and (belakang == True)):
            data = {
                "result" : "ok",
                "kartu_depan" : base+"static/front/"+result['no_anggota']+".jpg",
                "kartu_belakang" : base+"static/back/"+result['no_anggota']+".jpg"
            }
            return data
        else:
            return {'result' : 'failed'}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    # app.run(debug=True)