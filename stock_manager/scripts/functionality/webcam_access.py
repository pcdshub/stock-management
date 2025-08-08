import cv2

vc = cv2.VideoCapture(0)

if not vc.isOpened():
    print('Could not access webcam')
    exit()

rval, frame = vc.read()

while rval:
    cv2.imshow('Test Window Name', frame)
    rval, frame = vc.read()
    key = cv2.waitKey(50)  # 1 Frame per x ms
    if key == 27:  # ESC key
        break

vc.release()
cv2.destroyWindow('preview')
