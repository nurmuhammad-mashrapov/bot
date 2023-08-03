import os
import io
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InputFile
from aiogram.utils import executor


# Замените 'YOUR_TELEGRAM_BOT_TOKEN' на ваш токен от @BotFather
TOKEN = '5992491482:AAGp38yYM-uroWtJ_mNeQjmIrmZjPYotklk'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Функция для изменения текста на картинке
# Функция для изменения текста на картинке
def process_image(lines):
    image_width = 500
    image_height = 600
    border_size = 3
    border_color = 'black'
    background_color = 'white'

    # Создаем изображение с белым фоном
    image = Image.new('RGB', (image_width, image_height), color=background_color)

    # Добавляем рамку
    draw = ImageDraw.Draw(image)
    draw.rectangle(
        [border_size, border_size, image_width - border_size, image_height - border_size],
        outline=border_color, width=border_size
    )

    y_offset = 2 * border_size
    font_path = "fonts/Arimo-Regular.ttf"
    font_size = 20
    font = ImageFont.truetype(font_path, font_size)

    # Заменяем пустые строки на строки с информацией
    labels = [
        "Cтатус:     ", "ID операции:     ", "Тип операции:     ", "Детали операции:     ",
        "Дата и время:    ", "Отправитель:     ", "Сумма платежа:     ", "Комиссия:     ", "Валюта:     ", "Итого:     "
    ]

    # Добавляем специальную обработку для первой строки
    first_line = lines.pop(0)
    draw.text((2 * border_size, y_offset), first_line, font=font, fill='black')
    y_offset += 40

    for label, line in zip(labels, lines):
        # Encode the text as UTF-8 to support non-Latin characters
        text_to_draw = f"{label} {line}"
        draw.text((2 * border_size, y_offset), text_to_draw, font=font, fill='black')
        y_offset += 40  # Увеличиваем вертикальное смещение для следующей строки

    return image


# Функция для создания PDF изображения
def create_pdf(image):
    pdf = FPDF()
    pdf.add_page()

    # Сохраняем изображение во временный файл
    image_temp_file = "img.png"
    image.save(image_temp_file)

    # Добавляем изображение в PDF
    pdf.image(image_temp_file, x=10, y=10, w=200)

    # Удаляем временный файл
    os.remove(image_temp_file)

    return pdf

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне данные в нескольких строках, разделяя их переносами, и я сгенерирую для тебя отчет с этими данными в PDF. "
                        "Например, вот так: \n\n"
                        
                        "77774546464\n"
                        "Операция успешна\n"
                        "123456789\n"
                        "Перевод\n"
                        "Перевод по номеру телефона\n"
                        "2023-01-01 12:00:00\n"
                        "3324234234\n"
                        "1000.00\n"
                        "0.00\n"
                        "USD\n"
                        "1000.00\n"
                        )


# Обработчик текстовых сообщений
@dp.message_handler(content_types=types.ContentType.TEXT)
async def process_text(message: types.Message):
    input_text = message.text

    # Разделяем текст на строки
    lines = input_text.split('\n')

    # Создаем изображение с текстом
    image = process_image(lines)

    # Создаем PDF файл с изображением
    pdf = create_pdf(image)

    # Сохраняем PDF в файл и отправляем пользователю
    output_file = "output.pdf"
    pdf.output(output_file)
    with open(output_file, "rb") as f:
        await bot.send_document(message.chat.id, InputFile(f))
    os.remove(output_file)  # Удаляем временный PDF файл

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
