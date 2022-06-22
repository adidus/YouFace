from youface import YouFace


def main():
    stop = False
    while True and not stop:
        print('Input your URL --------->>> ')
        #     url_input = 'https://www.youtube.com/watch?v=fyRt5yWETJg'
        url_input = input()
        youface = YouFace([url_input])
        youface.download_to_local_video()
        youface.upload_to_cloud_audio()
        youface.upload_to_cloud_video()
        print('Input id for download --------->>> ')
        url_id = input()
        youface.download_from_cloud(url_id)
        youface.save_frames()
        youface.upload_to_cloud_dir()
        youface.save_metadata()
        print('Any button+return for exit:')
        stop = input()


if __name__ == '__main__':
    main()
