import os, io, torch
from torchvision import models
# import torchvision.transforms as transforms
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
from PIL import Image
from flask import request, current_app, jsonify
from flask_restful import Resource, abort, reqparse
from werkzeug import datastructures
from sqlalchemy.orm.exc import NoResultFound
from api.db.database import db
from api.models.lesion import Lesion
from api.schemas.lesion_schema import LesionSchema
import uuid
from flask_jwt_extended import jwt_required

LESIONS_ENDPOINT = "/api/lesions"

class LesionsResource(Resource):

    def load_model(self):
        model = torch.load(
            os.path.join(current_app.instance_path, 'ml/resnet34-best.pth'),
            map_location=torch.device('cpu')
        )
        model.eval()
        return model

    def transform_image(self, filepath):
        test_transform = A.Compose(
            [
                A.Resize(height=256, width=256),
                A.CenterCrop(height=224, width=224, p=1),
                A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
                ToTensorV2(),
            ]
        )

        image = cv2.imread(filepath)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = test_transform(image=image)["image"]
        # unsqueeze to add a batch dimension
        image = image.unsqueeze(0)
        return image

    def get_prediction(self, filepath):

        model = self.load_model()
        model.eval()
        tensor = self.transform_image(filepath)
        outputs = model.forward(tensor)
        softmax = torch.nn.Softmax(dim=1)
        outputs = softmax(outputs)
        confidence, malignancy = outputs.max(1)
        return malignancy.item(), confidence.item()

    @jwt_required()
    def get(self, id=None, lesion_id=None):
        if lesion_id:
            lesion = Lesion.query.filter_by(
                lesion_id=lesion_id
            ).first()
            lesion_json = LesionSchema().dump(lesion)

            if not lesion_json:
                abort(404, message="Lesion not found.")
            return lesion_json
        elif id:
            lesions = Lesion.query.filter_by(
                user_id=id
            ).all()

            lesions_json = [LesionSchema().dump(lesion) for lesion in lesions]
            if not lesions_json:
                abort(404, message="No result")
            return lesions_json
            

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
                filepath = f"{os.path.join(current_app.static_folder, f'uploads/{new_filename}{file_ext}')}"
                image_file.save(filepath)

                # img_bytes = open(file_path, "r").read()

                malignancy, conf = self.get_prediction(filepath)

                lesion = LesionSchema().load({
                    "user_id": id,
                    "lesion_img_url": f"uploads/{new_filename}{file_ext}",
                    "lesion_malignancy": malignancy,
                    "lesion_pred_conf": f"{conf:.2f}"
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
    def delete(self, id=None):
        if id:
            lesion = Lesion.query.filter_by(lesion_id=id).first()
            if lesion:
                try:
                    db.session.delete(lesion)
                    db.session.commit()
                except Exception as e:
                    abort(500, message=f"Failed to delete entry.\n{e}")
                else:
                    return {"message": "DEL_SUCCESS"}, 201
            else:
                abort(400, message="Nothing to delete.")