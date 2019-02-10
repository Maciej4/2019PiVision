#!/usr.bin/env python
import cv2
import numpy as np
import time
import math
import sys
#from networktables import NetworkTables

#ip = 'roborio-972-frc.local'
#NetworkTables.initialize(server=ip)
#sd = NetworkTables.getTable("SmartDashboard")
programStart = time.time()
print(programStart)

cap = cv2.VideoCapture(1)
cap.set(3, 160) #160
cap.set(4, 120) #120

def dist(a, b):

    # Find distance between two points
    return math.sqrt((a[0]-b[0])*(a[0]-b[0])+(a[1]-b[1])*(a[1]-b[1]))

def average(vec2s):
    xtotal = 0
    ytotal = 0
    for pos in vec2s:
        xtotal += pos[0]
        ytotal += pos[1]
    cx = xtotal / len(vec2s)
    cy = ytotal / len(vec2s)
    return [cx, cy]

def boxcenx(box):
    xtotal = 0
    for pos in box:
        xtotal += pos[0]
    cx = xtotal / len(box)
    return cx

def boxAng(box):
    boxab = dist(box[0], box[1])
    boxbc = dist(box[1], box[2])
    if(boxab < boxbc):
        boxab, boxbc = boxbc, boxab
        boxangle = math.atan2((box[1][1] - box[2][1]), (box[1][0] - box[2][0]))
    else:
        boxangle = math.atan2((box[0][1] - box[1][1]), (box[0][0] - box[1][0]))
    return math.degrees(boxangle)

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
        sortedcnts = sorted(cnts, key = cv2.contourArea, reverse = True)
        #firstcontour = max(cnts, key = cv2.contourArea)
        #return cv2.minAreaRect(sortedcnts[0])
        return sortedcnts

i = 0
while(1):
    print("\n")
    startTime = time.time();

    # Take each frame
    _, frame = cap.read()
    #frame = cv2.imread('test2.jpg')

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    #lower_blue = np.array([50,0,235])
    #upper_blue = np.array([60,10,255])
    lower_blue = np.array([0, 0, 230])
    upper_blue = np.array([50, 45, 255])


    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    markers = findline(mask)
    if markers is not None:
        boxList = list()
        for marker in markers:
            markerRect = cv2.minAreaRect(marker)
            box = np.int0(cv2.cv.BoxPoints(markerRect))
            boxab = dist(box[0], box[1])
            boxbc = dist(box[1], box[2])
            if(boxab < boxbc):
                boxab, boxbc = boxbc, boxab
            boxr = boxab / (boxbc + 1)
            if(boxr > 2 and boxr < 3.3 and (cv2.contourArea(box) > 80)):
                boxList.append(box)

        if boxList is not None and len(boxList) > 0:
            print("box count", len(boxList))
            boxAngles = list()

            for box in boxList:
                boxAngles.append(boxAng(box))

            xboxlist = sorted(boxList, key = boxcenx)

            dockList = list()
            l = 0
            for box in xboxlist:
                if l + 1 < len(xboxlist):
                    box0ang = boxAng(box)
                    box1ang = boxAng(xboxlist[l + 1])
                    print(box0ang, box1ang)
                    if box0ang > box1ang:
                        dockList.append(l)
                l += 1

            if dockList is not None:
                print("dockList length", len(dockList))

                for index in dockList:
                    origin = average(xboxlist[index])
                    end = average(xboxlist[index + 1])
                    cv2.line(frame, (origin[0], origin[1]), (end[0], end[1]), (0, 255, 0), 2)
                    center = average((origin, end))
                    lineAngle = math.atan2((origin[0] - end[0]), (origin[1] - end[1]))
                    perpAngle = lineAngle + (math.pi / 2)
                    xComp = int(20 * math.sin(perpAngle)) + center[0]
                    yComp = int(20 * math.cos(perpAngle)) + center[1]
                    cv2.line(frame, (center[0], center[1]), (xComp, yComp), (0, 0, 255), 2)
                    cv2.drawContours(frame, [xboxlist[index]], -1, (255, 0, 0), 2)
                    cv2.drawContours(frame, [xboxlist[index + 1]], -1, (255, 0, 0), 2)

            #cv2.line(frame, (box0cen[0], box0cen[1]), (box1cen[0], box1cen[1]), (0, 255, 0), 2)

            #j = 0

            #for box in boxList:
            #    if boxAngles[j] <= 90:
            #        cv2.drawContours(frame, [box], -1, (0, 0, 255), 2)
            #    else:
            #        cv2.drawContours(frame, [box], -1, (255, 0, 0), 2)
            #    j = j + 1


    #        sd.putNumber("visionX", x)
    #        sd.putNumber("visionY", y)

    #        sd.putNumber("Distance", round(cmDistance, 3))
    #        sd.putNumber("visionAngle", angleFromCenter)

    # Display image
    cv2.imshow('frame',frame)

    # Output time in milliseconds of processing time
    print("runtime ms: ", round((time.time()-startTime)*1000))

    # esc to kill program
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
