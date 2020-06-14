import os
import numpy as np
import cv2
import pickle
from PIL import Image

def train():
	BASE_DIR=os.path.dirname(os.path.abspath(__file__))
	image_dir=os.path.join(BASE_DIR,"I:\Đồ án\ThuVienThongMinh\Image")
	face_cascade=cv2.CascadeClassifier('I:\Program Files\Python\Lib\site-packages\cv2\data\haarcascade_frontalface_alt2.xml')
	recognizer=cv2.face.LBPHFaceRecognizer_create()
	current_id=0
	label_ids={}
	y_labels=[]
	x_train = []

	for root,dirs,files in os.walk(image_dir):
		for file in files:
			if file.endswith("png") or file.endswith("jpg"):
				path =os.path.join(root,file)
				label=os.path.basename(root).replace(" ","-").lower()
				print("trung",label, path)
				if not label in label_ids:
					label_ids[label] =current_id
					current_id+=1
				id_=label_ids[label]
				print("id",label_ids)
				pil_image=Image.open(path).convert("L")
				print("pil",pil_image)
				image_array=np.array(pil_image,"uint8")
				print(image_array)
				faces =face_cascade.detectMultiScale(image_array,minNeighbors=5)

				for (x,y,w,h) in faces:
					roi=image_array[y:y+h,x:x+w]
					x_train.append(roi)
					y_labels.append(id_)

#rint(x_train)
#print(y_labels)
	with open("labels.pickle","wb") as f:
		pickle.dump(label_ids,f)

	recognizer.train(x_train,np.array(y_labels))
	recognizer.save("trainer.yml")


def eye_train():
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	image_dir=os.path.join(BASE_DIR,"I:\Đồ án\ThuVienThongMinh\Image")

	eyes_cascade = cv2.CascadeClassifier('I:\Program Files\Python\Lib\site-packages\cv2\data\haarcascade_eye.xml')
	recognizer = cv2.face.LBPHFaceRecognizer_create()

	current_id = 0
	eyes_label_ids = {}
	y_labels = []
	x_train = []
	for root, dirs, files in os.walk(image_dir):
		for file in files:
			if file.endswith("png") or file.endswith("jpg"):
				path = os.path.join(root, file)
				label = os.path.basename(root).replace(" ", "-").lower()

				# print(label, path) #in tên của file và link của hình ảnh
				if not label in eyes_label_ids:
					eyes_label_ids[label] = current_id
					current_id += 1
				id_ = eyes_label_ids[label]
				pil_image = Image.open(path).convert("L")  # Chuyển image sang màu xám
				image_array = np.array(pil_image, "uint8")  # Chuyển hình ảnh thành ma trận số

				eyes = eyes_cascade.detectMultiScale(image_array)
				for (ex, ey, eh, ew) in eyes:
					capture_eyes = image_array[ey:ey + eh, ex:ex + ew]
					x_train.append(capture_eyes)
					y_labels.append(id_)

	with open("eyeslabels.pickle", 'wb') as f:
		pickle.dump(eyes_label_ids, f)

	recognizer.train(x_train, np.array(y_labels))
	recognizer.save("eyes-trainner.yml")
