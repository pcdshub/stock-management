import cv2


def read_qr_code(filepath: str):
	img = cv2.imread(filepath)
	decode = cv2.QRCodeDetector()
	_, decoded_info, _, _ = decode.detectAndDecodeMulti(img)
	return decoded_info[0]


print(read_qr_code(r'assets/text.png'))
print(read_qr_code(r'assets/linkedin.png'))
