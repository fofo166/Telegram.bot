post = instaloader.Post.from_shortcode(insta_loader.context, url.split("/")[-2])
            if post.is_video:
                insta_loader.download_post(post, target="instagram_media")
                await update.message.reply_video(video=open(f"instagram_media/{post.shortcode}.mp4", 'rb'))
            else:
                insta_loader.download_post(post, target="instagram_media")
                await update.message.reply_photo(photo=open(f"instagram_media/{post.shortcode}.jpg", 'rb'))
            os.remove(f"instagram_media/{post.shortcode}.mp4" if post.is_video else f"instagram_media/{post.shortcode}.jpg")
            await update.message.reply_text("تم تنزيل المحتوى بنجاح! 🎉")
        except Exception as e:
            await update.message.reply_text(f'حدث خطأ أثناء تنزيل المحتوى من Instagram: {e}')
    else:
        await update.message.reply_text(
            f"عذرًا، يجب عليك الانضمام إلى القناة التالية لاستخدام البوت:\n\n{REQUIRED_CHANNEL}\n\n"
            "بعد الانضمام، أرسل الرابط مرة أخرى."
        )

# دالة لتنزيل فيديو من Facebook
async def download_facebook_video(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    user_id = update.message.from_user.id
    if await is_user_member(user_id, context):
        try:
            await update.message.reply_text("جاري تنزيل الفيديو من Facebook... ⏳")
            
            # تهيئة yt-dlp
            ydl_opts = {
                'format': 'best',  # أفضل جودة متاحة
                'outtmpl': 'facebook_media/%(title)s.%(ext)s',  # حفظ الملف في مجلد facebook_media
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)

            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)
            await update.message.reply_text("تم تنزيل الفيديو بنجاح! 🎉")
        except Exception as e:
            await update.message.reply_text(f'حدث خطأ أثناء تنزيل الفيديو من Facebook: {e}')
    else:
        await update.message.reply_text(
            f"عذرًا، يجب عليك الانضمام إلى القناة التالية لاستخدام البوت:\n\n{REQUIRED_CHANNEL}\n\n"
            "بعد الانضمام، أرسل الرابط مرة أخرى."
        )

# دالة لمعالجة الرسائل النصية
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if await is_user_member(user_id, context):
        text = update.message.text

        # تحسين التعبيرات العادية
        youtube_regex = r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+"
        instagram_regex = r"(https?://)?(www\.)?instagram\.com/(p|reel)/[\w-]+"
        facebook_regex = r"(https?://)?(www\.)?facebook\.com/.+/videos/\d+"

        if re.match(youtube_regex, text):
            await download_youtube_video(update, context, text)
        elif re.match(instagram_regex, text):
            await download_instagram_media(update, context, text)
        elif re.match(facebook_regex, text):
            await download_facebook_video(update, context, text)
        else:
            await update.message.reply_text("الرابط غير مدعوم. أرسل رابط فيديو من YouTube أو Instagram أو Facebook.")
    else:
        await update.message.reply_text(
            f"عذرًا، يجب عليك الانضمام إلى القناة التالية لاستخدام البوت:\n\n{REQUIRED_CHANNEL}\n\n"
            "بعد الانضمام، أرسل الرابط مرة أخرى."
        )

def main():
    # إنشاء تطبيق البوت
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # تعريف الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # معالجة الرسائل النصية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # بدء البوت
    application.run_polling()

if name == 'main':
    main()