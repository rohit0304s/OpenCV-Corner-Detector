from tkinter import *
import tkinter as tk
import tkinter.messagebox
import tkinter.font as font
from tkinter import filedialog
from PIL import ImageTk, Image
import os.path
import cv2
import numpy as np
import math

filename=""
original_image=np.zeros((),np.uint8)
copy_image=np.zeros((),np.uint8)
corner_detection=['Single Object','Multiple Object']
counter=0

def select_pic():
    global original_image
    global copy_image
    global filename
    cv2.destroyAllWindows()
    filename=""
    filename = filedialog.askopenfilename(initialdir = 'E:\\',title = 'Select an Image',filetypes = (('JPG','*.jpg'),('All files','*.*')))
    print(filename)
    original_image=cv2.imread(filename)
    copy_image=original_image.copy()
    cv2.imshow('Image',original_image)
    cv2.waitKey(20)

    
def save_current():
    global copy_image
    name = ''
    name = filedialog.asksaveasfilename (initialdir = 'E:\\', title = 'Save File', filetypes = (('JPG', '*.jpg'), ('All files','*.*')))
    print (name)
    response=tk.messagebox.showinfo("Saved","Image saved successfully")

    if name != '':
        cv2.imwrite (name, copy_image)

def about_():
    top=Toplevel()
    top.wm_title("About this Application")
    top.minsize(200,200)
    top.geometry("300x300")
    text=Text(top,bg='white')
    text.insert('2.0','This is a GUI Application to detect sharp corners and Movability score. It uses OpenCV functions to detect sharp corners and Movability score based on its area.\nPlease click on Instruction on menubar to get Instructions')
    text.place(relx = 0.05,rely = 0.1,relwidth =0.9,relheight =0.6)
    Exit=Button(top,text="Exit",fg="black",justify=CENTER,bg="coral",cursor="hand2",width=10,height=2,padx=1,pady=1)
    Exit.place(x=100,y=230)

def _instruction_():
    top=Toplevel()
    top.wm_title("About this Application")
    top.minsize(200,200)
    top.geometry("300x300")
    text=Text(top,bg='white')
    text.insert('2.0',' Following are the instruction:\n1. Select the Image by clicking on (Select Image) button\n2. Select the corner detection method \n3. Get the Movability score ')
    text.place(relx = 0.05,rely = 0.1,relwidth =0.9,relheight =0.6)
    Exit=Button(top,text="Exit",fg="black",justify=CENTER,bg="coral",cursor="hand2",width=10,height=2,padx=1,pady=1)
    Exit.place(x=100,y=230)

