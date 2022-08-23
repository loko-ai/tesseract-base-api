from sanic import Sanic
from sanic import Blueprint
from sanic_openapi import swagger_blueprint, doc
from sanic.response import json, raw

from business.ocr import OCR

app = Sanic("PyTessBaseAPI")
swagger_blueprint.url_prefix = "/api"
app.blueprint(swagger_blueprint)
bp = Blueprint("default")

@bp.post("/extract")
@doc.consumes(doc.File(name="file"), location="formData", content_type="multipart/form-data", required=True)
def test(request):
    file = request.files.get('file')
    name = file.name
    content = file.body

    ret = OCR(content)

    if isinstance(ret, dict):
        return json(ret)
    return raw(ret)

app.blueprint(bp)

app.run("0.0.0.0", 9393)
