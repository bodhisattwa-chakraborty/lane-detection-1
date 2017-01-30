# import cv
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

'''
calculate the threshold of x or y sobel given certain thesh and kernel sizes
'''
def abs_sobel_thresh(img, orient='x', sobel_kernel=3, thresh=(0, 255)):
  # grayscale image
  red = img[:, :, 0]
  # gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
  # find abs sobel thresh
  if orient == 'x':
    sobel = cv2.Sobel(red, cv2.CV_64F, 1, 0, ksize=sobel_kernel)
  else:
    sobel = cv2.Sobel(red, cv2.CV_64F, 0, 1, ksize=sobel_kernel)
  
  #get abs value
  abs_sobel = np.absolute(sobel)
  # need to scale from 64 bit image to 8 bit... just needs to be uniform
  # so shouldnt mess up image?
  scaled = np.uint8(255*abs_sobel/np.max(abs_sobel))
  
  grad_binary = np.zeros_like(scaled)
  grad_binary[(scaled >= thresh[0]) & (scaled <= thresh[1])] = 1
  return grad_binary


'''
calculate magnitude of gradient given an image and threshold
'''
def mag_thresh(img, sobel_kernel=3, mag_thresh=(0, 255)):
  # gray scale
  red = img[:, :, 0]
  gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
  
  # given the magnitude of threshold for the combined two, return
  abs_x = np.absolute(cv2.Sobel(red, cv2.CV_64F, 1, 0, ksize=sobel_kernel))
  abs_y = np.absolute(cv2.Sobel(red, cv2.CV_64F, 0, 1, ksize=sobel_kernel))

  mag = np.sqrt(abs_x ** 2 + abs_y ** 2)
  scaled = (255*mag/np.max(mag))

  binary_output = np.zeros_like(scaled)
  binary_output[(scaled >= mag_thresh[0]) & (scaled <= mag_thresh[1])] = 1
  return binary_output

'''
calculate direction of gradient given image and thresh
'''
def dir_thresh(img, sobel_kernel=3, thresh=(0, np.pi/2)):
  # red = img[:, :, 0]

  gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
  
  # given the magnitude of threshold for the combined two, return
  abs_x = np.absolute(cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=sobel_kernel))
  abs_y = np.absolute(cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=sobel_kernel))

  sobel_dir = np.arctan2(abs_y, abs_x)

  binary_output = np.zeros_like(sobel_dir)
  binary_output[(sobel_dir >= thresh[0]) & (sobel_dir <= thresh[1])] = 1
  return binary_output

'''
calculate the threshold of the hls values
'''
def hls_thresh(img, thresh=(0, 255)):
  hls = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)

  s_channel = hls[:, :, 2]

  binary_output = np.zeros_like(s_channel)
  binary_output[(s_channel > thresh[0]) & (s_channel <= thresh[1])] = 1

  return binary_output

