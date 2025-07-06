# -*- coding: utf-8 -*-
import json
import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler,
                          ContextTypes, MessageHandler, filters)

logging.basicConfig(level=logging.INFO)

TOKEN = "7912306325:AAHVcIxD9aCCth8WzrZuLjGX1LRxltwDN-E"
DATA_FILE = "user_data.json"

# === КАТАЛОГ КАРТ ===
catalog = {
    "Солнце и драйв": ["Лучик счастья", "Ныряем!", "Милый ракурс", "То, что надо", "Наряжаемся",
                      "Пляжный покой", "Пляжные локоны", "В ногу", "На память", "Золотая карта Тропик"],
    "Якорь": ["Чистый горизонт", "Солнечные ванны", "Грибной товарищ", "Крутая экипир.", "Дрейф",
             "Команда", "Грёзы в гамаке", "Ветерок", "Лежебока", "Золотая карта у бассейна"],
    "Сёрф зона": ["Загорелый", "Лови волну!", "Улыбка сёрфера", "Крутая волна", "Зов моря",
                 "Доска на готове", "Прилив", "Ловец волн", "Ритм моря", "Золотая карта Волнорез: 2"],
    "Горки и волны": ["День в парке", "Наперегонки!", "Проездом", "Семья на воде", "На закорках",
                    "На глубину", "На скорости", "Мокро и весело", "Просто кайф", "Золотая карта Горка: 3"],
    "Загораем": ["Под защитой", "Стильные очки", "Не смазать!", "Сияю", "К загару готов",
               "Кайфуй!", "Золотой блеск", "В пути", "Дрёма и шик", "Золотая карта Загар: 4"],
    "Чилл у воды": ["Мило и свежо", "Быстро нырнул", "Неон ночи", "Супер компания", "Катимся",
                 "У воды", "Плюх!", "В пузырях", "Водная банда", "Золотая карта Всегда молод: 5"],
    "Большая поездка": ["Круиз", "С семьей", "По дорогам", "Внезапное шоу", "По городу",
                     "Берег светится", "Вид с лагеря", "На природе", "Полночный микс", "Золотая карта В пути: 6"],
    "Готовка во дворе": ["Вечеринка!", "Заводной!", "Добавку!", "Гриль и чилл", "Вишенка",
                      "Пикник", "Всё что надо", "Да, солёные!", "Лобстер пати", "Золотая карта Вкусняшка: 7"],
    "Летний десерт": ["Крутой бизнес", "Фисташковая любовь", "Готов подавать", "Сложный выбор", "Коротаем время",
                   "Всё что надо", "Ещё шариков!", "Лакомство", "До встречи", "Золотая карта Рожок патр.: 8"],
    "Остываем": ["Болтаем", "Дрыхну", "Покой души", "За снеками", "Приятель по сну",
              "Лёгкий день", "Выдох", "Семейный рецепт", "Классика!", "Золотая карта Фанаты: 9"],
    "Морской драйв": ["Для скорости", "Шар-парус", "Сторонись", "Джет-нырок", "Держись!",
                   "Лёгкая дорога", "Гонка!", "Высоко", "Золотая карта Всадник: шарик", "Золотая карта Взлёт"],
    "Глоток лета": ["Сочно и свежо", "Я защищу!", "Тропики", "Делимся", "Сладкая станция",
                 "Фруктовая пати", "Фруктик", "Катим!", "Золотая карта Ура!: +2", "Золотая карта Сладкая жизнь"],
    "Морские друзья": ["Соня-тюлень", "Выдра рада", "Гид с трубкой", "Готов дунуть", "Новые друзья",
                   "Прямо плывёт", "В волнах", "Золотая карта Друзья: обратно", "Золотая карта Дельфин ныряет", "Золотая карта Жизнь рифа"],
    "Птички на пляже": ["Богатый голубь", "Вкусняшка", "Проверяю воду", "Пламя фламинго", "Вдох...",
                    "В строю", "Яркость", "Золотая карта Бунтарь: скип", "Золотая карта Смотри!", "Золотая карта Кормёжка"],
    "Сладкая жизнь": ["Пляжный день", "Друг для загара", "Тень на двоих", "На страже", "Солнечный поцелуй",
                   "Кайфую", "Смотрю закат", "Золотая карта Лежни: дикая", "Золотая карта Скоро вернусь", "Золотая карта Любуясь видом"],
    "Клад у моря": ["Подбери меня", "Жемчужная", "Отшельник", "Идеально", "Сандалии",
                 "Белковый обед", "Музыка ветра", "Золотая карта Краски: +4", "Золотая карта Мини-сокровища", "Золотая карта Красота моря"],
    "Адреналин": ["Играем!", "Волейбол", "Поднимай!", "Летающий диск", "Апорт!",
               "Подача!", "Пикбол", "Золотая карта Розыгрыш!: Дикий удар", "Золотая карта Фрисби", "Золотая карта Бой у сетки"],
    "Чудеса воды": ["По течению", "Ускоряемся", "На течении", "Мини-мир", "Витрина",
                 "Кафе у моря", "Золотая карта Нырок и бросок: Дикий ужас", "Золотая карта В аквариуме!", "Золотая карта Мелодия моря", "Золотая карта В туннель"]
}

