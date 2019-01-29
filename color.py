import cv2
import numpy as np
import time
import math

cap = cv2.VideoCapture(0)
cap.set(3, 160)
cap.set(4, 120)

def dist(a, b):
    
    # Find distance between two points
    return math.sqrt((a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1]))
    
def average(a, b):
    
    # Average two positions
    cx = (a[0]+b[0])/2
    cy = (a[1]+b[1])/2
    return [cx, cy]
    
def vecMag(vec, mag):
    strPt = vec[0]
    
    #Calculate vector end point from 0,0
    vec[1][0] = vec[1][0] - strPt[0]
    vec[1][1] = vec[1][1] - strPt[1]
    
    curMag = dist((0, 0), vec[1])
    
    vec[1][0] = (vec[1][0]/curMag)*mag + strPt[0]
    vec[1][1] = (vec[1][1]/curMag)*mag + strPt[1]
    
    return vec
    

def findline(image):
    
    # Find contours
    (cnts, _) = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) > 0:
        maxcontour = max(cnts, key = cv2.contourArea)
        return cv2.minAreaRect(maxcontour)


while(1):
    startTime = time.time();
        
    # Take each frame
    _, frame = cap.read()
    #frame = cv2.imread('test2.jpg')
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([0,56,192])
    upper_blue = np.array([100,185,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    marker = findline(mask)
    if marker is not None and marker[1][0] > 0:
        box = np.int0(cv2.cv.BoxPoints(marker))
        
        # Calc side lengths
        ab = dist(box[0], box[1])
        bc = dist(box[1], box[2])
        cd = dist(box[2], box[3])
        da = dist(box[3], box[0])
        
        e = average(box[0], box[1])
        f = average(box[2], box[3])
        ef = average(e, f)
        
        abcd = [average(box[0], box[1]), average(box[2], box[3])]
        bcda = [average(box[1], box[2]), average(box[3], box[0])]
        
        cenPts = abcd
        
        #if(ab < bc):
        #    print(abcd)
        #else:
        #    print(bcda)
        #    cenPts = bcda
            
        if(ab > bc):
            cenPts = bcda
            
        #print(vecMag(abcd, 2000))
        
        #print(frame.shape[:2])
        
        centerPoint = average(average(box[0], box[1]), average(box[2], box[3]))
        
        #print("center point: ", centerPoint)
        focalLength = (64 * 34) / 13
        pixelLength = dist(cenPts[0], cenPts[1]);
        cmDistance = (13 * focalLength) / pixelLength
        pixelsFromCenter = centerPoint[0] - 80
        angleFromCenter = pixelsFromCenter * 0.3
        x = cmDistance * math.sin(angleFromCenter * 0.0174)
        y = cmDistance * math.cos(angleFromCenter * 0.0174)
        print("distance cm: ", round(cmDistance, 3), "angle deg: ", round(angleFromCenter, 3))
        print("x: ", round(x, 3), "y: ", round(y, 3))
        
        #print("pixel length: ", pixelLength)
        
        vecB = vecMag(cenPts, 500)
        
        #cv2.rectangle(frame, (10, 10), (26, 22), (0, 0, 255), 2)
        #cv2.line(frame, (int(vecB[0][0]/10), int(vecB[0][1]/10)), (int(vecB[1][0]/10), int(vecB[1][0]/10)), (0, 0, 255), 2)
        #cv2.line(frame, (int(cenPts[0][0]/10+10), int(cenPts[0][1])/10+10),
        # (int(cenPts[1][0]/10+10), int(cenPts[1][1])/10+10), (255, 255, 0), 2)
        #cv2.line(frame, (int(cenPts[0][0]), int(cenPts[0][1])), (int(cenPts[1][0]), int(cenPts[1][1])), (255, 0, 0), 2)
        cv2.drawContours(frame, [box], -1, (0, 0, 255), 2)
    
    # Display image
    cv2.imshow('frame',frame)
    
    # Output time in milliseconds of processing time
    print("runtime ms: ", round((time.time()-startTime)*1000))
    
    # esc to kill program
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
