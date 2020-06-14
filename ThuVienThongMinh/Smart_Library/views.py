from django.shortcuts import render
from django.http import HttpResponse
from .forms import Register, Sach, Message
from . import nouden as no
from django.views import View
from django.http import StreamingHttpResponse, HttpResponseServerError, HttpResponseRedirect, JsonResponse
from .models import Book, DocGia, Cart, Check_book, Category_Book,ID_DocGia,ID_Book
import serial
import numpy as np
import cv2
import pickle
import datetime
import time
from django.views.decorators import gzip
import os
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib.auth import decorators
from django.contrib.auth.mixins import LoginRequiredMixin
from . import face_training
from django.contrib import messages
import serial
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_control

import pytz
from django.db.models import (
    Count,
)
from .filters import BookFilter
from django.conf import settings
import shutil

# Create your views here.

global name
name = ""
id_check = ""
id_user = ""

z = ""
id_regis = ""
check_image=0
y=""


def scan_user(request):
    if request.is_ajax():
        global z,y
        try:
            z = no.getiduser()

        except:
            pass

        if z == "":
            context = {'id_user': z}
            return JsonResponse(context)
        elif len(z) == 8:
            context = {'id_user': z}
            return JsonResponse(context)
        else:
            z=""
            context = {'id_user': z}
            return JsonResponse(context)
    else:
        return HttpResponse("This route only handles AJAX requests")



id_ne = ""


class begin1(View):
    def get(self, request):
        try:
            del request.session['login']
            print(1)
            cache.clear()
        except:
            pass
        global id_user
        id_user = ""
        global id_ne
        id_re = id_ne
        id_ne = ""
        print("id_re", id_re)
        path = "./image_temp/"
        dics = os.listdir(path)
        if id_re != "":
            try:
                DocGia.objects.get(id_DG=id_re)
                for dic in dics:
                    if dic == id_re:
                        print(1)
                        shutil.rmtree('./image_temp/' + dic)
                        return render(request, 'login/begin.html')

            except ObjectDoesNotExist:
                try:
                    for dic in dics:
                        if dic == id_re:
                            print(1)
                            shutil.rmtree('./image_temp/' + dic)
                            return render(request, 'login/begin.html')

                except OSError:
                    print("Không xóa được")
                    return render(request, 'login/begin.html')

        else:
            return render(request, 'login/begin.html')


class register(View):
    def get(self, request):
        global id_ne
        id_ne = no.getiduser()
        print("data", id_ne)
        if id_ne == "":
            return redirect('/')
        q = Register()
        return render(request, 'login/register.html', {'f': q, 'id_card': id_ne})

    def post(self, request):
        q = Register(request.POST, request.FILES)
        if q.is_valid():
            a = request.POST.get('id_DG')
            try:
                DocGia.objects.get(id_DG=a)
                path1 = "./image_temp/"
                image = os.listdir(path1)
                shutil.rmtree('./image_temp/' + image[0])
                messages.error(request, "Thẻ đã được đăng kí")
                return render(request, 'login/begin.html')
            except ObjectDoesNotExist:
                q.save()
                path = "./Image/" + a + '/'
                dest = "./image_book/image_user/"
                dest1 = "/image_user/"
                path1 = "./image_temp/"
                dest2 = "./Image/"
                shutil.move(path1 + a, dest2)
                image = os.listdir(path)
                print(image[0])
                shutil.copy2(path + image[0], dest)
                im = DocGia.objects.get(id_DG=a)
                im.image_user = dest1 + image[0]
                im.save()
                face_training.train()
                face_training.eye_train()
                global id_ne
                id_ne = ""
                messages.success(request, "Tài khoản được tạo thành công")
                return render(request, 'login/begin.html')


def get_frame():
    camera = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(
        'I:\Program Files\Python\Lib\site-packages\cv2\data\haarcascade_frontalface_alt2.xml')

    a = id_regis
    b = a
    try:
        # creating a folder named data
        if os.path.exists('image_temp/' + b):
            os.remove('image_temp/' + b)
            os.makedirs('image_temp/' + b)
            print("trung")
        else:
            os.makedirs('image_temp/' + b)
    # if not created then raise error
    except OSError:
        print('Error: Creating directory of Image')
    currentframe = 0
    start = datetime.datetime.now()
    second_start = start.second
    minute_start = start.minute
    hour_start = start.hour
    c = hour_start * 3600 + minute_start * 60 + second_start
    data = 0
    while True:
        global check_image
        check_image = 0
        end = datetime.datetime.now()
        second_end = end.second
        minute_end = end.minute
        hour_end = end.hour
        b = hour_end * 3600 + minute_end * 60 + second_end
        ret, img = camera.read()
        img1 = img
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
        faces = sorted(faces, key=lambda x: x[2] * x[3],
                       reverse=True)
        faces = faces[:1]
        if len(faces) == 1:
            face = faces[0]
            # lưu lại những điểm của khuôn mặt
            x, y, w, h = face
            color = (255, 0, 0)
            stroke = 2
            end_cord_x = x + w
            end_cord_y = y + h
            font = cv2.FONT_HERSHEY_SIMPLEX
            stroke = 2
            if currentframe != 5:
                cv2.rectangle(img1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img1, "Processing", (150, 100), font, 2, color, stroke, cv2.LINE_AA)
            else:
                cv2.putText(img1, "Done", (240, 100), font, 2, color, stroke, cv2.LINE_AA)
                cv2.putText(img1, "Done", (240, 100), font, 2, color, stroke, cv2.LINE_AA)

        imgencode = cv2.imencode('.jpg', img)[1]
        stringData = imgencode.tostring()
        yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')
        if b-c >= 13:
            if len(faces) == 0:
                check_image = 0
                break
            c = b
        if currentframe != 5:
            if b - c >= 2:
                if len(faces) == 1:
                    face = faces[0]
                    x, y, w, h = face
                    image = img[y:y + h, x:x + w]
                    # lưu lại những điểm của khuôn mặt
                    name = './image_temp/' + a + '/' + a + str(currentframe) + '.jpg'
                    print('Creating...' + name)
                    cv2.imwrite(name, image)
                    currentframe += 1
                    c = b
        else:
            cv2.putText(img1, "Done", (240, 100), font, 2, color, stroke, cv2.LINE_AA)
            check_image = 1
            break
    del (camera)


