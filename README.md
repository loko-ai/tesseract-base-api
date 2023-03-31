<html><p><a href="https://loko-ai.com/" target="_blank" rel="noopener"> <img style="vertical-align: middle;" src="https://user-images.githubusercontent.com/30443495/196493267-c328669c-10af-4670-bbfa-e3029e7fb874.png" width="8%" align="left" /> </a></p>
<h1>Tesseract base API</h1><br></html>

**Tesseract base API** extension is based on <a href="https://github.com/sirfz/tesserocr">tesserocr</a> to implement OCR (Optical Character Recognition).

From the **Projects**'s tab, click on **Import from git** and copy and paste the URL of the current page 
(i.e. https://github.com/loko-ai/tesseract-base-api):
<p align="center"><img src="https://user-images.githubusercontent.com/30443495/229048981-e03d7b6f-6ef4-4064-8c0e-75052497744a.png" width="60%" /></p>
Once the project is downloaded, click and open it.  
<p align="center"><img src="https://user-images.githubusercontent.com/30443495/229172380-1461f6e2-4fa7-43d5-8798-ce9fa5c36f12.png" width="80%" /></p>

In order to start the project remember to press the **play** button on the right of the project's name.

You'll find the PyTessBaseAPI extension on the bottom of blocks' list. Choose a file in the *File Reader* component and click on **Run**.

<p align="center"><img src="https://user-images.githubusercontent.com/30443495/229173287-bdef50fb-4669-4dbf-b548-73a4866dd818.png" width="80%" /></p>

In the **Console** you'll visualize the extracted text.

Let's now see how to custom the extension (See more here <a href="https://github.com/loko-ai/loko/wiki/Custom-extensions">Custom extensions</a>).

Click right on the project's name on *Open in editor* (configure your editor using the Loko's settings first):
<p align="center"><img src="https://user-images.githubusercontent.com/30443495/229174649-eea3b85a-2b58-4a94-abe7-5caca4859b49.png" width="80%" /></p>

Otherwise, you can open your project directly on the Loko's directory (i.e. `~/loko/projects/tesseract-base-api`).

First of all, install the required libraries in the Dockerfile:
```
sudo apt-get install tesseract-ocr libtesseract-dev libleptonica-dev pkg-config
```

Then, create you **venv**, named venv, using python3.7 and install *requirements.lock*.

### Services

In `/tesseract-base-api/services/services.py` you'll find the PyTessBaseAPI component:

```
pyTess = Component('PyTessBaseAPI',
                   inputs=[Input(id='input', label='extract', service='extract', to='output')],
                   outputs=[Output(id='output')],
                   description='A simple custom component to allow an alternative of Tesseract usage (based on PyTessBaseAPI)')


save_extensions([pyTess])
```

We are defining all the block's information: *inputs*, *outputs*, *args*, *description*. When you run the script, the component will be 
saved as a json into `/tesseract-base-api/extensions/components.json` and showed in your block's list. 
See more here https://loko-extensions.readthedocs.io/en/latest/.

The input of the component is linked to the service `/extract`:

```
@bp.post("/extract")
@doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data", required=True)
@extract_value_args(file=True)
async def test(file, args):
    content = file[0].body

    ret = OCR(content)

    if isinstance(ret, dict):
        return json(ret)
    return raw(ret)
```

Parameter *file* represents the input of the block, while *args* represents the configuration of the block (we don't use any configuration in this case).

### OCR

In `/tesseract-base-api/business/ocr.py` you'll find the implementation of the OCR:

```
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

```

### Dockerfile

Once you prepared your components and the services they are linked to, you have to configure the Dockerfile of your 
container:

```
FROM python:3.7-slim
RUN apt-get update --fix-missing && apt-get install -y gcc tesseract-ocr wget libmagic-dev ffmpeg libsm6 libxext6 g++ libleptonica-dev libtesseract-dev && rm -rf /var/cache/apt
RUN rm /usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/ita.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
ADD ./requirements.lock /
RUN pip install -r /requirements.lock
ARG GATEWAY
ENV GATEWAY=$GATEWAY
ADD . /plugin
ENV PYTHONPATH=$PYTHONPATH:/plugin
ENV LC_ALL=C
WORKDIR /plugin/services
EXPOSE 8080
CMD python -m sanic services.app --host=0.0.0.0 --port=8080

```

When you **stop** your project and click again on the **play** button, Loko builds a new image, and you're ready to use 
your extension. 
