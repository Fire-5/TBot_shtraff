import os
import time
import cv2
import face_recognition


def create_dataset(path_to_dataset):
    os.chdir(path_to_dataset)
    data = []
    for firma in os.listdir():
        print('>', firma)
        os.chdir(firma)
        for pups in os.listdir():
            print('--->', pups)
            # pups_descriptor = detect(f'{os.getcwd()}\\{pups}')
            pups_descriptor = '123'
            name, role, firma = pups.split('_')
            data.append([name, role, firma, pups_descriptor])

    return data


def prepare(one_desc, two_desc):
    print(f'[ IMAGE] - {time.ctime(time.time())} - Calculate Euclidian distance')
    # print(f' > {one_desc}')
    # print(f' > {two_desc}')

    return face_recognition.face_distance(one_desc, two_desc)


def detect(path):
    print(f'[ IMAGE] - {time.ctime(time.time())} - Detecting face')
    image = cv2.imread(path)
    try:
        face_description = face_recognition.face_encodings(image, model='large')[0]
    except Exception:
        print(f'[ IMAGE] - {time.ctime(time.time())} - Not find faces.')
        face_description = None

    return face_description


def calculate():
    print(f'[ IMAGE] - {time.ctime(time.time())} - View Result')


async def main():
    img_desc = detect(f'{os.getcwd()}\\temp\\temp.jpg')
    obm_desc = detect(f'{os.getcwd()}\\test\\obama.jpg')

    # image = cv2.imread(f'{os.getcwd()}\\temp\\temp.jpg')
    # original = cv2.imread(f'{os.getcwd()}\\test\\obama.jpg')
    # # Get the face encodings for the known images
    # image_face_encoding = face_recognition.face_encodings(image, model='large')[0]
    # original_face_encoding = face_recognition.face_encodings(original, model='large')[0]
    # print(f'Shape 1: {image_face_encoding.shape}')
    # print(f'Shape 2: {original_face_encoding.shape}')

    face_distances = face_recognition.face_distance(img_desc, obm_desc)

    print(f'[ IMAGE] - {os.getcwd()}\\{os.listdir()[3]} - Euclidian distance: {face_distances}')
    return face_distances

if __name__ == '__main__':
    print(f'[ INFO ] - {time.ctime(time.time())} - Open dataset')
    data = create_dataset(f'{os.getcwd()}//dataset')

    for element in data:
        print(element)
    # # Открытие тестовой картинки
    # os.chdir('photos')
    # print('[ IMAGE] - My locations:', os.getcwd())
    # # print(os.listdir())
    # image = cv2.imread(f'{os.getcwd()}\\{os.listdir()[3]}')
    # original = cv2.imread(f'{os.getcwd()}\\{os.listdir()[2]}')
    # # Запуск главной функции
    # main(image, original)
