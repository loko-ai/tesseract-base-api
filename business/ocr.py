from io import BytesIO

from tesserocr import PyTessBaseAPI
import pdf2image as pdf2image
from PIL import Image
import magic

mime = magic.Magic(mime=True)

from business.text import JOINER_FACTORY


class Tesseract:

    def __init__(self, join_mode="text", join_str=None):
        self.joiner = JOINER_FACTORY(join_mode)(join_str=join_str)

    def __call__(self, file, lang="ita"):

        images = self.get_images(file)
        texts = [self.get_text(img) for img in images]

        return self.joiner(texts)

    def get_text(self, image, lang="ita"):
        with PyTessBaseAPI(lang=lang) as api:
            api.SetImage(image)
            text = api.GetUTF8Text()
        return text

    def get_images(self, file):

        if isinstance(file, str):
            file = open(file, "rb").read()

        mt = mime.from_buffer(file)
        file = BytesIO(file)

        if "image" in mt:
            return [Image.open(file)]
        if "pdf" in mt:
            return self._page_split(file)

        raise Exception("not supported extension {}".format(mt))

    def _page_split(self, file):
        '''@file: Bytes or path'''
        if isinstance(file, str):
            return pdf2image.convert_from_path(file)
        return pdf2image.convert_from_bytes(file.read())

OCR = Tesseract(join_mode="json")

if __name__ == '__main__':

    fname = "/home/alejandro/Documents/PDFname.pdf"
    # fname = "/media/alejandro/DATA/FileCV/2089405_CVD_108249.png"
    t = Tesseract(join_mode="text", join_str="\nnew page\n")
    t2 = Tesseract(join_mode="json")

    # print(t(fname))
    # print(t2(fname))

    with open(fname, "rb") as file:
        f = file.read()
        print(t(f))
        print(t2(f))
