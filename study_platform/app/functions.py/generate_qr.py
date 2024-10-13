import qrcode

def make_qr(link):
    qr = qrcode.make(link)
    qr.save('qr.png')

make_qr('https://www.google.com')