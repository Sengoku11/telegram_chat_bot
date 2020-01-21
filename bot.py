import telebot
import os
import requests
import subprocess
import urllib.request
import cv2
import sys

API_TOKEN = 'INSERT APIT_TOKEN'
bot = telebot.TeleBot(API_TOKEN)

DOWNLOADS_PATH = os.path.join('Downloads')
if not os.path.isdir(DOWNLOADS_PATH):
    os.makedirs(DOWNLOADS_PATH)


@bot.message_handler(content_types=['voice'])
def get_voice_message(message):
    chat_id = message.from_user.id
    voice_id = message.voice.file_id
    voice_info = bot.get_file(voice_id)
    download_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(
        API_TOKEN, voice_info.file_path)

    # Download voice message
    uid_path = os.path.join(DOWNLOADS_PATH, "uid_"+str(chat_id))
    if not os.path.isdir(uid_path):
        os.makedirs(uid_path)
    voice_path = os.path.join(uid_path, 'voice.ogg')
    urllib.request.urlretrieve(download_url, voice_path)

    # Count .wav files
    audios = [filename for filename in os.listdir(
        uid_path) if filename.endswith('.wav')]
    next_id = len(audios)

    # Covert voice to audio
    output_path = os.path.join(
        uid_path, 'audio_message_{}.wav'.format(next_id))
    process = subprocess.run(['ffmpeg', '-i', voice_path, output_path])
    if process.returncode != 0:
        bot.send_message(message.from_user.id,
                         "Хуйня какая-то")

    # Send back .wav
    audio = open(output_path, 'rb')
    bot.send_audio(chat_id, audio)


def detect_face(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faceCascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30)
    )
    return len(faces) > 0


@bot.message_handler(content_types=['photo'])
def get_photo(message):
    chat_id = message.from_user.id
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        download_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(
            API_TOKEN, file_info.file_path)

        # Download photo
        uid_path = os.path.join(DOWNLOADS_PATH, "uid_"+str(chat_id))
        if not os.path.isdir(uid_path):
            os.makedirs(uid_path)
        file_path = os.path.join(uid_path, 'photo.png')
        urllib.request.urlretrieve(download_url, file_path)

        # Face detection

        if detect_face(file_path):
            photos = [filename for filename in os.listdir(
                uid_path) if filename.endswith('.png')]
            next_id = len(photos)
            output_path = os.path.join(
                uid_path, 'photo_{}.png'.format(next_id))
            urllib.request.urlretrieve(download_url, output_path)
            photo = open(output_path, 'rb')
            bot.send_photo(chat_id, photo)
            bot.send_message(message.from_user.id,
                             "Красивое лицо, сохраним")
        else:
            bot.send_message(message.from_user.id,
                             "Тут нет лица")
    except:
        bot.send_message(message.from_user.id,
                         "Попробуй другое фото")


bot.polling(none_stop=True, interval=0)
