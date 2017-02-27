import os
import sys
import glob
import qrcode
import PIL.Image

def get_GPS(exif):
    # Get the GPS location dictionary from the EXIF data
    if exif[34853] is not None:
        return exif[34853]
    else:
        return False

def get_GPS_dec(exif):
    # Parse the GPS data into a decimal string
    if get_GPS(exif):
        GPS_data_dict = get_GPS(exif)
        return '%f%s,%f%s' % ((GPS_data_dict[2][0][0] + (GPS_data_dict[2][1][0]/60) + (GPS_data_dict[2][2][0]/3600)), GPS_data_dict[1], (GPS_data_dict[4][0][0] + (GPS_data_dict[4][1][0]/60) + (GPS_data_dict[4][2][0]/3600)), GPS_data_dict[3])
    else:
        return False

def get_GMaps_link(exif):
    # Add the GPS string to the Google Maps link
    if get_GPS(exif):
        return 'https://www.google.co.nz/maps/place/%s' % get_GPS_dec(exif)
    else:
        return False

def make_QR(link, size):
    # Create a QR code of (size) containing data (link)
    qr=qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
        )
    qr.add_data(link)
    qr.make(fit=True)
    img=qr.make_image()
    img=img.resize((size,size))
    return img

def paste_QR_on_Image(image, qr, locationX, locationY):
    # Return an image with the QR pasted in the designated location
    image.paste(qr, (locationX, locationY))
    return image

def createImage(filename):
    outfile='QR-%s' % filename
    img=PIL.Image.open(filename)

    # Get image dimensions
    imgX = img.size[0]
    imgY = img.size[1]

    # Calculate QR image size
    QRsize = int(imgX / 12.5)

    # Create QR code paste coordinates
    pasteX = imgX - int(QRsize * 1.1)
    pasteY = imgY - int(QRsize * 1.1)

    # Get EXIF data from image
    exif = img._getexif()

    if not get_GPS(exif):
        return False

    # Generate QR code    
    imgQR = make_QR(get_GMaps_link(exif), QRsize)

    # Paste QR code on original image
    img = paste_QR_on_Image(img, imgQR, pasteX, pasteY)

    # Save image
    img.save(outfile)

    return True

def main():
    # Pass input to image creation function
    if len(sys.argv) > 1:
        filenames=sys.argv[1:]
    else:
        sys.exit('No filename supplied!')

    if sys.argv[1] == '-all':
        print('Process all JPGs in folder:')
        filenames = glob.glob('*.jpg')

    for file in filenames:
        # Create image
        if os.path.isfile(file):
            # print(file)
            if createImage(file):
                print('%s processed!' % file)
            else:
                print('There was a problem processing %s.' % file)
    

main()
