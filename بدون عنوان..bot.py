from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os
from pytube import YouTube
from instaloader import Instaloader, Post, Profile

TOKEN = '7467852528:AAEQCI-cZjFk2QrtbDrv2fk91AwFLbiPIN0'

def download_youtube_video(url, output_path='video.mp4'):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    stream.download(output_path=output_path)
    return output_path

def download_youtube_audio(url, output_path='audio.mp3'):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(output_path=output_path)
    return output_path

def download_instagram_media(url):
    L = Instaloader()
    shortcode = url.split("/p/")[1].split("/")[0]
    post = Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target='instagram')
    return f'instagram/{post.owner_username}_{post.shortcode}'

def download_instagram_stories(username):
    L = Instaloader()
    profile = Profile.from_username(L.context, username)
    for story in L.get_stories([profile.userid]):
        for item in story.get_items():
            L.download_storyitem(item, target=f'instagram/{username}')

def start(update: Update, context: CallbackContext):
    update.message.reply_text('مرحبًا! أرسل لي رابطًا من يوتيوب أو إنستغرام وسأحاول تنزيله لك.')

def help(update: Update, context: CallbackContext):
    update.message.reply_text('الأوامر المتاحة:\n/start - بدء البوت\n/help - عرض الأوامر')

def about(update: Update, context: CallbackContext):
    update.message.reply_text('أنا بوت لتنزيل المحتوى من يوتيوب وإنستغرام.')

def handle_message(update: Update, context: CallbackContext):
    url = update.message.text
    try:
        if 'youtube.com' in url or 'youtu.be' in url:
            update.message.reply_text('جارٍ تنزيل الفيديو من يوتيوب...')
            video_path = download_youtube_video(url)
            update.message.reply_video(video=open(video_path, 'rb'))
            os.remove(video_path)
        elif 'instagram.com' in url:
            update.message.reply_text('جارٍ تنزيل المحتوى من إنستغرام...')
            media_path = download_instagram_media(url)
            if os.path.exists(media_path):
                for file in os.listdir(media_path):
                    if file.endswith('.mp4'):
                        update.message.reply_video(video=open(os.path.join(media_path, file), 'rb'))
                    elif file.endswith('.jpg'):
                        update.message.reply_photo(photo=open(os.path.join(media_path, file), 'rb'))
                for file in os.listdir(media_path):
                    os.remove(os.path.join(media_path, file))
                os.rmdir(media_path)
            else:
                update.message.reply_text('لم أتمكن من تنزيل المحتوى.')
        else:
            update.message.reply_text('الرابط غير مدعوم. يرجى إرسال رابط من يوتيوب أو إنستغرام.')
    except Exception as e:
        update.message.reply_text(f'حدث خطأ: {e}')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if name == 'main':
    main()