# stream_video
def video_feed(request):
    try:
        return StreamingHttpResponse(get_frame(), content_type='multipart/x-mixed-replace; boundary=frame')
    except:
        return "error"


# Login
class login(View):
    def get(self, request):
        try:
            del request.session['login']
        except KeyError:
            pass
        return render(request, 'login/login.html')

    def post(self, request):
        id_check = request.POST.get('id_check')
        request.session['login'] = id_check
        global id_user
        try:
            DocGia.objects.get(id_DG=id_check)
            try:
                c = camera_recognize(id_check)
                if (c == 1):
                    id_user = id_check
                    user = DocGia.objects.get(id_DG=id_user)
                    book = Book.objects.all()
                    book1 = book.filter(active=True)
                    sl = book1.aggregate(Count('id'))
                    Data = {'list_book': Book.objects.all(), 'sl': sl, 'tenDG': user.ten_DG}
                    return redirect('/book/')
                else:
                    messages.error(request, "Khuôn mặt không khớp")
                    return render(request, 'login/begin.html')
            except:
                return "error"
        except ObjectDoesNotExist:
            messages.error(request, "ID chưa được đăng kí")
            return render(request, 'login/begin.html')


# nhận dạng khuôn mặt
def camera_recognize(check):
    camera = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier('I:\Program Files\Python\Lib\site-packages\cv2\data\haarcascade_frontalface_alt.xml')
    eyes_cascade = cv2.CascadeClassifier('I:\Program Files\Python\Lib\site-packages\cv2\data\haarcascade_eye.xml')

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer.yml")

    eyes_recognizer = cv2.face.LBPHFaceRecognizer_create()
    eyes_recognizer.read("eyes-trainner.yml")

    labels = {"person_name": 1}
    with open("labels.pickle", "rb") as f:
        og_labels = pickle.load(f)
        labels = {v: k for k, v in og_labels.items()}

    eyes_labels = {"eyes_person_name": 1}
    with open("eyeslabels.pickle", 'rb') as f:
        og_labels = pickle.load(f)
        eyes_labels = {v: k for k, v in og_labels.items()}

    flag = 0;
    start = datetime.datetime.now()
    second_start = start.second
    minute_start = start.minute
    hour_start = start.hour
    c = hour_start * 3600 + minute_start * 60 + second_start
    while True:
        end = datetime.datetime.now()
        second_end = end.second
        minute_end = end.minute
        hour_end = end.hour
        b = hour_end * 3600 + minute_end * 60 + second_end
        ret, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(frame, scaleFactor=1.5, minNeighbors=5)
        eyes = eyes_cascade.detectMultiScale(frame)
        if flag == 0:
            if (b - c) != 15:
                for (x, y, w, h) in faces:
                    for (ex, ey, ew, eh) in eyes:
                        roi_gray = gray[y:y + h, x:x + w]  # (cord1-height,cord2-height)
                        capture_eyes = gray[ey:ey + eh, ex:ex + ew]
                        id_, conf = recognizer.predict(roi_gray)
                        temp, eyes_conf = eyes_recognizer.predict(capture_eyes)
                        print("eyes", eyes_conf)
                        print("conf", conf)
                        # print("1",flag)
                        if conf >= 20 and conf <= 70 and eyes_conf >= 90 and eyes_conf <= 170:

                            # print("2",flag)
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            name = (labels[id_])
                            print("name",name)
                            # print("name", upper_name)
                            if name == check:
                                flag = 1
                                # print("trung")
                    if flag == 1:
                        break
            else:
                flag = 2
                break
                # color = (255, 243, 153)
                # stroke = 2
                # cv2.putText(frame, name, (x, y), font, 1, color, stroke, cv2.LINE_AA)
                """color = (255, 0, 0)
                stroke = 2
                end_cord_x = x + w
                end_cord_y = y + h
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color, stroke)
                #cv2.rectangle(frame,(ex,ey),(ex+ew,ey+eh),color,stroke)
                imgencode = cv2.imencode('.jpg', frame)[1]
                stringData = imgencode.tostring()
                yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')"""
        else:
            break
    return flag
    del (camera)


# hiển thị video
def video_cam_recog(request):
    try:
        return StreamingHttpResponse(get_frame(), content_type='multipart/x-mixed-replace; boundary=frame')
    except:
        return "error"

def login_recog(check):
    camera = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier('I:\Program Files\Python\Lib\site-packages\cv2\data\haarcascade_frontalface_alt.xml')
    eyes_cascade = cv2.CascadeClassifier('I:\Program Files\Python\Lib\site-packages\cv2\data\haarcascade_eye.xml')

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trainer.yml")

    eyes_recognizer = cv2.face.LBPHFaceRecognizer_create()
    eyes_recognizer.read("eyes-trainner.yml")

    labels = {"person_name": 1}
    with open("labels.pickle", "rb") as f:
        og_labels = pickle.load(f)
        labels = {v: k for k, v in og_labels.items()}

    eyes_labels = {"eyes_person_name": 1}
    with open("eyeslabels.pickle", 'rb') as f:
        og_labels = pickle.load(f)
        eyes_labels = {v: k for k, v in og_labels.items()}

    flag = 0;
    start = datetime.datetime.now()
    second_start = start.second
    minute_start = start.minute
    hour_start = start.hour
    c = hour_start * 3600 + minute_start * 60 + second_start
    while True:
        end = datetime.datetime.now()
        second_end = end.second
        minute_end = end.minute
        hour_end = end.hour
        b = hour_end * 3600 + minute_end * 60 + second_end
        ret, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(frame, scaleFactor=1.5, minNeighbors=5)
        eyes = eyes_cascade.detectMultiScale(frame)
        if flag == 0:
            if (b - c) != 15:
                for (x, y, w, h) in faces:
                    for (ex, ey, ew, eh) in eyes:
                        roi_gray = gray[y:y + h, x:x + w]  # (cord1-height,cord2-height)
                        capture_eyes = gray[ey:ey + eh, ex:ex + ew]
                        id_, conf = recognizer.predict(roi_gray)
                        temp, eyes_conf = eyes_recognizer.predict(capture_eyes)
                        print("eyes", eyes_conf)
                        print("conf", conf)
                        # print("1",flag)
                        if conf >= 20 and conf <= 43 and eyes_conf >= 90 and eyes_conf <= 170:

                            # print("2",flag)
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            name = (labels[id_])
                            print("name",name)
                            # print("name", upper_name)
                            if name == check:
                                flag = 1
                                # print("trung")
                    if flag == 1:
                        break
            else:
                flag = 2
                break
                # color = (255, 243, 153)
                # stroke = 2
                # cv2.putText(frame, name, (x, y), font, 1, color, stroke, cv2.LINE_AA)
                color = (255, 0, 0)
                stroke = 2
                end_cord_x = x + w
                end_cord_y = y + h
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.rectangle(frame, (x, y), (end_cord_x, end_cord_y), color, stroke)
                #cv2.rectangle(frame,(ex,ey),(ex+ew,ey+eh),color,stroke)
                imgencode = cv2.imencode('.jpg', frame)[1]
                stringData = imgencode.tostring()
                yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n')
        else:
            break
    return flag
    del (camera)