'''
combine the thresholding functions
'''
def combo_thresh():
  x_thresholded = abs_sobel_thresh(image, orient='x', sobel_kernel=3, thresh=(6, 120))
  plt.imshow(x_thresholded, cmap='gray')
  plt.title('xthresh')
  # plt.show()

  y_thresholded = abs_sobel_thresh(image, orient='y', sobel_kernel=3, thresh=(10, 100))
  plt.imshow(y_thresholded, cmap='gray')
  plt.title('ythresh')
  # plt.show()

  binary_output = np.zeros_like(x_thresholded)
  # using bitwise or + and, look up how working
  binary_output[((x_thresholded == 1) & (y_thresholded == 1))] = 1
  plt.imshow(binary_output, cmap='gray')
  plt.title('x and y')
  # plt.show()

  hls_thresholded = hls_thresh(image, thresh=(90, 255))
  plt.imshow(hls_thresholded, cmap='gray')
  plt.title('hls')
  # plt.show()
  

  binary_output = np.zeros_like(x_thresholded)
  # using bitwise or + and, look up how working
  binary_output[((x_thresholded == 1) & (y_thresholded == 1)) & (hls_thresholded == 1)] = 1
  plt.imshow(binary_output, cmap='gray')
  plt.title('x and y, and hls')
  # plt.show()
  # 

  mag_thresholded = mag_thresh(image, sobel_kernel=3, mag_thresh=(20, 160))
  plt.imshow(mag_thresholded, cmap='gray')
  plt.title('magnitude')
  # plt.show()

  dir_thresholded = dir_thresh(image, sobel_kernel=15, thresh=(.7, 1.2))  
  plt.imshow(dir_thresholded, cmap='gray')  
  plt.title('directional')
  # plt.show()

  binary_output = np.zeros_like(dir_thresholded)
  # using bitwise or + and, look up how working
  binary_output[((dir_thresholded == 1) & (mag_thresholded == 1))] = 1
  plt.imshow(binary_output, cmap='gray')
  plt.title('dir and mag')
  # plt.show()


  binary_output = np.zeros_like(dir_thresholded)
  # using bitwise or + and, look up how working
  binary_output[((x_thresholded == 1) & (y_thresholded == 1)) | ((dir_thresholded == 1) & (mag_thresholded == 1) & (hls_thresholded == 1))] = 1
  # 
  return binary_output


'''
warp the perspective based on 4 points
'''
def changePerspective(img):
  img_size = (image.shape[1], image.shape[0])
  # print('image shape is', img_size)
  # [0] is 720, [1] is 128-
  src = np.float32(
    [[(img_size[0] / 2) - 40, img_size[1] / 2 + 90],
    [((img_size[0] / 6) + 40), img_size[1]],
    [(img_size[0] * 5 / 6) + 115, img_size[1]],
    [(img_size[0] / 2 + 42), img_size[1] / 2 + 90]])
  # print('src is', src)

  dst = np.float32(
    [[(img_size[0] / 4), 0],
    [(img_size[0] / 4), img_size[1]],
    [(img_size[0] * 3 / 4), img_size[1]],
    [(img_size[0] * 3 / 4), 0]])
  # print('dst is', dst)

  # cv2.fillConvexPoly(image, src, 1)
  # plt.imshow(image)
  # plt.title('lines')
  # plt.show()
  M = cv2.getPerspectiveTransform(src, dst)
  shape = img.shape
  warped = cv2.warpPerspective(img, M, (shape[1], shape[0]))
  return warped


if __name__ == '__main__':
  # image = mpimg.imread('straight_road_1x.jpg')
  image = mpimg.imread('output_images/test1_undistorted.jpg')
  plt.imshow(image)
  plt.title('starter')
  plt.show()

  warped = changePerspective(image)
  plt.imshow(warped)
  plt.title('warped')
  plt.show()

  # x_thresholded = abs_sobel_thresh(image, orient='x', sobel_kernel=3, thresh=(6, 120))
  # plt.imshow(x_thresholded, cmap='gray')
  # plt.show()

  # y_thresholded = abs_sobel_thresh(image, orient='y', sobel_kernel=3, thresh=(10, 100))
  # plt.imshow(y_thresholded, cmap='gray')
  # plt.title('ythresh')
  # plt.show()

  # hls_thresholded = hls_thresh(image, thresh=(90, 255))
  # plt.imshow(hls_thresholded, cmap='gray')
  # plt.title('hls')
  # plt.show()

  # mag_thresholded = mag_thresh(image, sobel_kernel=3, mag_thresh=(20, 160))
  # plt.imshow(mag_thresholded, cmap='gray')
  # plt.title('magnitude')
  # plt.show()

  # dir_thresholded = dir_thresh(image, sobel_kernel=15, thresh=(.7, 1.2))  
  # plt.imshow(dir_thresholded, cmap='gray')  
  # plt.title('directional')
  # plt.show()

  # combo = combo_thresh()
  # plt.imshow(combo, cmap='gray')
  # plt.title('combo')
  # plt.show()