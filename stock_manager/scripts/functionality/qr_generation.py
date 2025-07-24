import qrcode

qr = qrcode.QRCode(
        None,
        box_size=10,
        border=4,
)

qr.add_data("BK9000")
qr.make()

img = qr.make_image()

img.save("../assets/qr_code.png")