"""def login_cam(request):
    try:
        return StreamingHttpResponse(camera_recognize(request.session['login']), content_type='multipart/x-mixed-replace; boundary=frame')
    except:
        return "error"""""


# ------------------Book------------------#

class input_book(LoginRequiredMixin,View):
    login_url='/admin/'
    def get(self, request):
        if request.user.is_authenticated:
            b = Sach()
            return render(request, 'cart/nhapsach.html', {'b': b, 'id_book': no.getsensordata()})
        else:
            return redirect('/admin/')

    def post(self, request):
        b = Sach(request.POST, request.FILES)
        if b.is_valid():
            im = b.save(commit=False)
            im.image_book = request.FILES['image_book']
            im.save()
            return render(request, 'cart/success.html')
        else:
            return render(request, 'cart/fail.html')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def detailbook(request, id):
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        detailbook = Book.objects.get(id=id)
        book = Book.objects.all()
        book1 = book.filter(active=True)
        book_filter = BookFilter(request.GET, queryset=book1)
        sl = book_filter.qs.count()
        if book_filter.data:
            Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                    'list_book1': Book.objects.all(),
                    'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
            return render(request, 'book/book.html', Data)
        return render(request, 'book/detailbook.html',
                      {'detailbook': detailbook, 'tenDG': user.ten_DG, 'form': book_filter.form,
                       'list_book1': Book.objects.all(),
                       'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')})
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')

"""cart={}
def addcart(request):
    if request.is_ajax():
        id=request.POST.get('id')
        bookDetail=Book.objects.get(id=id)
        if id in cart.keys():
            BookCart={
                'id_book':bookDetail.id_book,
                'name':bookDetail.title,
                'image':str(bookDetail.image_book.url),
            }
        else:
            BookCart = {
                'id_book': bookDetail.id_book,
                'name': bookDetail.title,
                'image': str(bookDetail.image_book.url),
            }
        cart[id]=BookCart
        request.session['cart']=cart
        cartInfo=request.session['cart']
        return render(request,'cart/addcart.html',{'cart':cartInfo})"""

