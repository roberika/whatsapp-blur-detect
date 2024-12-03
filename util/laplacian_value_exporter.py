# import the necessary packages
from imutils import paths
import argparse
import csv
import cv2
from tqdm import tqdm

def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", required=True,
help="path to input directory of images")
args = vars(ap.parse_args())

with open('lap_var_values.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    ##print("Focus Measure\tActual Blur\tPredicted Blur")
    writer.writerow(['lap_var','blur'])
    with tqdm(total=2130) as pbar:
        # loop over the input images
        for imagePath in paths.list_images(args["images"]):
            # load the image, convert it to grayscale, and compute the
            # focus measure of the image using the Variance of Laplacian
            # method
            image = cv2.imread(imagePath)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (1200, 1600))
            fm = variance_of_laplacian(resized)
            
            actu = 0 # not blurry
            # if the image contains Mb (motion blur) or Ob(out-of-focus blur)
            if ("Ob" in imagePath.rsplit('\\', 1)[-1]):
                actu = 1 # out of focus blur
            if ("Mb" in imagePath.rsplit('\\', 1)[-1]):
                actu = 2 # motion blur
                
##            pred = "Not Blurry"
##            # if the focus measure is less than the supplied threshold,
##            # then the image should be considered "blurry"
##            if fm < 100:
##                pred = "Blurry"
                
            # show the image
            ##cv2.putText(image, "{}: {:.2f}".format(pred, fm), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
            ##cv2.imshow("Image", image)
            ##key = cv2.waitKey(0)
            # prints the focus measure and clasification
            ##print('%.6f\t%s\t%s' % (fm, actu, pred))
            writer.writerow([fm, actu])
            pbar.update(1)
