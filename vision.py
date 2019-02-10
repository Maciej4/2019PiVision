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
    xTotal = 0
    yTotal = 0
    for pos in vec2s:
        xTotal += pos[0]
        yTotal += pos[1]
    cx = xTotal / len(vec2s)
    cy = yTotal / len(vec2s)
    return [cx, cy]

def boxCenX(box):
    xTotal = 0
    for pos in box:
        xTotal += pos[0]
    cx = xTotal / len(box)
    return cx

def boxAng(box):
    boxAB = dist(box[0], box[1])
    boxBC = dist(box[1], box[2])
    if(boxAB < boxBC):
        boxAB, boxBC = boxBC, boxAB
        boxAngle = math.atan2((box[1][1] - box[2][1]), (box[1][0] - box[2][0]))
    else:
        boxAngle = math.atan2((box[0][1] - box[1][1]), (box[0][0] - box[1][0]))
    return math.degrees(boxAngle)

def longSide(box):
    boxAB = dist(box[0], box[1])
    boxBC = dist(box[1], box[2])
    if(boxAB < boxBC):
        boxAB, boxBC = boxBC, boxAB
    return boxAB

def findCnts(image):
    # Find contours
    (cnts, _) = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) > 0:
        sortedCnts = sorted(cnts, key = cv2.contourArea, reverse = True)
        return sortedCnts

while(1):
    print("\n")
    startTime = time.time();

    # Take each frame
    _, frame = cap.read()
    #frame = cv2.imread('test2.jpg')

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    #lowerBlue = np.array([50,0,235])
    #upperBlue = np.array([60,10,255])
    lowerBlue = np.array([0, 0, 230])
    upperBlue = np.array([50, 45, 255])


    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lowerBlue, upperBlue)

    markers = findCnts(mask)
    if markers is not None:
        boxList = list()
        for marker in markers:
            markerRect = cv2.minAreaRect(marker)
            box = np.int0(cv2.cv.BoxPoints(markerRect))
            boxAB = dist(box[0], box[1])
            boxBC = dist(box[1], box[2])
            if(boxAB < boxBC):
                boxAB, boxBC = boxBC, boxAB
            boxR = boxAB / (boxBC + 1)
            if(boxR > 2 and boxR < 3.3 and (cv2.contourArea(box) > 80)):
                boxList.append(box)

        if boxList is not None and len(boxList) > 0:
            print("box count", len(boxList))
            boxAngles = list()

            for box in boxList:
                boxAngles.append(boxAng(box))

            xBoxList = sorted(boxList, key = boxCenX)

            dockList = list()
            l = 0
            for box in xBoxList:
                if l + 1 < len(xBoxList):
                    box0Ang = boxAng(box)
                    box1Ang = boxAng(xBoxList[l + 1])
                    print(box0Ang, box1Ang)
                    if box0Ang > box1Ang:
                        dockList.append(l)
                l += 1

            if dockList is not None and len(dockList) > 0:
                print("dockList length", len(dockList))

                for index in dockList:
                    origin = average(xBoxList[index])
                    end = average(xBoxList[index + 1])
                    cv2.line(frame, (origin[0], origin[1]), (end[0], end[1]), (0, 255, 0), 2)
                    center = average((origin, end))
                    lineAngle = math.atan2((origin[0] - end[0]), (origin[1] - end[1]))
                    perpAngle = lineAngle + (math.pi / 2)
                    xComp = int(20 * math.sin(perpAngle)) + center[0]
                    yComp = int(20 * math.cos(perpAngle)) + center[1]
                    cv2.line(frame, (center[0], center[1]), (xComp, yComp), (0, 0, 255), 2)
                    cv2.drawContours(frame, [xBoxList[index]], -1, (255, 0, 0), 2)
                    cv2.drawContours(frame, [xBoxList[index + 1]], -1, (255, 0, 0), 2)

                focalLength = (64 * 34) / 13
                leftDistance = (13 * focalLength) / longSide(xBoxList[dockList[0]])
                rightDistance = (13 * focalLength) / longSide(xBoxList[dockList[0] + 1])
                dockDistanceCm = (leftDistance + rightDistance) / 2
                dockXPos = ((boxCenX(xBoxList[dockList[0]]) + boxCenX(xBoxList[dockList[0] + 1])) / 2) - 80
                dockAngle = dockXPos * 0.3
                print("Dock angle", dockAngle)
                print("Dock distance cm", dockDistanceCm)

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