"""class yourcart(View):
    def get(self,request):
        return render(request,'cart/yourcart.html')

    def post(self,request):
        cartInfo=request.session['cart']
        flag=0
        for key,value in cartInfo.items():
            store_cart=Cart(id_user=id_user,id_bor=value['id_book'])
            store_cart.save()
            bookDetail = Book.objects.get(id=key)
            bookDetail.active=False
            bookDetail.save()
            no.sendidbook(value['id_book'])
            flag=flag+1
        if(flag != 0):
            return HttpResponse('success')
        else:
            return HttpResponse('mươn ko thành công')
"""
timeout_1 = 0


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book(request):
    flag1 = 0
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        book = Book.objects.all()
        book1 = book.filter(active=True)
        book2=book1.filter(dup=False)
        print("dup",book2)
        print("id",book2[0].id_book)
        dupes_1=Book.objects.values('title').annotate(title_count=Count('title')).exclude(title_count=1)
        print("dupes_1",dupes_1)
        book_filter = BookFilter(request.GET, queryset=book2)
        book_filter1 = BookFilter(request.GET, queryset=book1)

        sl = book_filter1.qs.count()
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all(),
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book_rate(request):
    flag1 = 0
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        book = Book.objects.all()
        book1 = book.filter(active=True)
        book2=book.filter(dup=False)

        book_filter = BookFilter(request.GET, queryset=book2)
        # sl = book1.aggregate(Count('id'))
        sl = book_filter.qs.count()
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all()
            , 'list_rate': book2.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book_rate.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book_bor(request):
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        book = Book.objects.all()
        book1 = book.filter(active=True)
        book_filter = BookFilter(request.GET, queryset=book1)
        # sl = book1.aggregate(Count('id'))
        sl = book_filter.qs.count()
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all(),
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book_bor.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book_cate1(request):
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        get_cate = Book.objects.filter(category=Category_Book.objects.get(title="Giáo trình"))
        get_cate2 = get_cate.filter(active=True)
        get_cate3=get_cate2.filter(dup=False)
        book_filter = BookFilter(request.GET, queryset=get_cate3)
        book_filter1=BookFilter(request.GET,queryset=get_cate2)
        sl = book_filter1.qs.count()
        # sl=get_cate2.aggregate(Count('id'))
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all(),
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book_cate1.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book_cate2(request):
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        get_cate = Book.objects.filter(category=Category_Book.objects.get(title="Văn học nghệ thuật"))
        get_cate2 = get_cate.filter(active=True)
        get_cate3 = get_cate2.filter(dup=False)
        book_filter = BookFilter(request.GET, queryset=get_cate3)
        book_filter1 = BookFilter(request.GET, queryset=get_cate2)
        sl = book_filter1.qs.count()
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all(),
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book_cate2.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book_cate3(request):
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        get_cate = Book.objects.filter(category=Category_Book.objects.get(title="Tâm lý, tâm linh, tôn giáo"))
        get_cate2 = get_cate.filter(active=True)
        get_cate3 = get_cate2.filter(dup=False)
        book_filter = BookFilter(request.GET, queryset=get_cate3)
        book_filter1 = BookFilter(request.GET, queryset=get_cate2)
        sl = book_filter1.qs.count()
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all(),
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book_cate3.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book_cate4(request):
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        get_cate = Book.objects.filter(category=Category_Book.objects.get(title="Truyện, tiểu thuyết"))
        get_cate2 = get_cate.filter(active=True)
        get_cate3 = get_cate2.filter(dup=False)
        book_filter = BookFilter(request.GET, queryset=get_cate3)
        book_filter1 = BookFilter(request.GET, queryset=get_cate2)
        sl = book_filter1.qs.count()
        # sl=get_cate2.aggregate(Count('id'))
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all(),
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book_cate4.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book_cate5(request):
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        get_cate = Book.objects.filter(category=Category_Book.objects.get(title="Văn hóa xã hội - Lịch sử"))
        get_cate2 = get_cate.filter(active=True)
        get_cate3 = get_cate2.filter(dup=False)
        book_filter = BookFilter(request.GET, queryset=get_cate3)
        book_filter1 = BookFilter(request.GET, queryset=get_cate2)
        sl = book_filter1.qs.count()
        # sl=get_cate2.aggregate(Count('id'))
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all(),
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book_cate5.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book_cate6(request):
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        get_cate = Book.objects.filter(category=Category_Book.objects.get(title="Khoa học công nghệ - Kinh tế"))
        get_cate2 = get_cate.filter(active=True)
        get_cate3 = get_cate2.filter(dup=False)
        book_filter = BookFilter(request.GET, queryset=get_cate3)
        book_filter1 = BookFilter(request.GET, queryset=get_cate2)
        sl = book_filter1.qs.count()
        # sl=get_cate2.aggregate(Count('id'))
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all(),
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book_cate6.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def book_cate7(request):
    if request.session.has_key('login'):
        user = DocGia.objects.get(id_DG=request.session['login'])
        get_cate = Book.objects.filter(category=Category_Book.objects.get(title="Chính trị - Pháp luật"))
        get_cate2 = get_cate.filter(active=True)
        get_cate3 = get_cate2.filter(dup=False)
        book_filter = BookFilter(request.GET, queryset=get_cate3)
        book_filter1 = BookFilter(request.GET, queryset=get_cate2)
        sl = book_filter1.qs.count()
        # sl=get_cate2.aggregate(Count('id'))
        Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                'list_book1': Book.objects.all(),
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        return render(request, 'book/book_cate7.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


a = ""
b = ""
u = ""


# Scan id
def scan_book(request):
    if request.is_ajax():
        global u
        try:
            u = no.getidbook()
        except:
            print("fail")
            pass
        if u == "":
            context = {'tag_book': u}
            return JsonResponse(context)
        elif len(u) == 14:
            context = {'tag_book': u}
            return JsonResponse(context)
        else:
            u = ""
            context = {'tag_book': u}
            return JsonResponse(context)
    else:
        return HttpResponse("This route only handles AJAX requests")

def get_book(request):
    if request.is_ajax:
        id_book=request.POST.get('id_book')
        try:
            Book.objects.get(id_book=id_book)
            infor_book=Book.objects.get(id_book=id_book)
            try:
                check_cart=Cart.objects.get(id_user=request.session['login'])
                if check_cart.id_bor1 != "" and check_cart.id_bor2 != "" and check_cart.id_bor3 != "":
                    context = {'infor_book': 3}
                    return JsonResponse(context)
            except ObjectDoesNotExist:
                pass
            if infor_book.active == False:
                context={'infor_book':1}
                return JsonResponse(context)

            else:
                context={'infor_book':infor_book.title}
                return JsonResponse(context)
        except ObjectDoesNotExist:
            context={'infor_book':2}
            return JsonResponse(context)
    else:
        return HttpResponse("This route only handles AJAX requests")


class bor_book(View):
    @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
    def get(self, request):
        if request.session.has_key('login'):

            user = DocGia.objects.get(id_DG=request.session['login'])
            book = Book.objects.all()
            book1 = book.filter(active=True)
            book_filter = BookFilter(request.GET, queryset=book1)
            sl = book_filter.qs.count()
            if book_filter.data:
                Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                        'list_book1': Book.objects.all(),
                        'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
                return render(request, 'book/book.html', Data)
            return render(request, 'muontra/muonsach.html',
                          {'tenDG': user.ten_DG, 'list_book1': Book.objects.all(), 'form': book_filter.form,
                           'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')})
        else:
            messages.error(request, "Bạn chưa đăng nhập")
            return redirect('/login_new/')

    def post(self, request):
        flag = 0
        id_book = request.POST.get('id_book')
        bookDetail = Book.objects.get(id_book=id_book)

        try:
            Cart.objects.get(id_user=request.session['login'])
            flag = 1
        except ObjectDoesNotExist:
            flag = 0
        if flag == 1:
            check_cart = Cart.objects.get(id_user=request.session['login'])
            flag_book = 0



            if check_cart.id_bor1 == "":
                check_id = Check_book(id_bor=id_book)
                check_id.save()
                bookDetail.active = False
                if bookDetail.dup == False:
                    bookDetail.dup = True
                bookDetail.save()
                check_cart.id_bor1 = id_book
                check_cart.create1 = datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=7)
                check_cart.save()
                flag_book = 0
                book = Book.objects.all()
                book1 = book.filter(title=bookDetail.title)
                try:
                    book2=book1.filter(active=True)
                    book_filter3 = BookFilter(request.GET, queryset=book1)
                    book_filter4=BookFilter(request.GET,queryset=book2)
                    num1=book_filter4.qs.count()
                    num = book_filter3.qs.count()
                    for i in range(0, int(num)):
                        book3 = Book.objects.get(id_book=book1[i].id_book)
                        book3.sl = book3.sl - 1
                        book3.save()

                    for j in range(0,int(num1)):
                        book5=Book.objects.get(id_book=book2[j].id_book)
                        if book5.dup == False:
                            flag_book=1
                    if flag_book == 0 and int(num1) > 0:
                        book4 = Book.objects.get(id_book=book2[0].id_book)
                        book4.dup = False
                        book4.save()
                except ObjectDoesNotExist:
                    pass

                messages.success(request, "Bạn đã mượn sách thành công")
                return redirect('/muonsach/')

            elif check_cart.id_bor2 == "":

                check_id = Check_book(id_bor=id_book)
                check_id.save()
                bookDetail.active = False
                if bookDetail.dup == False:
                    bookDetail.dup = True
                bookDetail.save()
                check_cart.id_bor2 = id_book
                check_cart.create2 = datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=7)
                check_cart.save()
                flag_book = 0
                book = Book.objects.all()
                book1 = book.filter(title=bookDetail.title)
                try:
                    book2=book1.filter(active=True)

                    book_filter3 = BookFilter(request.GET, queryset=book1)
                    book_filter4 = BookFilter(request.GET, queryset=book2)
                    num1 = book_filter4.qs.count()
                    num = book_filter3.qs.count()
                    for i in range(0, int(num)):
                        book3 = Book.objects.get(id_book=book1[i].id_book)
                        book3.sl = book3.sl - 1
                        book3.save()
                    for j in range(0, int(num1)):
                        book5 = Book.objects.get(id_book=book2[j].id_book)
                        if book5.dup == False:
                            flag_book = 1
                    if flag_book == 0 and int(num1) > 0:
                        book4 = Book.objects.get(id_book=book2[0].id_book)
                        book4.dup = False
                        book4.save()
                except ObjectDoesNotExist:
                    pass
                messages.success(request, "Bạn đã mượn sách thành công")
                return redirect('/muonsach/')

            elif check_cart.id_bor3 == "":
                check_id = Check_book(id_bor=id_book)
                check_id.save()
                bookDetail.active = False
                if bookDetail.dup == False:
                    bookDetail.dup = True
                bookDetail.save()
                check_cart.id_bor3 = id_book
                check_cart.create3 = datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=7)
                check_cart.save()
                book = Book.objects.all()
                book1 = book.filter(title=bookDetail.title)
                flag_book = 0
                try:
                    book2=book1.filter(active=True)
                    book_filter3 = BookFilter(request.GET, queryset=book1)
                    book_filter4 = BookFilter(request.GET, queryset=book2)
                    num1 = book_filter4.qs.count()
                    num = book_filter3.qs.count()
                    for i in range(0, int(num)):
                        book3 = Book.objects.get(id_book=book1[i].id_book)
                        book3.sl = book3.sl - 1
                        book3.save()
                    for j in range(0,int(num1)):
                        book5=Book.objects.get(id_book=book2[j].id_book)
                        if book5.dup == False:
                            flag_book=1
                    if flag_book == 0 and int(num1) > 0:
                        book4 = Book.objects.get(id_book=book2[0].id_book)
                        book4.dup = False
                        book4.save()
                except ObjectDoesNotExist:
                    pass

                messages.success(request, "Bạn đã mượn sách thành công")
                return redirect('/muonsach/')




        elif flag == 0:
            check_id = Check_book(id_bor=id_book)
            check_id.save()
            check_cart=Cart(id_user=request.session['login'])
            check_cart.id_bor1 = id_book
            check_cart.create1 = datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=7)
            check_cart.save()
            bookDetail.active = False
            if bookDetail.dup==False:
                bookDetail.dup=True
            bookDetail.save()
            book = Book.objects.all()
            book1 = book.filter(title=bookDetail.title)
            flag_book=0
            try:
                book2 = book1.filter(active=True)
                book_filter3 = BookFilter(request.GET, queryset=book1)
                book_filter4 = BookFilter(request.GET, queryset=book2)
                num1 = book_filter4.qs.count()
                num=book_filter3.qs.count()

                for i in range(0,int(num)):

                    book3=Book.objects.get(id_book=book1[i].id_book)
                    book3.sl=book3.sl-1
                    book3.save()
                for j in range(0, int(num1)):
                    book5 = Book.objects.get(id_book=book2[j].id_book)
                    if book5.dup == False:
                        flag_book = 1
                if flag_book == 0 and int(num1) > 0:
                    book4 = Book.objects.get(id_book=book2[0].id_book)
                    book4.dup = False
                    book4.save()

            except ObjectDoesNotExist:
                pass
            messages.success(request, "Bạn đã mượn sách thành công")
            return redirect('/muonsach/')


