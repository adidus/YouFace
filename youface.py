import os

import youtube_dl

from utils import Cloud, Database, Video


class YouFace:
    def __init__(self, urls: list):
        self.urls = urls
        self.__yd = youtube_dl.YoutubeDL()
        self.__cloud = Cloud()
        self.__db = Database()
        self.__urls_info = {}
        self.videos = []

    def download_to_local_video(self):
        for url in self.urls:
            result = self.__yd.extract_info(url=url, download=True)
            os.rename(f"{result['title']}-{result['id']}.mp4", f"{result['id']}.mp4")
            self.__urls_info[result.get('id')] = result

    def upload_to_cloud_video(self):
        for id_ in self.__urls_info:
            self.__cloud.upload_file(
                upload_path=f"{id_}/{id_}.mp4", filename=f'{id_}.mp4'
            )
            os.remove(f'{id_}.mp4')

    def upload_to_cloud_dir(self):
        for id_ in self.__urls_info:
            self.__cloud.upload_directory(
                upload_path=f'{id_}/images', dirname=f'{id_}/images'
            )

    def download_from_cloud(self, id_: str):
        self.__cloud.download(id_=id_, filename=f'{id_}.mp4')

    def save_frames(self, id_: str = None):
        if not id_:
            for id_ in self.__urls_info:
                vd = Video(id_)
                vd.save_frames()
        else:
            vd = Video(id_)
            vd.save_frames()

    def save_metadata(self):
        self.__db.save(
            tablename='videos', data=self.__urls_info, columns=['id', 'webpage_url']
        )