# === Построение карты ID → (набор, карта)
card_id_map = {}
id_counter = 1
for set_name, cards in catalog.items():
    for card in cards:
        card_id = f"id{id_counter}"
        card_id_map[card_id] = (set_name, card)
        id_counter += 1

# === ЗАГРУЗКА/СОХРАНЕНИЕ ДАННЫХ ===
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

user_data = load_data()

# === Команды меню ===
async def set_bot_commands(app):
    commands = [
        BotCommand("start", "Начать работу"),
        BotCommand("mycards", "Показать мои карты"),
        BotCommand("want", "Добавить карту в список желаемого"),
        BotCommand("whohas", "Кто имеет такую карту"),
        BotCommand("offer", "Предложить обмен"),
        BotCommand("clearcards", "Удалить все мои карты")
    ]
    await app.bot.set_my_commands(commands)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    user_data.setdefault(user_id, {})
    user_data[user_id]["name"] = user.first_name
    save_data(user_data)

    keyboard = []
    row = []
    for i, key in enumerate(catalog.keys(), 1):
        row.append(InlineKeyboardButton(text=key, callback_data=f"set:{key}"))
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для обмена картами УНО. Вот что я умею:\n\n"
        "- /mycards — показать твои карты\n"
        "- /want [карта] — хочу эту карту\n"
        "- /whohas [карта] — кто имеет такую карту\n"
        "- /offer [твоя_карта] [нужная_карта] — предложить обмен\n"
        "- /clearcards — удалить все свои карты\n\n"
        "Выбери набор, чтобы отметить карты:",
        reply_markup=reply_markup
    )