temp1 = ""


def res_book(request):
    if request.is_ajax:
        t1 = 0
        id_book=request.POST.get('ret_book')
        user=DocGia.objects.get(id_DG=request.session['login'])
        sum_money = 0
        time_pre = datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=7)

        try:
            Book.objects.get(id_book=id_book)
            infor_book=Book.objects.get(id_book=id_book)
            try:
                check_cart=Cart.objects.get(id_user=request.session['login'])
            except ObjectDoesNotExist:
                context ={'res_book':2}
                return JsonResponse(context)

            if infor_book.active == True:
                context={'res_book':3}
                return JsonResponse(context)

            if check_cart.id_bor1 != id_book and check_cart.id_bor2 != id_book and check_cart.id_bor3 != id_book :
                context = {'res_book':4}
                return JsonResponse(context)

            elif check_cart.id_bor1 == id_book:
                time_cre1 = check_cart.create1
                t1 = time_pre - time_cre1
                sum_money=no.day(t1.days)
                if 0 <= user.money_user < sum_money:
                    context = {'res_book': infor_book.title, 'day': t1.days, 'sum': sum_money,'error':5}
                    return JsonResponse(context)
                context={'res_book':infor_book.title,'day':t1.days,'sum':sum_money}
                return JsonResponse(context)

            elif check_cart.id_bor2 == id_book:
                time_cre1 = check_cart.create2
                t1 = time_pre - time_cre1
                sum_money = no.day(t1.days)
                if 0 <= user.money_user < sum_money:
                    context = {'res_book': infor_book.title, 'day': t1.days, 'sum': sum_money,'error':5}
                    return JsonResponse(context)
                context = {'res_book': infor_book.title, 'day': t1.days, 'sum': sum_money}
                return JsonResponse(context)

            else:
                time_cre1 = check_cart.create3
                t1 = time_pre - time_cre1
                sum_money = no.day(t1.days)
                if 0 <= user.money_user < sum_money:
                    context = {'res_book': infor_book.title, 'day': t1.days, 'sum': sum_money,'error':5}
                    return JsonResponse(context)
                context = {'res_book': infor_book.title, 'day': t1.days, 'sum': sum_money}
                return JsonResponse(context)
        except ObjectDoesNotExist:
            context={'res_book':1}
            return JsonResponse(context)
    else:
        return HttpResponse("This route only handles AJAX requests")

