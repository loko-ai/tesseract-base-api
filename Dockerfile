FROM python:3.7-slim
RUN apt-get update --fix-missing && apt-get install -y gcc tesseract-ocr wget libmagic-dev ffmpeg libsm6 libxext6 g++ libleptonica-dev libtesseract-dev && rm -rf /var/cache/apt
RUN rm /usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/ita.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/spa.traineddata --directory-prefix=/usr/share/tesseract-ocr/4.00/tessdata
ADD ./requirements.txt /
RUN pip install -r /requirements.txt
ARG GATEWAY
ENV GATEWAY=$GATEWAY
ADD . /plugin
ENV PYTHONPATH=$PYTHONPATH:/plugin
ENV LC_ALL=C
WORKDIR /plugin/services
CMD python -m sanic services.app --host=0.0.0.0 --port=8080
