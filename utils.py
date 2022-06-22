import os
import sqlite3

import boto3
import cv2
import numpy as np

from config import (
    AWS_SERVER_SECRET_KEY,
    AWS_SERVER_PUBLIC_KEY,
    REGION_NAME,
    BUCKET_NAME,
)


class Cloud:
    def __init__(self):
        self.__s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
            aws_secret_access_key=AWS_SERVER_SECRET_KEY,
            region_name=REGION_NAME,
        )

    def upload_file(self, upload_path: str, filename: str):
        self.__s3.upload_file(
            Filename=filename,
            Bucket=BUCKET_NAME,
            Key=upload_path,
        )

    def upload_directory(self, upload_path: str, dirname: str):
        if os.path.exists(dirname):
            for filename in os.listdir(dirname):
                self.upload_file(
                    f'{upload_path}/{filename}', f'{upload_path}/{filename}'
                )

    def download(self, id_: str, filename: str):
        self.__s3.download_file(
            Filename=filename,
            Bucket=BUCKET_NAME,
            Key=f"{id_}/{filename}",
        )


class Database:
    def __init__(self, db_name: str = 'default'):
        self.__connection = sqlite3.connect(f'{db_name}.sqlite')
        self.__cursor = self.__connection.cursor()

    def save(self, tablename: str = 'videos', data: dict = None, columns: list = None):
        self.__create_table(tablename, columns)
        for key in data:
            columns = [data[key][col] for col in columns]
            columns = '"' + '", "'.join(columns) + '"'
            self.__cursor.execute(
                f'''
                insert into {tablename}
                values ({columns})
            '''
            )
        self.__connection.commit()

    def __create_table(self, tablename: str, columns: list):
        columns = ', '.join(columns)
        self.__cursor.execute(
            f'''
            create table if not exists {tablename}
            ({columns})
        '''
        )


class Video:
    def __init__(self, filename: str):
        self.filename = filename
        self.__cap = cv2.VideoCapture(f'{filename}.mp4')
        self.__cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)
        self.frameCount = int(self.__cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frameWidth = int(self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frameHeight = int(self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.videoFPS = int(self.__cap.get(cv2.CAP_PROP_FPS))
        self.__facemeta = {}
        self.__db = Database()

    def save_frames(self, each_fc: int = 24):
        buf = np.empty(
            (self.frameCount, self.frameHeight, self.frameWidth, 3), np.dtype('uint8')
        )

        fc = 0
        ret = True
        if not os.path.exists(f'{self.filename}'):
            os.mkdir(f'{self.filename}')
            os.mkdir(f'{self.filename}/images')
        while fc < self.frameCount:
            ret, buf[fc] = self.__cap.read()
            cv2.imwrite(f'{self.filename}/images/{fc}.jpg', buf[fc])
            img2, is_face = self.__detect_face(buf[fc])
            cv2.imwrite(f'{self.filename}/images/{fc}_face.jpg', img2)
            fc += each_fc
            self.__facemeta[self.filename] = {
                'name': f'{fc}.jpg',
                'is_face': str(is_face),
            }
            self.__save_meta_to_db()

        self.__cap.release()

    def __save_meta_to_db(self):
        self.__db.save(
            tablename=self.filename, data=self.__facemeta, columns=['name', 'is_face']
        )

    def __detect_face(self, img):
        is_face = False
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            is_face = True
        return img, is_face
