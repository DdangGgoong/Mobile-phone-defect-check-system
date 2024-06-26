from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.models import load_model
import os
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 모델 로드
models = {
    'iphone11': {
        'front': load_model('iphone14pro_front_model.h5'),
        'left': load_model('iphone14pro_left_model.h5'),
        'right': load_model('iphone14pro_right_model.h5'),
        'back': load_model('iphone14pro_back_model.h5'),
        'top': load_model('iphone14pro_top_model.h5'),
        'bottom': load_model('iphone14pro_bottom_model.h5') 
    },
    # 'iphone12': {
    #     'front': load_model('iphone12_front_model.h5'),
    #     'left': load_model('iphone12_left_model.h5'),
    #     'right': load_model('iphone12_right_model.h5'),
    #     'back': load_model('iphone12_back_model.h5'),
    #     'top': load_model('iphone12_top_model.h5'),
    #     'bottom': load_model('iphone12_bottom_model.h5')
    # }
}

def preprocess_image(image_path):
    image = load_img(image_path, target_size=(224, 224))
    image_array = img_to_array(image)
    return image_array

def predict_defect(image_array, model):
    image_array = image_array / 255.0  # 이미지를 0과 1 사이의 값으로 정규화
    processed_image = np.expand_dims(image_array, axis=0)  # 배치 차원 추가
    prediction = model.predict(processed_image)
    defect_score = int(prediction[0][0] * 100)  # 0~1 사이의 값으로 변환하여 100점 만점으로 스케일링
    return defect_score

def determine_defect(image_path, model):
    image_array = preprocess_image(image_path)
    defect_score = predict_defect(image_array, model)
    return defect_score

def determine_grade(defect_scores):
    average_score = np.mean(list(defect_scores.values()))
    if average_score > 70:
        return "Gold"
    elif average_score > 50:
        return "Silver"
    else:
        return "Bronze"

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze_images():
    try:
        model_type = request.form['model_select']
        
        # 이미지 파일 가져오기
        images = {
            'front': request.files['front_image'],
            'left': request.files['left_image'],
            'right': request.files['right_image'],
            'back': request.files['back_image'],
            'top': request.files['top_image'],
            'bottom': request.files['bottom_image']
        }
        
        # 각 이미지의 하자 점수 예측
        defect_scores = {}
        for view, img in images.items():
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
            img.save(image_path)
            defect_scores[view] = determine_defect(image_path, models[model_type][view])
        
        # 등급 판단
        grade = determine_grade(defect_scores)

         # 총 결과 점수 계산 (단순 평균)
        total_score = np.mean(list(defect_scores.values()))
        
        # 결과 템플릿 렌더링
        return render_template('result.html', 
                                front_image=images['front'].filename,
                                left_image=images['left'].filename,
                                right_image=images['right'].filename,
                                back_image=images['back'].filename,
                                top_image=images['top'].filename,
                                bottom_image=images['bottom'].filename,
                                defect_front=defect_scores['front'], 
                                defect_left=defect_scores['left'], 
                                defect_right=defect_scores['right'], 
                                defect_back=defect_scores['back'], 
                                defect_top=defect_scores['top'], 
                                defect_bottom=defect_scores['bottom'],
                                grade=grade,
                                total_score=total_score) 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.secret_key = 'super_secret_key'
    app.run(debug=True, port=5001)