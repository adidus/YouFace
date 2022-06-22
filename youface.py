import os

import moviepy.editor as mp
import youtube_dl

from utils import Cloud, Database, Video


class YouFace:
    def __init__(self, urls: list):
        """
        Class for working with YouTube video
        :param urls: list of youtube urls
        """
        self.urls = urls
        self.__yd = youtube_dl.YoutubeDL()
        self.__cloud = Cloud()
        self.__db = Database()
        self.__urls_info = {}
        self.videos = []

    def download_to_local_video(self):
        """
        Download to local from Youtube
        """
        for url in self.urls:
            result = self.__yd.extract_info(url=url, download=True)
            os.rename(f"{result['title']}-{result['id']}.mp4", f"{result['id']}.mp4")
            self.__urls_info[result.get('id')] = result

    def upload_to_cloud_video(self):
        """
        Upload to cloud videos
        """
        for id_ in self.__urls_info:
            self.__cloud.upload_file(
                upload_path=f"{id_}/{id_}.mp4", filename=f'{id_}.mp4'
            )
            os.remove(f'{id_}.mp4')

    def upload_to_cloud_audio(self):
        """
        Upload to cloud audios
        """
        for id_ in self.__urls_info:
            my_clip = mp.VideoFileClip(f'{id_}.mp4')
            my_clip.audio.write_audiofile(f'{id_}.mp3')
            self.__cloud.upload_file(
                upload_path=f"{id_}/{id_}.mp3", filename=f'{id_}.mp3'
            )
            os.remove(f'{id_}.mp3')

    def upload_to_cloud_dir(self):
        """
        Upload to cloud directory with images
        """
        for id_ in self.__urls_info:
            self.__cloud.upload_directory(
                upload_path=f'{id_}/images', dirname=f'{id_}/images'
            )

    def download_from_cloud(self, id_: str):
        """
        Download from S3 by id
        :param id_: youtube id of video
        """
        self.__cloud.download_file(id_=id_, filename=f'{id_}.mp4')

    def save_frames(self, id_: str = None):
        """
        Save frames with detected faces from video on your local
        :param id_: youtube id of video
        """
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