def get_movability():
    global filename
    global copy_image
    if os.path.exists(filename):
        h=copy_image.shape[0]
        w=copy_image.shape[1]
        a=h*w
        print(a)
        gray=cv2.cvtColor(copy_image,cv2.COLOR_BGR2GRAY)
        blurred=cv2.GaussianBlur(gray,(3,3),0)
        canny=cv2.Canny(blurred,120,255,1)
        kernel=np.ones((5,5),np.uint8)
        dilate=cv2.dilate(canny,kernel,iterations=1)
        cnts,h=cv2.findContours(dilate,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        areas=[cv2.contourArea(c) for c in cnts]
        area=np.sort(areas)
        print(area)
        n=len(area)
        for c in cnts:
            x,y,w,h=cv2.boundingRect(c)
            cv2.rectangle(copy_image,(x,y),(x+w,y+h),(36,255,12),2)
            if cv2.contourArea(c)<area[n//3]:
                cv2.putText(copy_image,'High',(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
            elif cv2.contourArea(c)>(area[2*n//3]):
                cv2.putText(copy_image,'Low',(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
            else:
                cv2.putText(copy_image,'Medium',(x,y),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),1)
        cv2.imshow('Movability',copy_image)
        cv2.waitKey(20)

    else:
        response=tk.messagebox.showinfo("Alert","Please select the image\n Click on Select Image")
    
def callback(*args):
    global filename
    global copy_image,corner_detection
    option=variable.get()
    print("You selected "+str(variable.get()))
    if os.path.exists(filename):
        img=cv2.imread(filename)
        if option==corner_detection[0]:
            min_dist=[]
            final_points=[]
            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            ret,thresh=cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
            dilate=cv2.dilate(thresh,np.ones((5,5)))
            blur=cv2.medianBlur(thresh,11)
            canny=cv2.Canny(dilate,100,255)
            
            contours,hierarchy=cv2.findContours(canny,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            areas=[cv2.contourArea(c) for c in contours]
            max_index=np.argmax(areas)
            max_contour_area=contours[max_index]
            
            perimeter=cv2.arcLength(max_contour_area,True)
            ROI=cv2.approxPolyDP(max_contour_area,0.01*perimeter,True)
            
            corners=cv2.goodFeaturesToTrack(gray,25,0.05,10)
            corners=np.int0(corners)
            for i in ROI[:,0]:
                for j in corners[:,0]:
                    distance=math.sqrt((i[0]-j[0])**2 +(i[1]-j[1])**2)
                    if distance<12:
                        min_dist.append(j)

            Hull=cv2.convexHull(max_contour_area)

            for i in Hull[:,0]:
                for j in min_dist:
                    distance=math.sqrt((i[0]-j[0])**2 +(i[1]-j[1])**2)
                    if distance<15:
                        final_points.append(j)

            print(final_points)
            for x,y in final_points:
                cv2.circle(copy_image,(x,y),3,(0,0,255),-1)

            cv2.imshow('Corners',copy_image)
            cv2.waitKey(10)
        
        elif option==corner_detection[1]:

            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            blur=cv2.GaussianBlur(gray,(5,5),0)
            edge=cv2.Canny(blur,50,150,apertureSize=3)

            h,w=edge.shape[:2]
            mask=np.zeros((h+2,w+2),np.uint8)
            
            cv2.floodFill(edge,mask,(0,0),123)
            floodfill=edge.copy()
            bg=np.zeros_like(edge)
            bg[edge==123]=255
            bg=cv2.blur(bg,(3,3))
            edge=cv2.Canny(bg,50,150,apertureSize=3)

            harris_points=[]
            hull=[]
            a=[]
            hull_points=[]
            contour_points=[]
            final_ponts=[]
            
            gray = np.float32(gray)
            dst = cv2.cornerHarris(gray,5,3,0.04)
            ret, dst = cv2.threshold(dst,0.1*dst.max(),255,0)
            dst = np.uint8(dst)
            ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
            
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
            corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)
            
            for i in range(1, len(corners)):
                harris_points.append(corners[i])#Get the harris point list(Its in float form)
                
            contours,hierarchy=cv2.findContours(edge,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            for i in range(len(contours)):
                hull.append(cv2.convexHull(contours[i], False))#Getting contur region and hull_points list

            for i in range(0,len(hull)):
                a=hull[i]
                b=a[:,0]
                for j in range(0,len(b)):
                    hull_points.append(b[j])

    #Distance theoram
            for i in range(0,len(hull_points)):
                for j in range(0,len(harris_points)):
                    a=hull_points[i]
                    b=harris_points[j]
                    distance=math.sqrt((a[0]-b[0])**2 +(a[1]-b[1])**2)
                    if distance<2:
                        final_ponts.append(b)
                        
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            blur=cv2.GaussianBlur(gray,(25,25),2)
            ret, thresh = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
            x, y, w, h = cv2.boundingRect(thresh)           
            left = (x, np.argmax(thresh[:, x]))              
            right = (x+w-1, np.argmax(thresh[:, x+w-1]))     
            top = (np.argmax(thresh[y, :]), y)               
            bottom = (np.argmax(thresh[y+h-1, :]), y+h-1)    
            
            cv2.circle(copy_image, left, 3, (0, 0, 255), -1)
            cv2.circle(copy_image, right, 3, (0, 0, 255), -1)
            cv2.circle(copy_image, top, 3, (0, 0, 255), -1)
            cv2.circle(copy_image, bottom, 3, (0, 0, 255), -1)
            
            dilate=cv2.dilate(thresh,np.ones((5,5)))
            canny=cv2.Canny(dilate,100,255)
            contours,hierarchy=cv2.findContours(canny,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            x,y=0,0

            for cnt in contours:
                approx=cv2.approxPolyDP(cnt,0.009*cv2.arcLength(cnt,True),True)
                n=approx.ravel()
                i=0
                for j in n:
                    if(i%2==0):
                        x=n[i]
                        y=n[i+1]
                        contour_points.append([x,y])
                    i+=1

            get_points=[]
            for i in final_ponts:
                for j in contour_points:
                    distance=math.sqrt((i[0]-j[0])**2 +(i[1]-j[1])**2)
                    if distance<4:
                        get_points.append(j)
    #Get circles
            for x,y in get_points:
                cv2.circle(copy_image,(x,y),3,(0,0,255),-1)

            print('Multiple corner detction done')
            cv2.imshow('Frame',copy_image)
            cv2.waitKey(20)

    else:
         response=tk.messagebox.showinfo("Alert","Please select image")





window=tk.Tk()
myFont = font.Font(family='Helvetica',size=13, weight='bold')

canvas=tk.Canvas(window,height=400,width=500,bg="LightCyan2")
canvas.pack()

menubar=Menu(canvas)
filemenu=Menu(menubar,tearoff=0)
filemenu.add_command(label="New Image",command=select_pic)
filemenu.add_command(label="Save-as",command=save_current)
filemenu.add_separator()

filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=about_)
helpmenu.add_command(label="Instructions", command=_instruction_)
menubar.add_cascade(label="help", menu=helpmenu)
window.config(menu=menubar)

label=Label(canvas,text='Edge Detection & Movability Score',bd=1,fg='black',font=myFont,bg='LightCyan2')
label.place(x=90,y=30)
btn_frame=tk.Frame(canvas,bg='LightCyan2')
btn_frame.place(bordermode=OUTSIDE,x=150,y=80,height=300,width=200)

select_btn=Button(btn_frame,text="Select Image",fg="white",justify=CENTER,cursor="hand2",width=20,height=2,bd=1,bg="royal blue",font=myFont,command=select_pic,padx=1,pady=1).grid(row=0,column=0,padx=10,pady=10)
movability=Button(btn_frame,text="Movability Score",fg="white",justify=CENTER,cursor="hand2",width=20,height=2,bd=1,bg="royal blue",font=myFont,command=get_movability,padx=1,pady=1).grid(row=2,column=0,padx=10,pady=10)

variable=tk.StringVar(btn_frame)
variable.set('Corner detector')
opt1=tk.OptionMenu(btn_frame,variable,*corner_detection)
variable.trace("w", callback)
opt1.config(width=15,height=2,font=myFont,bg="royal blue",fg="white")
opt1.place(x=5,y=160)

Save=Button(canvas,text="Save",fg="black",justify=CENTER,bg="coral",cursor="hand2",width=10,height=2,font=myFont,padx=1,pady=1,command=save_current)
Save.place(x=30,y=330)
Exit_btn=Button(canvas,text="Exit",fg="black",justify=CENTER,bg="coral",cursor="hand2",width=10,height=2,font=myFont,padx=1,pady=1,command=window.quit)
Exit_btn.place(x=330,y=330)
window.mainloop()