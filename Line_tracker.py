import cv2
import numpy as np
import utils
import serial

kernel = np.ones((5,5),np.uint8)

cam = "redline_Trim.mp4"
def empty(a):
    pass


vid = cv2.VideoCapture(cam)
if not vid.isOpened():
    raise IOError("Cannot open video file / live feed")

cv2.namedWindow("TrackBars") #Create new trackbar window
cv2.resizeWindow("TrackBars", 960, 540) #resize that window

cv2.createTrackbar("Hue Min","TrackBars", 125, 179, empty) #create trackbars with range of values
cv2.createTrackbar("Hue Max","TrackBars", 179, 179, empty)
cv2.createTrackbar("Sat Min","TrackBars", 111, 255, empty)
cv2.createTrackbar("Sat Max","TrackBars", 255, 255, empty)
cv2.createTrackbar("Val Min","TrackBars", 99, 255, empty)
cv2.createTrackbar("Val Max","TrackBars", 255, 255, empty)
cv2.createTrackbar("Cannyarg1","TrackBars", 100, 200, empty)
cv2.createTrackbar("Cannyarg2","TrackBars", 100, 200, empty)
cv2.createTrackbar("maxlinegap","TrackBars", 0, 200, empty)

state = 1

while True:
    success, frame = vid.read()
    frame = cv2.resize(frame, (960, 540))
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)   #convert image to HSV
    h_min = cv2.getTrackbarPos("Hue Min","TrackBars") #Get the positions of the trackbars to use as values
    h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")
    s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")
    s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")
    v_min = cv2.getTrackbarPos("Val Min", "TrackBars")
    v_max = cv2.getTrackbarPos("Val Max", "TrackBars")
    maxlinegap = cv2.getTrackbarPos("maxlinegap", "TrackBars")
    canny1 = cv2.getTrackbarPos("Cannyarg1", "TrackBars")
    canny2 = cv2.getTrackbarPos("Cannyarg2", "TrackBars")
    lower = np.array([h_min,s_min,v_min]) #Create an array of min values
    upper = np.array([h_max,s_max,v_max]) #Create an array of max values
    mask = cv2.inRange(imgHSV, lower, upper)
    frameResult = cv2.bitwise_and(frame, frame, mask=mask)
    maskCanny = cv2.Canny(frameResult, canny1, canny2)
    maskDialated = cv2.dilate(maskCanny, kernel, iterations=3)
    baseyPoint, basexPoint = utils.getbasePoints(maskDialated, minpercentage=0.5)
    if state == 1:
        if basexPoint > 799:
            state+=1
    elif state == 2:
        if baseyPoint > 400:
            state+=1
    elif state == 3:
        if basexPoint < 350:
            
            state +=1
    elif state == 4:
        if baseyPoint > 400:
            state +=1
    elif state == 5: 
        if basexPoint > 750: #THIS VALUE IS FOR THE END OF STATE 5, (final right)
            print("END") #STOP THE ROV HERE
            #quit() 

    utils.movement(state)
    utils.centralizeX(basexPoint, state) ##CENTRALIZATION OF THE LINE DEPENDING ON STATE (VERTICAL/HORIZONTAL)
    utils.centralizeY(baseyPoint, state)
    utils.rotation_control(state, maskDialated, sens=0.08)
    print(state)

    cv2.line(frame, (basexPoint, 0), (basexPoint, 540), (0, 255, 255), 2) ##DRAW LOCATION OF BASEPOINT FOR VISUAL
    cv2.line(frame, (0, baseyPoint), (960, baseyPoint), (0, 255, 255), 2)
    cv2.circle(frame, (basexPoint, baseyPoint), 10, (0, 0, 0), cv2.FILLED)
    contours, hierarchy = cv2.findContours(maskDialated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    lines = cv2.HoughLinesP(maskDialated, 1, np.pi/180, 100, maxLineGap=maxlinegap)
    cv2.imshow("LinesResult", frame)
    cv2.imshow("Dialated", maskDialated) 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        quit()