class ret_book(View):
    @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
    def get(self, request):
        flag1 = 0
        if request.session.has_key('login'):
            user = DocGia.objects.get(id_DG=request.session['login'])
            book = Book.objects.all()
            book1 = book.filter(active=True)
            book_filter = BookFilter(request.GET, queryset=book1)
            sl = book_filter.qs.count()
            if book_filter.data:
                Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                        'list_book1': Book.objects.all(),
                        'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
                return render(request, 'book/book.html', Data)
            return render(request, 'muontra/trasach.html',
                          {'tenDG': user.ten_DG, 'list_book1': Book.objects.all(), 'form': book_filter.form,
                           'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')})
        else:
            messages.error(request, "Bạn chưa đăng nhập")
            return redirect('/login_new/')

    def post(self, request):
        global temp1
        id_book = request.POST.get('ret_book')
        temp1=id_book
        user = DocGia.objects.get(id_DG=request.session['login'])
        book_detail=Book.objects.get(id_book=id_book)
        t1=0
        sum_money = 0
        time_pre = datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=7)
        check_cart=Cart.objects.get(id_user=request.session['login'])
        if check_cart.id_bor1 == id_book:
            check_cart.id_bor1 = ""
            check_cart.save()
            book_detail.active=True
            book_detail.save()
            Check_book.objects.filter(id_bor=id_book).delete()
            time_cre1 = check_cart.create1
            t1 = time_pre - time_cre1
            sum_money = no.day(t1.days)
            user.money_user=user.money_user-sum_money
            user.save()
            book = Book.objects.all()
            book1 = book.filter(title=book_detail.title)
            temp_filter = 0
            try:
                book_filter3 = BookFilter(request.GET, queryset=book1)
                book2=book1.filter(active=True)
                book_filter4 = BookFilter(request.GET, queryset=book2)
                num1=book_filter4.qs.count()
                num = book_filter3.qs.count()
                for i in range(0, int(num)):
                    book3 = Book.objects.get(id_book=book1[i].id_book)
                    book3.sl = book3.sl + 1
                    book3.save()
                for j in range(0,int(num1)):
                    book5 = Book.objects.get(id_book=book2[j].id_book)
                    if book5.dup == False:
                        print("1",book5.dup)
                        temp_filter= 1
                if temp_filter==0:
                    book4=Book.objects.get(id_book=book2[0].id_book)
                    book4.dup=False
                    book4.save()
            except ObjectDoesNotExist:
                pass
            if check_cart.id_bor1 == "" and check_cart.id_bor2 == "" and check_cart.id_bor3 == "":
                Cart.objects.filter(id_user=request.session['login']).delete()
                messages.success(request, "Trả sách thành công")
                return redirect('/rate/')
            messages.success(request, "Trả sách thành công")
            return redirect('/rate/')

        if check_cart.id_bor2 == id_book:
            check_cart.id_bor2 = ""
            check_cart.save()
            book_detail.active=True
            book_detail.save()
            Check_book.objects.filter(id_bor=id_book).delete()
            time_cre1 = check_cart.create2
            t1 = time_pre - time_cre1
            sum_money = no.day(t1.days)
            user.money_user=user.money_user-sum_money
            user.save()
            book = Book.objects.all()
            book1 = book.filter(title=book_detail.title)
            temp_filter = 0
            try:
                book_filter3 = BookFilter(request.GET, queryset=book1)
                book2 = book1.filter(active=True)
                book_filter4 = BookFilter(request.GET, queryset=book2)
                num1 = book_filter4.qs.count()
                num = book_filter3.qs.count()
                for i in range(0, int(num)):
                    book3 = Book.objects.get(id_book=book1[i].id_book)
                    book3.sl = book3.sl + 1
                    book3.save()
                for j in range(0,int(num1)):
                    book5 = Book.objects.get(id_book=book2[j].id_book)
                    if book5.dup == False:
                        temp_filter= 1
                if temp_filter==0:
                    book4=Book.objects.get(id_book=book2[0].id_book)
                    book4.dup=False
                    book4.save()
            except ObjectDoesNotExist:
                pass
            if check_cart.id_bor1 == "" and check_cart.id_bor2 == "" and check_cart.id_bor3 == "":
                Cart.objects.filter(id_user=request.session['login']).delete()
                messages.success(request, "Trả sách thành công")
                return redirect('/rate/')
            messages.success(request, "Trả sách thành công")
            return redirect('/rate/')

        if check_cart.id_bor3 == id_book:
            check_cart.id_bor3 = ""
            check_cart.save()
            book_detail.active=True
            book_detail.save()
            Check_book.objects.filter(id_bor=id_book).delete()
            time_cre1 = check_cart.create3
            t1 = time_pre - time_cre1
            sum_money = no.day(t1.days)
            user.money_user=user.money_user-sum_money
            user.save()
            book = Book.objects.all()
            book1 = book.filter(title=book_detail.title)
            temp_filter = 0
            try:
                book_filter3 = BookFilter(request.GET, queryset=book1)
                book2 = book1.filter(active=True)
                book_filter4 = BookFilter(request.GET, queryset=book2)
                num1 = book_filter4.qs.count()
                num = book_filter3.qs.count()
                for i in range(0, int(num)):
                    book3 = Book.objects.get(id_book=book1[i].id_book)
                    book3.sl = book3.sl + 1
                    book3.save()
                for j in range(0,int(num1)):
                    book5 = Book.objects.get(id_book=book2[j].id_book)
                    if book5.dup == False:
                        temp_filter= 1
                if temp_filter==0:
                    book4=Book.objects.get(id_book=book2[0].id_book)
                    book4.dup=False
                    book4.save()
            except ObjectDoesNotExist:
                pass
            if check_cart.id_bor1 == "" and check_cart.id_bor2 == "" and check_cart.id_bor3 == "":
                Cart.objects.filter(id_user=request.session['login']).delete()
                messages.success(request, "Trả sách thành công")
                return redirect('/rate/')
            messages.success(request, "Trả sách thành công")
            return redirect('/rate/')