# === CALLBACK ===
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(query.from_user.id)

    if data.startswith("set:"):
        set_name = data[4:]
        keyboard = []
        for card in catalog[set_name]:
            for cid, (s, c) in card_id_map.items():
                if s == set_name and c == card:
                    keyboard.append([InlineKeyboardButton(card, callback_data=f"card:{cid}")])
                    break
        await query.edit_message_text(f"Карты набора \"{set_name}\":", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("card:"):
        card_id = data[5:]
        set_name, card_name = card_id_map.get(card_id, (None, None))
        if not card_name:
            await query.edit_message_text("Ошибка: неизвестная карта.")
            return
        user_cards = user_data.setdefault(user_id, {}).setdefault("cards", {})
        count = user_cards.get(card_name, 0) + 1
        user_cards[card_name] = count
        save_data(user_data)
        await query.edit_message_text(f"Добавлена карта: {card_name} (всего: {count})")

# === /mycards ===
async def my_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    cards = user_data.get(user_id, {}).get("cards", {})
    if not cards:
        await update.message.reply_text("У тебя пока нет карт. Выбери в каталоге, какие у тебя есть.")
        return
    text = "Твои карты:\n" + "\n".join(f"{k} — {v} шт." for k, v in cards.items())
    await update.message.reply_text(text)

# === /clearcards ===
async def clear_cards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data.setdefault(user_id, {})["cards"] = {}
    save_data(user_data)
    await update.message.reply_text("Все карты удалены.")

# === /want ===
async def want(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if len(context.args) < 1:
        await update.message.reply_text("Укажи, какую карту ты хочешь. Например: /want Лучик счастья")
        return
    card = " ".join(context.args)
    user_data.setdefault(user_id, {}).setdefault("wants", []).append(card)
    save_data(user_data)

    notified = 0
    for uid, data in user_data.items():
        if uid == user_id:
            continue
        if card in data.get("cards", {}):
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=f"Пользователь @{update.effective_user.username or update.effective_user.first_name} интересуется картой: {card}"
                )
                notified += 1
            except:
                pass
    await update.message.reply_text(f"Желание записано. Уведомлено: {notified} пользователей.")

# === /whohas ===
async def who_has(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Укажи карту. Например: /whohas Лучик счастья")
        return
    card = " ".join(context.args)
    owners = []
    for uid, data in user_data.items():
        if card in data.get("cards", {}):
            owners.append(uid)
    if not owners:
        await update.message.reply_text("Никто пока не имеет такую карту.")
    else:
        msg = "Карту имеют:\n"
        for uid in owners:
            name = uid
            try:
                name = f"@{(await context.bot.get_chat(uid)).username}"
            except:
                pass
            msg += f"{name}\n"
        await update.message.reply_text(msg)

# === /offer ===
async def offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Формат: /offer [твоя карта] [нужная карта]")
        return
    user_id = str(update.effective_user.id)
    give = context.args[0]
    want = " ".join(context.args[1:])
    user_data.setdefault(user_id, {}).setdefault("offers", []).append({"give": give, "want": want})
    save_data(user_data)

    notified = 0
    for uid, data in user_data.items():
        if uid == user_id:
            continue
        if want in data.get("cards", {}):
            try:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Принять обмен", callback_data=f"accept:{user_id}|{give}|{want}")]
                ])
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=f"@{update.effective_user.username or update.effective_user.first_name} предлагает обмен: 🃏 {give} на {want}",
                    reply_markup=keyboard
                )
                notified += 1
            except:
                pass
    await update.message.reply_text(f"Предложение отправлено. Уведомлено: {notified} пользователей.")

# === ПРИНЯТИЕ ОБМЕНА ===
async def handle_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data[7:].split("|")
    from_user_id, give, want = data
    to_user_id = str(query.from_user.id)

    from_cards = user_data.get(from_user_id, {}).get("cards", {})
    to_cards = user_data.get(to_user_id, {}).get("cards", {})

    if from_cards.get(give, 0) < 1 or to_cards.get(want, 0) < 1:
        await query.edit_message_text("Обмен невозможен: кто-то больше не имеет нужной карты.")
        return

    from_cards[give] -= 1
    to_cards[want] -= 1
    from_cards[want] = from_cards.get(want, 0) + 1
    to_cards[give] = to_cards.get(give, 0) + 1
    save_data(user_data)

    await context.bot.send_message(chat_id=int(from_user_id),
        text=f"🎉 Обмен подтверждён! Вы получили карту: {want}, отдали: {give}.")
    await query.edit_message_text("🎉 Обмен совершен!")

# === MAIN ===
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mycards", my_cards))
app.add_handler(CommandHandler("want", want))
app.add_handler(CommandHandler("whohas", who_has))
app.add_handler(CommandHandler("offer", offer))
app.add_handler(CommandHandler("clearcards", clear_cards))
app.add_handler(CallbackQueryHandler(handle_accept, pattern="^accept:"))
app.add_handler(CallbackQueryHandler(handle_callback))  # обязательно в конце

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_bot_commands(app))
    app.run_polling()
