from os import environ

from loko_extensions.business.decorators import extract_value_args
from loko_extensions.model.components import Component, Input, Output, save_extensions
from sanic import Sanic
from sanic import Blueprint
from sanic_openapi import swagger_blueprint, doc
from sanic.response import json, raw

from business.ocr import OCR

pyTess = Component('PyTessBaseAPI',
                   inputs=[Input(id='input', label='extract', service='extract', to='output')],
                   outputs=[Output(id='output')],
                   description='A simple custom component to allow an alternative of Tesseract usage (based on PyTessBaseAPI)')


save_extensions([pyTess])

app = Sanic("PyTessBaseAPI")
swagger_blueprint.url_prefix = "/api"
app.blueprint(swagger_blueprint)
bp = Blueprint("default")


@bp.post("/extract")
@doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data", required=True)
@extract_value_args(file=True)
async def test(file, args):
    content = file[0].body

    ret = OCR(content)

    if isinstance(ret, dict):
        return json(ret)
    return raw(ret)


app.blueprint(bp)

if __name__ == "__main__":
    app.run("0.0.0.0", environ.get("PORT", 8080))
