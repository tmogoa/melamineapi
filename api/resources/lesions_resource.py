import os, io, torch
from torchvision import models
import torchvision.transforms as transforms
from PIL import Image
from flask import request, current_app, jsonify
from flask_restful import Resource, abort, reqparse
from werkzeug import datastructures

from api.db.database import db
from api.models.lesion import Lesion
from api.schemas.lesion_schema import LesionSchema
import uuid
from flask_jwt_extended import jwt_required

LESIONS_ENDPOINT = "/api/lesions"

class LesionsResource(Resource):

    def load_model(self):
        model = torch.load(
            os.path.join(current_app.instance_path, 'ml/acc-82-resnet.pth'),
            map_location=torch.device('cpu')
        )
        model.eval()
        return model

    def transform_image(self, filepath):
        my_transforms = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            )
        ])
        image = Image.open(filepath).convert('RGB')
        return my_transforms(image).unsqueeze(0)


    def get_prediction(self, filepath):
        tensor = self.transform_image(filepath=filepath)
        model = self.load_model()
        outputs = model.forward(tensor)
        outputs = torch.sigmoid(outputs)
        conf, malignancy = outputs.max(1)
        return malignancy.item(), conf.item()

    @jwt_required()
    def get(self):
        pass
        # model = self.load_model()
        # if model:
        #     return jsonify({"msg": "model loaded"})
        # else:
        #     abort(500, message="Error occurred!")

    @jwt_required()
    def post(self, id=None):
        if id:
            parse = reqparse.RequestParser()
            parse.add_argument('file', type=datastructures.FileStorage, location='files')
            args = parse.parse_args()
            image_file = args['file']
            filename = image_file.filename
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                    abort(400, message="Only PNG, JPG and GIF are permitted")

                new_filename = str(uuid.uuid4())
                filepath = f"{os.path.join(current_app.instance_path, f'uploads/{new_filename}{file_ext}')}"
                image_file.save(filepath)

                # img_bytes = open(file_path, "r").read()

                malignancy, conf = self.get_prediction(filepath)

                lesion = LesionSchema().load({
                    "user_id": id,
                    "lesion_img_url": f"uploads/{new_filename}{file_ext}",
                    "lesion_malignancy": malignancy,
                    "lesion_pred_conf": conf
                })

                try:
                    db.session.add(lesion)
                    db.session.commit()
                except Exception as e:
                    abort(500, message=f"Failed to process image.\n{e}")
                else:
                    return LesionSchema().dump(lesion)
        
        else:
            abort(400, message="user_id is required.")

    @jwt_required()
    def predict():
        pass

    @jwt_required()
    def delete(self):
        pass