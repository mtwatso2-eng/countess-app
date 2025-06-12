from shiny import App, ui, render
import numpy as np
import matplotlib.pyplot as plt
import cv2
from pathlib import Path
import os
import time
import pandas as pd
import tensorflow as tf
from scipy import signal
from PIL import Image, ImageOps
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import load_img, img_to_array

def getBorders(cv2Image):
  src = cv2.cvtColor(cv2Image, cv2.COLOR_BGR2GRAY)
  src = cv2.blur(src,(src.shape[1], 1))
  src = cv2.adaptiveThreshold(src,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,101,2)
  points = np.sum(src, axis = 1)
  points = signal.savgol_filter(points, 300, 2)
  plt.cla()
  plt.plot(range(len(points)), points)
  peaks, _ = signal.find_peaks(points, distance = 1000)
  row1 = peaks[0]
  row2 = peaks[-1]
  src = cv2.cvtColor(cv2Image, cv2.COLOR_BGR2GRAY)
  src = cv2.blur(src,(1, src.shape[0]))
  src = cv2.adaptiveThreshold(src,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,101,2)
  points = np.sum(src, axis = 0)
  points = signal.savgol_filter(points, 300, 2)
  plt.plot(range(len(points)), points)
  peaks, _ = signal.find_peaks(points, distance = 700)
  column1 = peaks[0]
  column2 = peaks[-1]
  if(abs((column2 - column1) - 4365) > 200):
    print("col corrected")
    column1 = 227
    column2 = 4643
  if(abs((row2 - row1) - 2100) > 150):
    print("row corrected")
    row1 = 725
    row2 = 2979
  return([row1, row2, column1, column2])

def tupleToList(t):
    return list(map(tupleToList, t)) if isinstance(t, (list, tuple)) else t

def cropSquareFromContour(c, img):

    rect = cv2.minAreaRect(c)

    rect = tupleToList(rect)
    rect[1][0] = max(rect[1])
    rect[1][1] = max(rect[1])

    box = cv2.boxPoints(rect)
    box = np.intp(box)

    width = int(rect[1][0])
    height = int(rect[1][1])

    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height-1],
                        [0, 0],
                        [width-1, 0],
                        [width-1, height-1]], dtype="float32")

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(img, M, (width, height))

    return warped

def cropRectangleFromContour(c, img):

    rect = cv2.minAreaRect(c)

    box = cv2.boxPoints(rect)
    box = np.intp(box)
    width = int(rect[1][0])
    height = int(rect[1][1])

    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height-1],
                        [0, 0],
                        [width-1, 0],
                        [width-1, height-1]], dtype="float32")
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(img, M, (width, height))

    return warped

def classifyObject(cv2Image):
  img = cv2Image
  img = cv2.resize(img, (150, 150))
  img = Image.fromarray(img)

  img_array = tf.keras.preprocessing.image.img_to_array(img)
  img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
  img_array /= 255.0

  # Make a prediction
  predictions = model.signatures['serving_default'](tf.constant(img_array))

  return predictions['output_0'].numpy()

modelDirectory = "saved_model"
model = tf.saved_model.load(modelDirectory)

def countImage(img):
    thisBorders = getBorders(img)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("thresholding image")
    thres = cv2.adaptiveThreshold(img_gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,101,2)
    kernel = np.ones((7, 7), np.uint8)
    thres = cv2.morphologyEx(thres, cv2.MORPH_OPEN, kernel)
    cnts, _ = cv2.findContours(thres, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts_filtered = []
    print("counting eggs")
    for i, c in enumerate(cnts):
        objectIsInFrame = (
            thisBorders[0] < c.flatten()[1] < thisBorders[1] and
            thisBorders[2] < c.flatten()[0] < thisBorders[3]
        )
        area = cv2.contourArea(c)
        # TUNE: AREA THRESHOLD
        # Filter by area
        if(area < 4000 and area > 1500 and objectIsInFrame):
            width = min(cv2.minAreaRect(c)[1])
            length = max(cv2.minAreaRect(c)[1])
            # TUNE: L, W, LW THRESHOLD
            if(length > 40 and length < 150 and length/width > 1.5 and length/width < 5):
                thisObject = cropSquareFromContour(c, img)
                modelClasses = ("egg", "not egg")
                prediction = modelClasses[np.argmax(classifyObject(thisObject))]
                if(prediction == "egg"):
                    cnts_filtered.append(c)

    cv2.rectangle(img, (thisBorders[2], thisBorders[0]), (thisBorders[3], thisBorders[1]), 1, 10)
    cv2.drawContours(img, cnts_filtered, -1, (0,255, 20), 6)
    img = cv2.putText(img, 'Egg count: ' + str(len(cnts_filtered)), (100, 100), 1, 8, 1, 10)
    print("finished counting image")
    return img, len(cnts_filtered)


