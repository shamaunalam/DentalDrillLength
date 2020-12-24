import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os
import shutil

lines = []
frame = None
datas = pd.DataFrame({'Image': [], 'x1': [], 'y1': [], 'x2': [], 'y2': [], 'x3': [], 'y3': [], 'x4': [], 'y4': []})
tempdir = r"img_temp"
imgdir = r"img_dir"
isVisible = True
MMPP = 0.04719  ## mm per pixel

try:
    file = pd.read_csv(r"length_data_standard.csv")
except:
    datas.to_csv(r"length_data_standard.csv", index = False, header = True)
    file = "done"
else:
    pass
finally:
    del file


def showControls(ms):
    controls_page = np.zeros((320,640,3))
    cv2.putText(controls_page, "Controls", (220, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255), 3, cv2.LINE_AA)
    cv2.line(controls_page, (200, 60), (440, 60) ,(0, 0, 255), 2)
    cv2.putText(controls_page, "Esc", (20, 90), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (0, 69, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "- to remove current point(s) / skip this page", (70, 90), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "h/H", (20, 120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (0, 69, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "- to see this page again", (70, 120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "n/N", (20, 150), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (0, 69, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "- goto next frame", (70, 150), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "s/S", (20, 180), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (0, 69, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "- save current contour", (70, 180), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "x/X", (20, 210), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (0, 69, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "- exports the contour data to csv file", (70, 210), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "q/Q", (20, 240), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (0, 69, 255), 1, cv2.LINE_AA)
    cv2.putText(controls_page, "- to quit", (70, 240), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
    
    cv2.imshow("Preview Window", controls_page)
    k = cv2.waitKey(ms)
    if k == 27:
        cv2.imshow("Preview Window", frame)
        return
    cv2.imshow("Preview Window", frame)

def getCoordinate(event, x, y, flags, param):
    global lines, frame, MMPP
    
    frame_copy = frame.copy()
    
    if event == cv2.EVENT_LBUTTONDOWN and len(lines)<4:
        lines.append( (x, y) )
        #print(x,y)
        
    if event == cv2.EVENT_LBUTTONDOWN and len(lines) == 1:
        for i in range(x-4, x+3):
            for j in range(y-4, y+3):
                frame_copy[j,i] = [255, 255, 0]
        cv2.imshow("Preview Window", frame_copy)
        
    elif event == cv2.EVENT_LBUTTONDOWN and len(lines) == 2:
        cv2.line(frame_copy,lines[0],lines[1],(255,255,0), 2)
        x1 = lines[0][0]
        y1 = lines[0][1]
        x2 = lines[1][0]
        y2 = lines[1][1]
        d = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        print(round(d*MMPP,3),"mm")
        cv2.imshow("Preview Window", frame_copy)
        
    elif event == cv2.EVENT_LBUTTONDOWN and len(lines) > 2 and len(lines)<5:
        pts = np.array(lines, np.int32)
        pts = pts.reshape((-1,1,2))
        cv2.polylines(frame_copy, [pts], True, (255,255,0), 2)
        if len(lines) != 4:
            cv2.imshow("Preview Window", frame_copy)
        else:
            cv2.putText(frame_copy, "press s/S to save contour", (10,40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.imshow("Preview Window", frame_copy)
            if datas.shape[0] >= 5:
                cv2.putText(frame_copy, "press x/X to export -- {} unexported data found".format(datas.shape[0]), (10,70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 255), 2, cv2.LINE_AA)
                cv2.imshow("Preview Window", frame_copy)
                
def exportToFile():
    global datas, frame, tempdir, imgdir
    
    frame_copy1 = frame.copy()
    frame_copy2 = frame.copy()
    
    file = pd.read_csv(r"length_data_standard.csv")
    file = file.append(datas)
    
    imgs = os.listdir(tempdir)
    for img in imgs:
        shutil.move(os.path.join(tempdir,img), imgdir, copy_function=shutil.copytree)
        
    file.to_csv(r"length_data_standard.csv", index = False, header = True)
    
    datas.drop(datas.index, inplace=True)
    
    cv2.putText(frame_copy1, "Data Exported", (20,40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow("Preview Window", frame_copy1)
    cv2.waitKey(750)
    cv2.imshow("Preview Window", frame_copy2)
    
     
def saveContour():
    global lines, datas, frame, tempdir
    
    frame_copy1 = frame.copy()
    frame_copy2 = frame.copy()
    
    if len(lines) == 4:
        img_name = datetime.now().strftime("%Y_%m_%d__%H_%M_%S___%f.jpg")
        temp_data = pd.DataFrame({'Image': [img_name], 'x1': [lines[0][0]], 'y1': [lines[0][1]], 'x2': [lines[1][0]], 'y2': [lines[1][1]],
                                  'x3': [lines[2][0]], 'y3': [lines[2][1]], 'x4': [lines[3][0]], 'y4': [lines[3][1]]})
        cv2.imwrite(os.path.join(tempdir, img_name), frame_copy1)
        datas = datas.append(temp_data, ignore_index=True)
        
        cv2.putText(frame_copy1, "Contour Saved", (20,40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow("Preview Window", frame_copy1)
        cv2.waitKey(750)
        cv2.imshow("Preview Window", frame_copy2)
    else:
        cv2.putText(frame_copy1, "you need 4 points to save contour", (20,40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow("Preview Window", frame_copy1)
        cv2.waitKey(750)
        cv2.imshow("Preview Window", frame_copy2)
    
    lines = []

cam = cv2.VideoCapture(0)

check, frame = cam.read()

if check:
    showControls(5000)

while check:
    check, frame = cam.read()
    
    if not check:
        break
    
    cv2.imshow("Preview Window", frame)
    cv2.setMouseCallback("Preview Window", getCoordinate)
     
    while True:
        
        k = cv2.waitKey(30)
        if k in [ord('n'), ord('N'), ord('q'), ord('Q')]:
            lines.clear()
            break
        
        if k == 27:
            lines.clear()
            cv2.imshow("Preview Window", frame)
            
        if k in [ord('x'), ord('X')]:
            exportToFile()
            
        if k in [ord('s'), ord('S')]:
            saveContour()
        
        if k in [ord('h'), ord('H')]:
            showControls(5000)
        
        if cv2.getWindowProperty('Preview Window', cv2.WND_PROP_AUTOSIZE) < 0:
            isVisible = False
            break
    
    if k in [ord('q'), ord('Q')] or not isVisible:
        break
        
if not check:
    print("Camera not found")
    
cv2.destroyAllWindows()
cam.release()