"""class thanhtoan(View):
    @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
    def get(self, request):
        if request.session.has_key('login'):
            user = DocGia.objects.get(id_DG=request.session['login'])
            book = Book.objects.all()
            book1 = book.filter(active=True)
            book_filter = BookFilter(request.GET, queryset=book1)
            sl = book_filter.qs.count()
            if book_filter.data:
                Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                        'list_book1': Book.objects.all(),
                        'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
                return render(request, 'book/book.html', Data)
        else:
            messages.error(request, "Bạn chưa đăng nhập")
            return redirect('/login_new/')

    def post(self, request):
        money = request.POST.get('tien')
        a = int(money)
        user = DocGia.objects.get(id_DG=id_user)
        if (user.money_user == 0 and a != 0):
            messages.error(request, "Tài khoản của bạn không đủ để thanh toán")
            book = Book.objects.all()
            book1 = book.filter(active=True)
            sl = book1.aggregate(Count('id'))
            return redirect('/trasach/')
        else:
            if (temp1 != ""):
                bookDetail = Book.objects.get(id_book=temp1)
                bookDetail.active = True
                bookDetail.save()
                Check_book.objects.filter(id_bor=temp1).delete()
                book_bor = Cart.objects.get(id_user=id_user)
                if (book_bor.id_bor1 == temp1):
                    book_bor.id_bor1 = ""
                    book_bor.save()

                elif (book_bor.id_bor2 == temp1):
                    book_bor.id_bor2 = ""
                    book_bor.save()

                elif (book_bor.id_bor3 == temp1):
                    book_bor.id_bor3 = ""
                    book_bor.save()

            if (temp2 != ""):
                bookDetail = Book.objects.get(id_book=temp2)
                bookDetail.active = True
                bookDetail.save()
                Check_book.objects.filter(id_bor=temp2).delete()
                book_bor = Cart.objects.get(id_user=id_user)
                if (book_bor.id_bor1 == temp2):
                    book_bor.id_bor1 = ""
                    book_bor.save()
                elif (book_bor.id_bor2 == temp2):
                    book_bor.id_bor2 = ""
                    book_bor.save()
                elif (book_bor.id_bor3 == temp2):
                    book_bor.id_bor3 = ""
                    book_bor.save()

            if (temp3 != ""):
                bookDetail = Book.objects.get(id_book=temp3)
                bookDetail.active = True
                bookDetail.save()
                Check_book.objects.filter(id_bor=temp3).delete()
                book_bor = Cart.objects.get(id_user=id_user)
                if (book_bor.id_bor1 == temp3):
                    book_bor.id_bor1 = ""
                    book_bor.save()
                elif (book_bor.id_bor2 == temp3):
                    book_bor.id_bor2 = ""
                    book_bor.save()
                elif (book_bor.id_bor3 == temp3):
                    book_bor.id_bor3 = ""
                    book_bor.save()

            check_cart = Cart.objects.get(id_user=id_user)
            if (check_cart.id_bor1 == "" and check_cart.id_bor2 == "" and check_cart.id_bor3 == ""):
                Cart.objects.filter(id_user=id_user).delete()
            user.money_user = user.money_user - a
            user.save()
        messages.success(request, "Trả sách thành công")
        book = Book.objects.all()
        book1 = book.filter(active=True)
        sl = book1.aggregate(Count('id'))
        return redirect('/rate/')"""


d = ""


def check_book(request):
    if request.is_ajax():
        global d
        flag = 0
        no.socket_recv()
        print("d", d)

        context = {'id_book': d}
        return JsonResponse(context)
    else:
        return HttpResponse("This route only handles AJAX requests")


def testcheck(request):
    return render(request, 'check/check.html', {})


class contact(View):
    @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
    def get(self, request):
        if request.session.has_key('login'):
            q = Message()
            user = DocGia.objects.get(id_DG=request.session['login'])
            book = Book.objects.all()
            book1 = book.filter(active=True)
            book_filter = BookFilter(request.GET, queryset=book1)
            sl = book_filter.qs.count()
            if book_filter.data:
                Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                        'list_book1': Book.objects.all(),
                        'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
                return render(request, 'book/book.html', Data)
            return render(request, 'contact/contact.html',
                          {'form': book_filter.form, 'opi': q, 'tenDG': user.ten_DG, 'emailDG': user.email_DG,
                           'phone': user.phone})
        else:
            messages.error(request, "Bạn chưa đăng nhập")
            return redirect('/login_new/')

    def post(self, request):
        q = Message(request.POST)
        if q.is_valid():
            q.save()
            messages.success(request, "Cảm ơn bạn đã đóng góp ý kiến")
            return redirect('/book/')


@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def detailuser(request):
    if request.session.has_key('login'):
        book = Book.objects.all()
        user = DocGia.objects.get(id_DG=request.session['login'])
        try:
            check_cart = Cart.objects.get(id_user=request.session['login'])
        except ObjectDoesNotExist:
            book1 = book.filter(active=True)
            book_filter = BookFilter(request.GET, queryset=book1)
            sl = book_filter.qs.count()
            if book_filter.data:
                Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                        'list_book1': Book.objects.all(),
                        'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate'),'temp':0}
                return render(request, 'book/book.html', Data)
            name1 = ""
            name2 = ""
            name3 = ""
            Data = {'tenDG': user.ten_DG, 'form': book_filter.form, 'list_book1': Book.objects.all(), 'DG': user,
                    'book1': name1, 'book2': name2, 'book3': name3,'temp':0,
                    'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
            return render(request, 'login/detailuser.html', Data)
        book1 = book.filter(active=True)
        book_filter = BookFilter(request.GET, queryset=book1)
        sl = book_filter.qs.count()
        if book_filter.data:
            Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                    'list_book1': Book.objects.all(),'temp':0}
            return render(request, 'book/book.html', Data)
        name1 = ""
        name2 = ""
        name3 = ""
        m = 0
        n = 0
        p = 0
        x=""
        y=""
        z=""

        time_pre = datetime.datetime.now(timezone.utc) + datetime.timedelta(hours=7)
        try:
            book1 = Book.objects.get(id_book=check_cart.id_bor1)
            img1=book1.image_book
            x=img1
            name1 = book1.title
            time1 = check_cart.create1
            day1 = time_pre - time1
            m = day1.days
        except ObjectDoesNotExist:
            name1 = ""
        try:
            book2 = Book.objects.get(id_book=check_cart.id_bor2)
            img2=book2.image_book
            y=img2
            name2 = book2.title
            time2 = check_cart.create2
            day2 = time_pre - time2
            n = day2.days
        except ObjectDoesNotExist:
            name2 = ""

        try:
            book3 = Book.objects.get(id_book=check_cart.id_bor3)
            img3=book3.image_book
            z=img3
            name3 = book3.title
            time3 = check_cart.create3
            day3 = time_pre - time3
            p = day3.days
        except ObjectDoesNotExist:
            name3 = ""

        Data = {'tenDG': user.ten_DG, 'form': book_filter.form, 'list_book1': Book.objects.all(), 'DG': user,
                'book1': name1, 'book2': name2, 'book3': name3,
                'day1': m, 'day2': n, 'day3': p,'img1':x,'img2':y,'img3':z,'temp':1,
                'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
        print(4)
        return render(request, 'login/detailuser.html', Data)
    else:
        messages.error(request, "Bạn chưa đăng nhập")
        return redirect('/login_new/')


class rating(View):
    @cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
    def get(self, request):
        if request.session.has_key('login'):
            user = DocGia.objects.get(id_DG=request.session['login'])
            book = Book.objects.all()
            book1 = book.filter(active=True)
            book_filter = BookFilter(request.GET, queryset=book1)
            sl = book_filter.qs.count()
            name_book1 = ""

            if (temp1 != ""):
                temp_book1 = Book.objects.get(id_book=temp1)
                name_book1 = temp_book1.title
            if book_filter.data:
                Data = {'form': book_filter.form, 'list_book': book_filter.qs, 'sl': sl, 'tenDG': user.ten_DG,
                        'list_book1': Book.objects.all(),
                        'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')}
                return render(request, 'book/book.html', Data)
            else:
                return render(request, 'rate/rate.html',
                              {'name_book1': name_book1, 'form': book_filter.form, 'tenDG': user.ten_DG, 'list_book1': Book.objects.all(),
                               'list_rate': Book.objects.filter(ave_rate__gte=4).order_by('-ave_rate')})
        else:
            messages.error(request, "Bạn chưa đăng nhập")
            return redirect('/login_new/')

    def post(self, request):
        global temp1
        temp1 = ""

        try:
            star1 = request.POST.get('star')
            if star1 is not None:
                book = Book.objects.get(id_book=temp1)
                book.rate = book.rate + int(star1)
                book.vote = book.vote + 1
                book.ave_rate = book.rate // book.vote
                book.save()
        except ObjectDoesNotExist:
            star1 = 0
        print(star1)
        messages.success(request, "Cảm ơn bạn đã đánh giá")
        return redirect("/book/")

class Register_id(View):
    def get(self,request):
        try:
            del request.session['login']
        except KeyError:
            pass
        global id_regis
        id_re = id_regis
        id_regis = ""
        print("id_re", id_re)
        path = "./image_temp/"
        dics = os.listdir(path)
        if id_re != "":
            try:
                for dic in dics:
                    if dic == id_re:
                        shutil.rmtree('./image_temp/' + dic)
                        return render(request, 'login/register_id.html')
                return render(request, 'login/register_id.html')

            except OSError:
                return render(request, 'login/register_id.html')

        else:
            return render(request, 'login/register_id.html')

    def post(self,request):
        global id_regis
        id_regis = request.POST.get('id_DG')
        print("id_regis",id_regis)
        try:
            ID_DocGia.objects.get(Id_Docgia=id_regis)
            try:
                DocGia.objects.get(id_DG=id_regis)
                messages.error(request, "ID đã tồn tại")
                return redirect("/")
            except ObjectDoesNotExist:
                return redirect('/register_infor/')
        except ObjectDoesNotExist:
            messages.error(request, "ID không hợp lệ")
            return redirect("/")


id_DG =""
HoTen =""
Email=""
CMND=""
Phone =""

class Register_infor(View):
    def get(self,request):
        if id_regis == "":
            messages.error(request,"chưa scan id")
            return redirect('/')
        return render(request,'login/register_infor.html',{'id_card':id_regis})

    def post(self,request):
        global id_DG, HoTen, Email, CMND, Phone
        id_DG = request.POST.get('id_DG')
        HoTen = request.POST.get('HoTen')
        Email = request.POST.get('Email')
        CMND = request.POST.get('CMND')
        Phone = request.POST.get('Phone')

        return redirect('/register_image/')

def check_Image(request):
    global check_image
    if request.is_ajax():
        context={'image':check_image}

        check_image=0
        return JsonResponse(context)
    else:
        return HttpResponse("This route only handles AJAX requests")


class Register_image(View):
    def get(self,request):
        if id_regis == "":
            messages.error(request,"chưa scan id")
            return redirect('/')
        return render(request, 'login/register_image.html')

    def post(self,request):
        global id_regis
        q = DocGia(id_DG=id_DG, ten_DG=HoTen, email_DG=Email, CMND=CMND, phone=Phone)
        q.save()
        path = "./Image/" + id_regis + '/'
        dest = "./image_book/image_user/"
        dest1 = "/image_user/"
        path1 = "./image_temp/"
        dest2 = "./Image/"
        shutil.move(path1 + id_regis, dest2)
        image = os.listdir(path)
        print(image[0])
        shutil.copy2(path + image[0], dest)
        im = DocGia.objects.get(id_DG=id_regis)
        im.image_user = dest1 + image[0]
        im.save()
        face_training.train()
        face_training.eye_train()
        global id_ne
        id_ne = ""
        id_regis=""
        messages.success(request, "Tài khoản được tạo thành công")
        return redirect('/login_new/')

id_cam=""
class Login_New(View):
    def get(self,request):
        try:
            del request.session['login']
        except KeyError:
            pass
        return render(request,'login/login_new.html')

    def post(self,request):
        id_check = request.POST.get('id_DG')
        request.session['login'] = id_check
        try:
            DocGia.objects.get(id_DG=id_check)
            try:
                c = camera_recognize(id_check)
                if (c == 1):
                    id_user = id_check
                    user = DocGia.objects.get(id_DG=id_user)
                    book = Book.objects.all()
                    book1 = book.filter(active=True)
                    sl = book1.aggregate(Count('id'))
                    Data = {'list_book': Book.objects.all(), 'sl': sl, 'tenDG': user.ten_DG}
                    return redirect('/book/')
                else:
                    messages.error(request, "Khuôn mặt không khớp")
                    return render(request, 'login/login_new.html')
            except:
                return "error"
        except ObjectDoesNotExist:
            messages.error(request, "ID chưa được đăng kí")
            return redirect('/login_new/')


