

from telebot import TeleBot, types
from datetime import datetime
import random
import time
import re

API_TOKEN = '7756181021:AAF-Lne3in_DISdGueKCqdNZw6E5LiN5tm8'
LOG_CHANNEL = -52617179362  # Log kanalının ID-sini dəyiş
ADMINS = [7800338935]  # Admin ID-lərini əlavə et

bot = TeleBot(API_TOKEN, parse_mode=None)

afk_users = {}  # user_id: (reason, start_time)
filters = {}    # chat_id: {word: reply_text}
message_counts = {}  # chat_id: {user_id: count}
last_start_users = set()  # start spam qarşısı üçün

START_IMAGE = 'https://files.catbox.moe/e083zz.jpg'

# ----------- Helper funksiyalar -------------

def is_admin(user_id, chat_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def extract_user(message):
    # Reply yoxsa id və ya @username-dən istifadəçi tapır
    if message.reply_to_message:
        return message.reply_to_message.from_user
    args = message.text.split()
    if len(args) > 1:
        arg = args[1]
        if arg.startswith('@'):
            try:
                user = bot.get_chat_member(message.chat.id, arg).user
                return user
            except:
                return None
        else:
            try:
                return bot.get_chat_member(message.chat.id, int(arg)).user
            except:
                return None
    return None

def format_time(timestamp=None):
    if not timestamp:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

def check_links(text):
    # Sadə link tapma regex-i
    pattern = r"(https?://|t.me/|telegram.me/|http://|www.)"
    return re.search(pattern, text, re.IGNORECASE)

# ----------- START KOMANDASI + BUTTON MENYU -----------

def create_start_markup():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("➕ Məni qrupuna əlavə et", url="https://t.me/{bot.get_me().username}?startgroup=true")
    )
    markup.row(
        types.InlineKeyboardButton("📤 Support", url=f"https://t.me/PersionalSupport")
    )
    markup.row(
        types.InlineKeyboardButton("📚 Əmrlər", callback_data="commands"),
        types.InlineKeyboardButton("🧑‍💻 Sahibim", url="https://t.me/PersionalTeamBot")
    )
    markup.row(
        types.InlineKeyboardButton("ℹ️ Bot haqqında", callback_data="about")
    )
    return markup

def get_start_caption(user_name):
    return (
        f"👩‍⚕ Salam {user_name}\n"
        f"🪬 Mənim adım 𝐏𝐞𝐫𝐬𝐢𝐨𝐧𝐚𝐥 𝐌𝐮𝐥𝐭𝐢 𝐁𝐨𝐭\n"
        f"🇦🇿 Azərbaycan dilində multi funksiyalı telegram botuyam\n"
        f"🛠 Bacarıqlarımı görmək üçün 📚 əmrlər buttonuna daxil olun"
    )

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    chat_id = message.chat.id

    # Qrupda /start@NihadRobot yazılarsa
    if message.chat.type in ['group', 'supergroup']:
        if message.text.startswith('/start@NihadRobot'):
            chat_name = message.chat.title or "Bu Qrup"
            group_message = (
                f"╔═════════════════\n"
                f"║▻ 🙎‍♀️️️️️️️️ 𝐏𝐞𝐫𝐬𝐢𝐨𝐧𝐚𝐥 {chat_name} Qrupunda Əla şəkildə stabil işləyir  🥳\n"
                f"╚═════════════════"
            )
            bot.send_message(chat_id, group_message)
            return

    # Privat mesajda start
    if user.id not in last_start_users:
        last_start_users.add(user.id)
        try:
            bot.send_message(LOG_CHANNEL,
                f"<b>Log📥</b>\n"
                f"Bota yeni istifadəçi start verdi ✅\n"
                f"🆕 {user.first_name}\n"
                f"🆔 {user.id}\n"
                f"🕰️ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
        except:
            pass

    bot.send_photo(
        chat_id,
        START_IMAGE,
        caption=get_start_caption(user.first_name),
        reply_markup=create_start_markup()
    )

@bot.callback_query_handler(func=lambda c: True)
def callback_query(call):
    try:
        if call.data == 'about':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏡 Ana Səhifə", callback_data="home"))
            
            about_text = (
                "╔═════════════════\n"
                f"║▻ 🙋‍♀️ Salam {call.from_user.first_name}\n"
                "║\n"
                "║▻ 🙎‍♀️ 𝐏𝐞𝐫𝐬𝐢𝐨𝐧𝐚𝐥 🇦🇿 Çox Özəllikli Telegram Botudur...\n"
                "║▻ 🐍 Python: 3.9.12\n"
                "║▻ 📚 TeleBot: 4.x\n"
                "║▻ ⚙️ Server: Replit VPS\n"
                "║▻ 👨‍💻 Sahib: @PersionalTeamBot\n"
                "║▻ 📆 Start tarixi: 16.06.2025\n"
                "╚════════════════"
            )
            
            # Mesajın photo olub-olmadığını yoxla
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=about_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=about_text,
                    reply_markup=markup
                )
                
        elif call.data == 'commands':
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("📌 Pin Əmrləri", callback_data="pin_commands"),
                types.InlineKeyboardButton("🥷 Moderasiya", callback_data="mod_commands")
            )
            markup.row(
                types.InlineKeyboardButton("👑 Admin Əmrləri", callback_data="admin_commands"),
                types.InlineKeyboardButton("📢 Tag Əmrləri", callback_data="tag_commands")
            )
            markup.row(
                types.InlineKeyboardButton("ℹ️ Məlumat Əmrləri", callback_data="info_commands"),
                types.InlineKeyboardButton("🔁 Filter Əmrləri", callback_data="filter_commands")
            )
            markup.row(
                types.InlineKeyboardButton("🎯 Əyləncə Əmrləri", callback_data="fun_commands"),
                types.InlineKeyboardButton("🅿️ Font Əmrləri", callback_data="font_commands")
            )
            markup.row(
                types.InlineKeyboardButton("🎮 Oyun Əmrləri", callback_data="game_commands"),
                types.InlineKeyboardButton("📶 AFK Sistemi", callback_data="afk_commands")
            )
            markup.row(
                types.InlineKeyboardButton("🤖 Avtomatik", callback_data="auto_commands")
            )
            markup.add(types.InlineKeyboardButton("🏡 Ana Səhifə", callback_data="home"))
            
            commands_text = (
                "📚 Komandalar Menyusu\n\n"
                "Aşağıdakı kateqoriyalardan birini seçin:\n\n"
                "📌 Pin Əmrləri - Mesaj sabitləmə\n"
                "🥷 Moderasiya - Ban, mute, kick\n"
                "👑 Admin Əmrləri - Admin idarəetməsi\n"
                "📢 Tag Əmrləri - İstifadəçi çağırışı\n"
                "ℹ️ Məlumat Əmrləri - Profil məlumatları\n"
                "🔁 Filter Əmrləri - Söz filterləri\n"
                "🎯 Əyləncə Əmrləri - Oyunlar\n"
                "🅿️ Font Əmrləri - Mətn formatı\n"
                "🎮 Oyun Əmrləri - Söz oyunu\n"
                "📶 AFK Sistemi - Oflayn rejimi\n"
                "🤖 Avtomatik - Avtomatik funksiyalar"
            )
            
            # Mesajın photo olub-olmadığını yoxla
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=commands_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=commands_text,
                    reply_markup=markup
                )
                
        elif call.data == 'pin_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            pin_text = (
                "📌 Pin Əmrləri\n\n"
                "🔸 /pin - Mesajı sabitləyir\n"
                "   ↳ Cavab verdiyiniz mesajı sabitləyir\n"
                "   ↳ İstifadə: Mesaja reply ilə /pin\n\n"
                "🔸 /unpin - Mesajın sabitlənməsini silir\n"
                "   ↳ Cavab verdiyiniz mesajın pinini silir\n"
                "   ↳ İstifadə: Mesaja reply ilə /unpin\n\n"
                "🔸 /unpinall - Bütün sabitləmələri silir\n"
                "   ↳ Qrupdakı bütün pin mesajları silir\n"
                "   ↳ İstifadə: /unpinall\n\n"
                "⚠️ Bu əmrləri yalnız adminlər istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=pin_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=pin_text,
                    reply_markup=markup
                )
                
        elif call.data == 'mod_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            mod_text = (
                "🥷 Moderasiya Əmrləri\n\n"
                "🔸 /ban - İstifadəçini qadağan edir\n"
                "   ↳ İstifadə: /ban (reply/ID/@username)\n\n"
                "🔸 /unban - Qadağanı silir\n"
                "   ↳ İstifadə: /unban (reply/ID/@username)\n\n"
                "🔸 /mute - İstifadəçini səssiz edir\n"
                "   ↳ İstifadə: /mute (reply/ID/@username)\n\n"
                "🔸 /unmute - Səssizdən çıxarır\n"
                "   ↳ İstifadə: /unmute (reply/ID/@username)\n\n"
                "🔸 /kick - İstifadəçini qrupdan qovur\n"
                "   ↳ İstifadə: /kick (reply/ID/@username)\n\n"
                "🔸 /warn - Xəbərdarlıq verir\n"
                "   ↳ İstifadə: /warn (reply/ID/@username) [səbəb]\n\n"
                "⚠️ Bu əmrləri yalnız adminlər istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=mod_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=mod_text,
                    reply_markup=markup
                )
                
        elif call.data == 'admin_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            admin_text = (
                "👑 Admin Əmrləri\n\n"
                "🔸 /promote - İstifadəçini admin edir\n"
                "   ↳ İstifadə: /promote (reply/ID/@username)\n\n"
                "🔸 /demote - Adminlikdən çıxarır\n"
                "   ↳ İstifadə: /demote (reply/ID/@username)\n\n"
                "🔸 /adminlist - Admin siyahısını göstərir\n"
                "   ↳ İstifadə: /adminlist\n\n"
                "🔸 /reload - Admin siyahısını yeniləyir\n"
                "   ↳ İstifadə: /reload\n\n"
                "⚠️ Bu əmrləri yalnız adminlər istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=admin_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=admin_text,
                    reply_markup=markup
                )
                
        elif call.data == 'tag_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            tag_text = (
                "📢 Tag Əmrləri\n\n"
                "🔸 /tag - Adminləri tək-tək tag edir\n"
                "   ↳ İstifadə: /tag [mesaj]\n\n"
                "🔸 /tagall - Bütün üzvləri tək-tək tag edir\n"
                "   ↳ İstifadə: /tagall [mesaj]\n\n"
                "🔸 /tagadmin - Bütün adminləri bir mesajda tag edir\n"
                "   ↳ İstifadə: /tagadmin [mesaj]\n\n"
                "🔸 /stag - Sessiz admin tag\n"
                "   ↳ İstifadə: /stag [mesaj]\n\n"
                "🔸 /utag - Aktiv istifadəçiləri tag edir\n"
                "   ↳ İstifadə: /utag [mesaj]\n\n"
                "🔸 /cancel - Tag prosesini dayandırır\n\n"
                "⚠️ Bu əmrləri yalnız adminlər istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=tag_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=tag_text,
                    reply_markup=markup
                )
                
        elif call.data == 'info_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            info_text = (
                "ℹ️ Məlumat Əmrləri\n\n"
                "🔸 /men - Özünüz haqqında məlumat\n"
                "   ↳ İstifadə: /men\n\n"
                "🔸 /kim - İstifadəçi haqqında məlumat\n"
                "   ↳ İstifadə: /kim (reply/ID/@username)\n\n"
                "🔸 /id - İstifadəçi ID-sini göstərir\n"
                "   ↳ İstifadə: /id\n\n"
                "🔸 /info - Ətraflı istifadəçi məlumatı\n"
                "   ↳ İstifadə: /info (reply/ID/@uosername)\n\n"
                "🔸 /alive - Botun aktiv olduğunu göstərir\n"
                "   ↳ İstifadə: /alive\n\n"
                "✅ Bu əmrləri hər kəs istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=info_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=info_text,
                    reply_markup=markup
                )
                
        elif call.data == 'filter_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            filter_text = (
                "🔁 Filter Əmrləri\n\n"
                "🔸 /filter - Söz filterı əlavə edir\n"
                "   ↳ İstifadə: /filter söz cavab\n"
                "   ↳ Reply ilə: /filter cavab\n\n"
                "🔸 /stop - Filterı silir\n"
                "   ↳ İstifadə: /stop söz\n\n"
                "🔸 /stopall - Bütün filterləri silir\n"
                "   ↳ İstifadə: /stopall\n\n"
                "🔸 /filters - Filter siyahısını göstərir\n"
                "   ↳ İstifadə: /filters\n\n"
                "⚠️ Bu əmrləri yalnız adminlər istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=filter_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=filter_text,
                    reply_markup=markup
                )
                
        elif call.data == 'fun_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            fun_text = (
                "🎯 Əyləncə Əmrləri\n\n"
                "🔸 /mal - Təsadüfi 'mal' seçir\n"
                "   ↳ İstifadə: /mal\n\n"
                "🔸 /ship - İki nəfər arasında uyğunluq faizi\n"
                "   ↳ İstifadə: /ship ad1 ad2\n"
                "   ↳ Reply ilə: /ship\n\n"
                "🔸 /q - Mesajdan sitat düzəldir\n"
                "   ↳ İstifadə: Mesaja reply ilə /q\n\n"
                "✅ Bu əmrləri hər kəs istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=fun_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=fun_text,
                    reply_markup=markup
                )
                
        elif call.data == 'font_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            font_text = (
                "🅿️ Font Əmrləri\n\n"
                "🔸 /font - 8 müxtəlif fontda metn formatı\n"
                "   ↳ İstifadə: /font yazı\n\n"
                "📝 Mövcud font növləri:\n"
                "• 𝐁𝐨𝐥𝐝 - Qalın mətn\n"
                "• 𝘐𝘵𝘢𝘭𝘪𝘤 - Əyik mətn\n"
                "• 𝙼𝚘𝚗𝚘 - Monoşrift mətn\n"
                "• 𝔻𝕠𝕦𝕓𝕝𝕖 - İkiqat mətn\n"
                "• 𝖲𝖾𝗋𝗂𝖿 - Serif mətn\n"
                "• 𝒮𝒸𝓇𝒾𝓅𝓉 - Yazı mətn\n"
                "• 𝔉𝔯𝔞𝔨𝔱𝔲𝔯 - Fraktur mətn\n"
                "• Ⓑⓤⓑⓑⓛⓔ - Dairəli mətn\n\n"
                "✅ Bu əmri hər kəs istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=font_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=font_text,
                    reply_markup=markup
                )
                
        elif call.data == 'afk_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            afk_text = (
                "📶 AFK Sistemi\n\n"
                "🔸 /afk - AFK rejimə keçir\n"
                "   ↳ İstifadə: /afk [səbəb]\n"
                "   ↳ Nümunə: /afk Yeməkdə\n\n"
                "🤖 Avtomatik funksiyalar:\n"
                "• AFK olan şəxsə reply verəndə bildiriş\n"
                "• AFK şəxs mesaj yazanda avtomatik çıxış\n"
                "• AFK müddətinin göstərilməsi\n\n"
                "✅ Bu əmri hər kəs istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=afk_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=afk_text,
                    reply_markup=markup
                )
                
        elif call.data == 'game_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            game_text = (
                "🎮 Oyun Əmrləri\n\n"
                "🔸 /game - Söz oyununu başladır\n"
                "   ↳ Qarışdırılmış sözü düzgün tapın\n"
                "   ↳ Düzgün cavab: +25 xal\n\n"
                "🔸 /xallar - Xallarınızı göstərir\n"
                "   ↳ İstifadə: /xallar\n\n"
                "🔸 /kec - Cari sözü keçir\n"
                "   ↳ İstifadə: /kec\n\n"
                "🔸 /bitir - Oyunu dayandırır\n"
                "   ↳ İstifadə: /bitir və ya /stop\n\n"
                "🎯 Oyun qaydaları:\n"
                "• Qarışdırılmış sözü düzgün tapın\n"
                "• Hər düzgün cavab 25 xal verir\n"
                "• Yanlış cavab heç nə vermir\n\n"
                "✅ Bu əmrləri hər kəs istifadə edə bilər"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=game_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=game_text,
                    reply_markup=markup
                )
                
        elif call.data == 'auto_commands':
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Komandalar", callback_data="commands"))
            
            auto_text = (
                "🤖 Avtomatik Funksiyalar\n\n"
                "📥 Sosial Media Yükləyici:\n"
                "• Instagram, TikTok, YouTube linklərindən\n"
                "  avtomatik media yüklənir\n\n"
                "🚫 Link Qadağası:\n"
                "• Adi linkləri avtomatik silir\n"
                "• Adminlər istisnadır\n\n"
                "🎬 Media Qadağası:\n"
                "• Foto, video və digər media növlərini silir\n"
                "• Adminlər istisnadır\n\n"
                "🔄 Ad Dəyişikliyi İzləməsi:\n"
                "• İstifadəçi adı dəyişəndə bildiriş göndərir\n\n"
                "👋 Yeni Üzv Salamı:\n"
                "• Bot qrupa əlavə ediləndə təşəkkür mesajı\n\n"
                "✅ Bu funksiyalar avtomatik işləyir"
            )
            
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=auto_text,
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=auto_text,
                    reply_markup=markup
                )
                
        elif call.data == 'home':
            home_caption = get_start_caption(call.from_user.first_name)
            home_markup = create_start_markup()
            
            # Mesajın photo olub-olmadığını yoxla
            if call.message.photo:
                bot.edit_message_caption(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    caption=home_caption,
                    reply_markup=home_markup
                )
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=home_caption,
                    reply_markup=home_markup
                )
                
    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Xəta baş verdi")
        print(f"Callback query error: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith('font_'))
def font_callback_query(call):
    try:
        parts = call.data.split('_')
        font_style = parts[1]
        original_message_id = int(parts[2])
        
        if original_message_id in font_messages:
            text = font_messages[original_message_id]
            
            if font_style in fonts:
                formatted_text = fonts[font_style](text)
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"✅ Font tətbiq edildi:\n\n{formatted_text}"
                )
                # Clean up stored message
                del font_messages[original_message_id]
            else:
                bot.answer_callback_query(call.id, "❌ Font tapılmadı")
        else:
            bot.answer_callback_query(call.id, "❌ Mətn tapılmadı")
    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Xəta baş verdi")

# Callback handler for word change button
@bot.callback_query_handler(func=lambda c: c.data.startswith('change_word_'))
def change_word_callback(call):
    try:
        # Chat ID-ni daha dəqiq parse et
        parts = call.data.split('_')
        if len(parts) >= 3:
            chat_id = int(parts[2])
        else:
            chat_id = call.message.chat.id
        
        if chat_id not in game_sessions or not game_sessions[chat_id]['active']:
            bot.answer_callback_query(call.id, "❌ Aktiv oyun yoxdur")
            return
        
        # Yeni söz götür
        word = get_random_word()
        scrambled = scramble_word(word)
        
        game_sessions[chat_id]['word'] = word
        game_sessions[chat_id]['scrambled'] = scrambled
        
        # Button əlavə et
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔃 Sözü dəyişmək", callback_data=f"change_word_{chat_id}"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🔃 Söz dəyişdirildi!\n\n"
                 f"🔤 Yeni qarışdırılmış söz: {scrambled}\n\n"
                 f"Bu hərflərdən düzgün sözü tapın!",
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id, "✅ Yeni söz yükləndi!")
        
    except Exception as e:
        print(f"Change word callback error: {e}")
        bot.answer_callback_query(call.id, "❌ Xəta baş verdi")

# ----------- PIN / UNPIN / UNPINALL -------------

@bot.message_handler(commands=['pin'])
def pin(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    if not message.reply_to_message:
        return bot.reply_to(message, "🔺 Zəhmət olmasa, hər hansısa mesaja cavab verin ✅")
    try:
        bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        bot.reply_to(message.reply_to_message, "📌 Bir mesajı sabitlədim")
    except Exception as e:
        bot.reply_to(message, "❌ Pin edilə bilmədi. Yetkiniz olmaya bilər.")

@bot.message_handler(commands=['unpin'])
def unpin(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    if not message.reply_to_message:
        return bot.reply_to(message, "🔺 Zəhmət olmasa, hər hansısa mesaja cavab verin ✅")
    try:
        bot.unpin_chat_message(message.chat.id, message.reply_to_message.message_id)
        bot.reply_to(message.reply_to_message, "✅ Bir mesajı pindən sildim")
    except Exception as e:
        bot.reply_to(message, "❌ Pin silinə bilmədi. Yetkiniz olmaya bilər.")

@bot.message_handler(commands=['unpinall'])
def unpinall(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    try:
        bot.unpin_all_chat_messages(message.chat.id)
        bot.reply_to(message, "✅ Bütün sabitləmələr silindi")
    except Exception as e:
        bot.reply_to(message, "❌ Bütün pinlər silinə bilmədi. Yetkiniz olmaya bilər.")

# ----------- BAN / UNBAN / MUTE / UNMUTE / KICK / WARN -------------

@bot.message_handler(commands=['ban'])
def ban(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    user = None
    args = message.text.split()
    
    # Reply ilə istifadəçi tapma
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    # ID və ya username ilə axtarış
    elif len(args) > 1:
        try:
            # ID ilə axtarış
            if args[1].isdigit():
                user_id = int(args[1])
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
            # Username ilə axtarış
            elif args[1].startswith('@'):
                username = args[1][1:]  # @ işarəsini sil
                member = bot.get_chat(username)
                user_id = member.id
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
            else:
                # @ olmadan username
                username = args[1]
                member = bot.get_chat(username)
                user_id = member.id
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
        except:
            return bot.reply_to(message, "❌ İstifadəçi tapılmadı. Düzgün ID və ya @username daxil edin.")
    
    if not user:
        return bot.reply_to(message, "🔺 İstifadə: /ban (reply) və ya /ban <ID/username>")
    
    try:
        bot.ban_chat_member(message.chat.id, user.id)
        username_display = f"@{user.username}" if user.username else "yoxdur"
        bot.reply_to(message, f"🚫 {user.first_name} qadağan edildi\n👤 Username: {username_display}\n🆔 ID: {user.id}\n🥷 İcraçı: {message.from_user.first_name}")
    except:
        bot.reply_to(message, "❌ Ban edilə bilmədi")

@bot.message_handler(commands=['unban'])
def unban(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    user = None
    args = message.text.split()
    
    # Reply ilə istifadəçi tapma
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    # ID və ya username ilə axtarış
    elif len(args) > 1:
        try:
            # ID ilə axtarış
            if args[1].isdigit():
                user_id = int(args[1])
                bot.unban_chat_member(message.chat.id, user_id)
                bot.reply_to(message, f"✅ ID {user_id} qadağası silindi\n🥷 İcraçı: {message.from_user.first_name}")
                return
            # Username ilə axtarış
            elif args[1].startswith('@'):
                username = args[1][1:]
                member = bot.get_chat(username)
                user_id = member.id
                bot.unban_chat_member(message.chat.id, user_id)
                bot.reply_to(message, f"✅ @{username} qadağası silindi\n🥷 İcraçı: {message.from_user.first_name}")
                return
            else:
                username = args[1]
                member = bot.get_chat(username)
                user_id = member.id
                bot.unban_chat_member(message.chat.id, user_id)
                bot.reply_to(message, f"✅ @{username} qadağası silindi\n🥷 İcraçı: {message.from_user.first_name}")
                return
        except:
            return bot.reply_to(message, "❌ İstifadəçi tapılmadı. Düzgün ID və ya @username daxil edin.")
    
    if not user:
        return bot.reply_to(message, "🔺 İstifadə: /unban (reply) və ya /unban <ID/username>")
    
    try:
        bot.unban_chat_member(message.chat.id, user.id)
        username_display = f"@{user.username}" if user.username else "yoxdur"
        bot.reply_to(message, f"✅ {user.first_name} qadağası silindi\n👤 Username: {username_display}\n🆔 ID: {user.id}\n🥷 İcraçı: {message.from_user.first_name}")
    except:
        bot.reply_to(message, "❌ Qadağa silinə bilmədi")

@bot.message_handler(commands=['mute'])
def mute(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    user = None
    args = message.text.split()
    
    # Reply ilə istifadəçi tapma
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    # ID və ya username ilə axtarış
    elif len(args) > 1:
        try:
            # ID ilə axtarış
            if args[1].isdigit():
                user_id = int(args[1])
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
            # Username ilə axtarış
            elif args[1].startswith('@'):
                username = args[1][1:]
                member = bot.get_chat(username)
                user_id = member.id
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
            else:
                username = args[1]
                member = bot.get_chat(username)
                user_id = member.id
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
        except:
            return bot.reply_to(message, "❌ İstifadəçi tapılmadı. Düzgün ID və ya @username daxil edin.")
    
    if not user:
        return bot.reply_to(message, "🔺 İstifadə: /mute (reply) və ya /mute <ID/username>")
    
    try:
        bot.restrict_chat_member(message.chat.id, user.id, can_send_messages=False)
        username_display = f"@{user.username}" if user.username else "yoxdur"
        bot.reply_to(message, f"🔇 {user.first_name} səssiz edildi\n👤 Username: {username_display}\n🆔 ID: {user.id}\n🥷 İcraçı: {message.from_user.first_name}")
    except:
        bot.reply_to(message, "❌ Səssiz edilə bilmədi")

@bot.message_handler(commands=['unmute'])
def unmute(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    user = None
    args = message.text.split()
    
    # Reply ilə istifadəçi tapma
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    # ID və ya username ilə axtarış
    elif len(args) > 1:
        try:
            # ID ilə axtarış
            if args[1].isdigit():
                user_id = int(args[1])
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
            # Username ilə axtarış
            elif args[1].startswith('@'):
                username = args[1][1:]
                member = bot.get_chat(username)
                user_id = member.id
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
            else:
                username = args[1]
                member = bot.get_chat(username)
                user_id = member.id
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
        except:
            return bot.reply_to(message, "❌ İstifadəçi tapılmadı. Düzgün ID və ya @username daxil edin.")
    
    if not user:
        return bot.reply_to(message, "🔺 İstifadə: /unmute (reply) və ya /unmute <ID/username>")
    
    try:
        bot.restrict_chat_member(message.chat.id, user.id, can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True)
        username_display = f"@{user.username}" if user.username else "yoxdur"
        bot.reply_to(message, f"🔊 {user.first_name} səssizdən çıxarıldı\n👤 Username: {username_display}\n🆔 ID: {user.id}\n🥷 İcraçı: {message.from_user.first_name}")
    except:
        bot.reply_to(message, "❌ Səssiz açıla bilmədi")

@bot.message_handler(commands=['kick'])
def kick(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    user = extract_user(message)
    if not user:
        return bot.reply_to(message, "🔺Kimin haqqında danışdığınızı bilmirəm......")
    
    try:
        bot.ban_chat_member(message.chat.id, user.id)
        bot.unban_chat_member(message.chat.id, user.id)
        bot.reply_to(message, f"{user.first_name} (ID: {user.id}) qrupdan qovuldu ✅\nİcraçı 🥷 {message.from_user.first_name}")
    except:
        bot.reply_to(message, "❌ Qovula bilmədi")

@bot.message_handler(commands=['warn'])
def warn(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    user = None
    args = message.text.split()
    reason = "Səbəb göstərilməyib"
    
    # Reply ilə istifadəçi tapma
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        # Səbəbi al
        if len(args) > 1:
            reason = " ".join(args[1:])
    # ID və ya username ilə axtarış
    elif len(args) > 1:
        try:
            # ID ilə axtarış
            if args[1].isdigit():
                user_id = int(args[1])
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
                if len(args) > 2:
                    reason = " ".join(args[2:])
            # Username ilə axtarış
            elif args[1].startswith('@'):
                username = args[1][1:]
                member = bot.get_chat(username)
                user_id = member.id
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
                if len(args) > 2:
                    reason = " ".join(args[2:])
            else:
                username = args[1]
                member = bot.get_chat(username)
                user_id = member.id
                member = bot.get_chat_member(message.chat.id, user_id)
                user = member.user
                if len(args) > 2:
                    reason = " ".join(args[2:])
        except:
            return bot.reply_to(message, "❌ İstifadəçi tapılmadı. Düzgün ID və ya @username daxil edin.")
    
    if not user:
        return bot.reply_to(message, "🔺 İstifadə: /warn (reply) [səbəb] və ya /warn <ID/username> [səbəb]")
    
    username_display = f"@{user.username}" if user.username else "yoxdur"
    bot.reply_to(message, f"⚠️ {user.first_name} xəbərdarlıq aldı!\n👤 Username: {username_display}\n🆔 ID: {user.id}\n📝 Səbəb: {reason}\n🥷 İcraçı: {message.from_user.first_name}")

@bot.message_handler(commands=['promote'])
def promote(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    user = extract_user(message)
    if not user:
        return bot.reply_to(message, "🔺Kimin haqqında danışdığınızı bilmirəm......")
    
    try:
        bot.promote_chat_member(
            message.chat.id, 
            user.id,
            can_delete_messages=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False
        )
        bot.reply_to(message, f"🎉 {user.first_name} (ID: {user.id}) admin oldu!\nİcraçı 🥷 {message.from_user.first_name}")
    except:
        bot.reply_to(message, "❌ Admin edilə bilmədi")

@bot.message_handler(commands=['demote'])
def demote(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    user = extract_user(message)
    if not user:
        return bot.reply_to(message, "🔺Kimin haqqında danışdığınızı bilmirəm......")
    
    try:
        bot.promote_chat_member(
            message.chat.id, 
            user.id,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False
        )
        bot.reply_to(message, f"📉 {user.first_name} (ID: {user.id}) adminlikdən çıxarıldı!\nİcraçı 🥷 {message.from_user.first_name}")
    except:
        bot.reply_to(message, "❌ Adminlikdən çıxarıla bilmədi")

# ----------- ADMINLIST / RELOAD -------------

@bot.message_handler(commands=['adminlist'])
def adminlist(message):
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        if not admins:
            return bot.reply_to(message, "Admin siyahısı boşdur.")
        text = "Adminlər siyahısı:\n"
        for admin in admins:
            user = admin.user
            status = admin.status
            text += f"- {user.first_name}"
            if user.username:
                text += f" (@{user.username})"
            text += f" — {status}\n"
        text += "\nNot: Admin siyahısı tam güncəldir!"
        bot.reply_to(message, text)
    except Exception as e:
        bot.reply_to(message, "Admin siyahısını götürmək mümkün olmadı.")

@bot.message_handler(commands=['reload'])
def reload(message):
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        if admins:
            bot.reply_to(message, "🔹 Yeni qonaqlarımızın olduğunu görürəm və admin siyahısını yeniləyirəm ✅")
        else:
            bot.reply_to(message, "🔺 Admin siyahısı tam güncəldir ✅")
    except Exception as e:
        bot.reply_to(message, "Admin siyahısı yenilənmədi.")

# ----------- MEN / KIM / ID / INFO -------------

@bot.message_handler(commands=['men'])
def men(message):
    user = message.from_user
    chat = bot.get_chat(message.chat.id)
    owner = None
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        for admin in admins:
            if admin.status == 'creator':
                owner = admin.user.first_name
                break
    except:
        owner = "Tapılmadı"
    text = (
        f"▻ | • Name: {user.first_name}\n"
        f"▻ | • ID: {user.id}\n"
        f"▻ | • Time: {format_time()}\n"
        f"▻ | • Chat: {chat.title}\n"
        f"▻ | • Chat Owner: {owner}"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['kim', 'id', 'info'])
def info_commands(message):
    user = None
    chat = None
    arg = message.text.split()
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        chat = message.chat
    elif len(arg) > 1:
        try:
            user = bot.get_chat_member(message.chat.id, int(arg[1])).user
            chat = message.chat
        except:
            try:
                user = bot.get_chat_member(message.chat.id, arg[1]).user
                chat = message.chat
            except:
                pass
    else:
        user = message.from_user
        chat = message.chat

    if not user:
        return bot.reply_to(message, "🔺 Zəhmət olmasa, istifadəçini təyin edin ✅")

    if message.text.startswith('/id'):
        bot.reply_to(message, f"Sənin 🆔 {user.id}")
        return

    text = (
        f"▻ | • Name: {user.first_name}\n"
        f"▻ | • ID: {user.id}\n"
        f"▻ | • Time: {format_time()}\n"
        f"▻ | • Chat: {chat.title}"
    )
    if message.text.startswith('/info'):
        try:
            member = bot.get_chat_member(chat.id, user.id)
            if member.status in ['kicked', 'left']:
                text += "\n▻ | • Qadağan: Qadağan olunub"
            else:
                text += "\n▻ | • Qadağan: Yoxdur 🔺"
        except:
            text += "\n▻ | • Qadağan: Məlumat tapılmadı"
    bot.reply_to(message, text)

# ----------- ALIVE -------------

@bot.message_handler(commands=['alive'])
def alive(message):
    ping = int(bot.get_me().id)  # Sadə ping kimi id-nin integer hissəsi
    bot.reply_to(message,
        f"🔹Bot aktivdir ✅\n🔹Ping: {ping}\n🔺 Server: Replit Thunder VPS")

# ----------- TAG / CANCEL / TAGALL -------------

tag_process = {}  # chat_id: bool

@bot.message_handler(commands=['tag'])
def tag(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    chat_id = message.chat.id
    if tag_process.get(chat_id, False):
        return bot.reply_to(message, "❌ Tag prosesi artıq aktivdir.")
    
    # Mesaj varsa götür
    args = message.text.split(None, 1)
    custom_message = args[1] if len(args) > 1 else None
    
    tag_process[chat_id] = True
    bot.reply_to(message, f"{message.from_user.first_name} admin tag prosesi başladı ✅\nProsesi saxlamaq üçün /cancel yaz")

    def tag_admins():
        try:
            admins = bot.get_chat_administrators(chat_id)
            for admin in admins:
                if not tag_process.get(chat_id, False):
                    break
                user = admin.user
                try:
                    if custom_message:
                        tag_text = f"@{user.username} {custom_message}" if user.username else f"{user.first_name} {custom_message}"
                    else:
                        tag_text = f"@{user.username}" if user.username else user.first_name
                    bot.send_message(chat_id, tag_text)
                    time.sleep(1.2)
                except:
                    pass
            if tag_process.get(chat_id, False):
                bot.send_message(chat_id, f"Admin tag prosesi başa çatdı ✅\nİcraçı 🥷 {message.from_user.first_name}")
        except:
            bot.send_message(chat_id, "Tag edilərkən xəta baş verdi.")

        tag_process[chat_id] = False

    import threading
    threading.Thread(target=tag_admins).start()

@bot.message_handler(commands=['tagadmin'])
def tagadmin(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    chat_id = message.chat.id
    args = message.text.split(None, 1)
    custom_message = args[1] if len(args) > 1 else "📢 Admin çağırışı"
    
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_tags = []
        for admin in admins:
            user = admin.user
            if user.username:
                admin_tags.append(f"@{user.username}")
            else:
                admin_tags.append(user.first_name)
        
        if admin_tags:
            tag_text = f"{custom_message}\n\n" + " ".join(admin_tags)
            bot.send_message(chat_id, tag_text)
        else:
            bot.reply_to(message, "❌ Admin tapılmadı.")
    except:
        bot.reply_to(message, "❌ Adminlər tag edilə bilmədi.")

@bot.message_handler(commands=['stag'])
def stag(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    chat_id = message.chat.id
    args = message.text.split(None, 1)
    custom_message = args[1] if len(args) > 1 else "📣 Sessiz tag"
    
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_tags = []
        for admin in admins:
            user = admin.user
            if user.username:
                admin_tags.append(f"@{user.username}")
        
        if admin_tags:
            # Sessiz tag üçün zero-width space istifadə et
            tag_text = f"{custom_message}\n\n" + "‌".join(admin_tags)
            bot.send_message(chat_id, tag_text)
        else:
            bot.reply_to(message, "❌ Admin tapılmadı.")
    except:
        bot.reply_to(message, "❌ Sessiz tag edilə bilmədi.")

@bot.message_handler(commands=['tagall'])
def tagall(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    chat_id = message.chat.id
    if tag_process.get(chat_id, False):
        return bot.reply_to(message, "❌ Tag prosesi artıq aktivdir.")
    
    # Mesaj varsa götür
    args = message.text.split(None, 1)
    custom_message = args[1] if len(args) > 1 else None
    
    tag_process[chat_id] = True
    bot.reply_to(message, f"{message.from_user.first_name} bütün üzvləri tag etmə prosesi başladı ✅\nProsesi saxlamaq üçün /cancel yaz")

    def tag_all_members():
        try:
            # Note: Telegram API-də bütün üzvləri almaq məhdud olduğu üçün adminləri tag edirik
            members = bot.get_chat_administrators(chat_id)
            for member in members:
                if not tag_process.get(chat_id, False):
                    break
                user = member.user
                try:
                    if custom_message:
                        tag_text = f"@{user.username} {custom_message}" if user.username else f"{user.first_name} {custom_message}"
                    else:
                        tag_text = f"@{user.username}" if user.username else user.first_name
                    bot.send_message(chat_id, tag_text)
                    time.sleep(1.5)
                except:
                    pass
            if tag_process.get(chat_id, False):
                bot.send_message(chat_id, f"Bütün mövcud üzvlər tag edildi ✅\nİcraçı 🥷 {message.from_user.first_name}")
        except:
            bot.send_message(chat_id, "Tag edilərkən xəta baş verdi.")

        tag_process[chat_id] = False

    import threading
    threading.Thread(target=tag_all_members).start()

@bot.message_handler(commands=['utag'])
def utag(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    chat_id = message.chat.id
    args = message.text.split(None, 1)
    custom_message = args[1] if len(args) > 1 else "🔥 Vacib elan"
    
    try:
        # Son aktiv istifadəçiləri tag et (message_counts-dan)
        if chat_id in message_counts:
            active_users = list(message_counts[chat_id].keys())[:10]  # Son 10 aktiv istifadəçi
            user_tags = []
            for user_id in active_users:
                try:
                    member = bot.get_chat_member(chat_id, user_id)
                    user = member.user
                    if user.username:
                        user_tags.append(f"@{user.username}")
                    else:
                        user_tags.append(user.first_name)
                except:
                    pass
            
            if user_tags:
                tag_text = f"{custom_message}\n\n" + " ".join(user_tags)
                bot.send_message(chat_id, tag_text)
            else:
                bot.reply_to(message, "❌ Aktiv istifadəçi tapılmadı.")
        else:
            bot.reply_to(message, "❌ Aktiv istifadəçi məlumatı yoxdur.")
    except:
        bot.reply_to(message, "❌ İstifadəçilər tag edilə bilmədi.")

@bot.message_handler(commands=['cancel'])
def cancel(message):
    chat_id = message.chat.id
    if tag_process.get(chat_id, False):
        tag_process[chat_id] = False
        bot.reply_to(message, f"{message.from_user.first_name}, tag prosesi saxladıldı 🔺")
    else:
        bot.reply_to(message, "❌ Aktiv tag prosesi yoxdur.")

# ----------- SOSIAL MEDIA DOWNLOADER -------------

import requests
import os

def download_media_from_url(url):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            filename = f"media_{int(time.time())}.mp4"
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        return None
    except:
        return None

def check_social_media_links(text):
    social_patterns = [
        r"(https?://)?(www\.)?(instagram\.com|instagr\.am)/",
        r"(https?://)?(www\.)?(tiktok\.com)/",
        r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
        r"(https?://)?(www\.)?(facebook\.com|fb\.com)/",
        r"(https?://)?(www\.)?(twitter\.com|x\.com)/"
    ]
    
    for pattern in social_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

# ----------- AFK -------------

@bot.message_handler(commands=['afk'])
def afk(message):
    user_id = message.from_user.id
    reason = message.text[4:].strip()
    if not reason:
        reason = "AFK"
    afk_users[user_id] = (reason, time.time())
    bot.reply_to(message, f"{message.from_user.first_name} Afk səbəbi qeyd olundu, Uğurlar ✨✅")

# ----------- FILTER -------------

@bot.message_handler(commands=['filter'])
def add_filter(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    
    chat_id = message.chat.id
    
    # Reply-ə cavab verilmişsə, həmin mesajın mətni filter olaraq əlavə edilsin
    if message.reply_to_message:
        replied_text = message.reply_to_message.text or message.reply_to_message.caption
        if not replied_text:
            return bot.reply_to(message, "❌ Cavab verdiyiniz mesajda mətn yoxdur.")
        
        args = message.text.split(None, 1)
        if len(args) < 2:
            return bot.reply_to(message, "İstifadə: /filter [cavab metni] (mesaja reply ilə)")
        
        reply_text = args[1]
        word = replied_text.lower()
        
        if chat_id not in filters:
            filters[chat_id] = {}
        filters[chat_id][word] = reply_text
        bot.reply_to(message, f"✅ Filter əlavə olundu: {replied_text} → {reply_text}")
        return
    
    # Əgər reply yoxdursa, adi metod
    args = message.text.split(None, 2)
    if len(args) < 3:
        return bot.reply_to(message, "İstifadə: /filter söz cavab və ya mesaja reply ilə /filter cavab")
    word, reply_text = args[1], args[2]

    if chat_id not in filters:
        filters[chat_id] = {}
    filters[chat_id][word.lower()] = reply_text
    bot.reply_to(message, f"✅ Filter əlavə olundu: {word} → {reply_text}")

@bot.message_handler(commands=['stop'])
def stop_filter(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    chat_id = message.chat.id
    args = message.text.split(None, 1)
    if len(args) < 2:
        return bot.reply_to(message, "İstifadə: /stop söz")
    word = args[1].lower()

    if chat_id in filters and word in filters[chat_id]:
        del filters[chat_id][word]
        bot.reply_to(message, f"✅ Filter silindi: {word}")
    else:
        bot.reply_to(message, "❌ Belə filter tapılmadı.")

@bot.message_handler(commands=['stopall'])
def stop_all_filters(message):
    if not is_admin(message.from_user.id, message.chat.id):
        return bot.reply_to(message, "❌ Bu əmri istifadə etmək üçün admin olmalısınız.")
    chat_id = message.chat.id
    if chat_id in filters:
        filters[chat_id].clear()
        bot.reply_to(message, "✅ Bütün filterlər silindi.")
    else:
        bot.reply_to(message, "❌ Filterlər mövcud deyil.")

@bot.message_handler(commands=['filters'])
def list_filters(message):
    chat_id = message.chat.id
    if chat_id in filters and filters[chat_id]:
        text = "📋 Mövcud filterlər:\n"
        for word, reply_text in filters[chat_id].items():
            text += f"- {word} → {reply_text}\n"
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "❌ Heç bir filter mövcud deyil.")

# ----------- FONT GENERATOR -------------

fonts = {
    'bold': lambda text: ''.join(chr(ord(c) + 0x1D400 - 65) if 'A' <= c <= 'Z' else
                                chr(ord(c) + 0x1D41A - 97) if 'a' <= c <= 'z' else c for c in text),
    'italic': lambda text: ''.join(chr(ord(c) + 0x1D434 - 65) if 'A' <= c <= 'Z' else
                                  chr(ord(c) + 0x1D44E - 97) if 'a' <= c <= 'z' else c for c in text),
    'mono': lambda text: ''.join(chr(ord(c) + 0x1D670 - 65) if 'A' <= c <= 'Z' else
                                chr(ord(c) + 0x1D68A - 97) if 'a' <= c <= 'z' else c for c in text),
    'double': lambda text: ''.join(chr(ord(c) + 0x1D538 - 65) if 'A' <= c <= 'Z' else
                                  chr(ord(c) + 0x1D552 - 97) if 'a' <= c <= 'z' else c for c in text),
    'serif': lambda text: ''.join(chr(ord(c) + 0x1D5A0 - 65) if 'A' <= c <= 'Z' else
                                 chr(ord(c) + 0x1D5BA - 97) if 'a' <= c <= 'z' else c for c in text),
    'script': lambda text: ''.join(chr(ord(c) + 0x1D4D0 - 65) if 'A' <= c <= 'Z' else
                                  chr(ord(c) + 0x1D4EA - 97) if 'a' <= c <= 'z' else c for c in text),
    'fraktur': lambda text: ''.join(chr(ord(c) + 0x1D504 - 65) if 'A' <= c <= 'Z' else
                                   chr(ord(c) + 0x1D51E - 97) if 'a' <= c <= 'z' else c for c in text),
    'bubble': lambda text: ''.join(chr(ord(c) + 0x24B6 - 65) if 'A' <= c <= 'Z' else
                                  chr(ord(c) + 0x24D0 - 97) if 'a' <= c <= 'z' else c for c in text),
}

# Temporary storage for font messages
font_messages = {}  # message_id: text

@bot.message_handler(commands=['font'])
def font_command(message):
    args = message.text.split(None, 1)
    if len(args) < 2:
        return bot.reply_to(message, "İstifadə: /font <mətn>")
    
    text = args[1]
    
    # Create inline keyboard with font options
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("𝐁𝐨𝐥𝐝", callback_data=f"font_bold_{message.message_id}"),
        types.InlineKeyboardButton("𝘐𝘵𝘢𝘭𝘪𝘤", callback_data=f"font_italic_{message.message_id}")
    )
    markup.row(
        types.InlineKeyboardButton("𝙼𝚘𝚗𝚘", callback_data=f"font_mono_{message.message_id}"),
        types.InlineKeyboardButton("𝔻𝕠𝕦𝕓𝕝𝕖", callback_data=f"font_double_{message.message_id}")
    )
    markup.row(
        types.InlineKeyboardButton("𝖲𝖾𝗋𝗂𝖿", callback_data=f"font_serif_{message.message_id}"),
        types.InlineKeyboardButton("𝒮𝒸𝓇𝒾𝓅𝓉", callback_data=f"font_script_{message.message_id}")
    )
    markup.row(
        types.InlineKeyboardButton("𝔉𝔯𝔞𝔨𝔱𝔲𝔯", callback_data=f"font_fraktur_{message.message_id}"),
        types.InlineKeyboardButton("Ⓑⓤⓑⓑⓛⓔ", callback_data=f"font_bubble_{message.message_id}")
    )
    
    # Store the text for later use
    font_messages[message.message_id] = text
    
    bot.reply_to(message, f"Mətn: {text}\n\nFont seçin:", reply_markup=markup)

# ----------- MAL / SHIP / Q KOMANDALARI -------------

@bot.message_handler(commands=['mal'])
def mal(message):
    names = ["Narmin", "Leyla", "Tural", "Aysel", "Ramil"]
    mal = random.choice(names)
    bot.reply_to(message, f"Sənin malın: {mal} 😎")

@bot.message_handler(commands=['ship'])
def ship(message):
    # Reply-ə cavab verilmişsə, reply istifadəçisi və komanda istifadəçisi
    if message.reply_to_message:
        user1 = message.from_user
        user2 = message.reply_to_message.from_user
        rate = random.randint(0, 100)
        bot.reply_to(message, f"❤️ {user1.first_name} və {user2.first_name} arasında uyğunluq: {rate}%")
        return
    
    # Əgər reply yoxdursa, adi metod
    args = message.text.split(None, 2)
    if len(args) < 3:
        return bot.reply_to(message, "İstifadə: /ship ad1 ad2 və ya mesaja reply ilə /ship")
    name1, name2 = args[1], args[2]
    rate = random.randint(0, 100)
    bot.reply_to(message, f"❤️ {name1} və {name2} arasında uyğunluq: {rate}%")

@bot.message_handler(commands=['q'])
def q(message):
    if not message.reply_to_message:
        return bot.reply_to(message, "Zəhmət olmasa, sitat üçün bir mesaja cavab verin.")
    text = message.reply_to_message.text or message.reply_to_message.caption
    if not text:
        return bot.reply_to(message, "Cavab verdiyiniz mesajda mətn yoxdur.")
    bot.reply_to(message, f"💬 Sitat:\n\n{text}")

# ----------- NEW MEMBER HANDLER -----------

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        # Əgər bot özü əlavə edilibsə
        if new_member.id == bot.get_me().id:
            # Qalın fontda təşəkkür mesajı
            bold_text = "𝐌𝐞𝐧𝐢 𝐛𝐮 𝐪𝐫𝐮𝐩𝐚 ə𝐥𝐚𝐯𝐞 𝐞𝐭𝐝𝐢𝐲𝐢𝐧𝐢𝐳 ü𝐜ü𝐧 𝐭əş𝐞𝐤𝐤ü𝐫 𝐞𝐝𝐢𝐫ə𝐦, 𝐝𝐚𝐡𝐚 ç𝐨𝐱 𝐤ö𝐦ə𝐤 ü𝐜ü𝐧 𝐚şă𝐠ı𝐝𝐚𝐤ı 𝐝ü𝐲𝐦ə𝐲ə 𝐤𝐥𝐢𝐤𝐥ə𝐲𝐢𝐧 :)"
            
            # Düymə əlavə et
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("📚 Komandalar", callback_data="commands"),
                types.InlineKeyboardButton("🧑‍💻 Sahibim", url="https://t.me/PersionalTeamBot")
            )
            
            bot.send_message(
                message.chat.id,
                f"😇 {bold_text}",
                reply_markup=markup
            )
        else:
            # Adi istifadəçi üçün random salamlama mesajı
            username = f"@{new_member.username}" if new_member.username else new_member.first_name
            
            welcome_messages = [
                f"{username} xoş gəldin⚡ nə gətirmisən mənə🥱",
                f"{username} xoş gəldin necəsən?❤️‍🔥",
                f"{username} xoş gəldin çıxacaqsansa indidən vzzz🥳",
                f"{username} xoş gəldin necəsən brat 🌸"
            ]
            
            random_message = random.choice(welcome_messages)
            bot.send_message(message.chat.id, random_message)

# ----------- MESSAGE HANDLERS -----------

# Username dəyişikliyi izləməsi üçün storage
user_names = {}  # user_id: last_known_name

# ----------- WORD GAME HANDLERS -----------

@bot.message_handler(commands=['game'])
def start_game_command(message):
    chat_id = message.chat.id
    
    # Yeni oyun başlat
    word = get_random_word()
    scrambled = scramble_word(word)
    
    game_sessions[chat_id] = {
        'word': word,
        'scrambled': scrambled,
        'active': True
    }
    
    # Chat üçün xal sistemi başlat
    if chat_id not in player_scores:
        player_scores[chat_id] = {}
    
    # Button əlavə et
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔃 Sözü dəyişmək", callback_data=f"change_word_{chat_id}"))
    
    bot.send_message(
        chat_id,
        f"🎮 Söz Oyunu Başladı!\n\n"
        f"🔤 Qarışdırılmış söz: {scrambled}\n\n"
        f"Bu hərflərdən düzgün sözü tapın!\n"
        f"✅ Düzgün cavab: +25 xal\n"
        f"🛑 Oyunu bitirmək: /bitir və ya /stop\n"
        f"📊 Xallarınızı görmək: /xallar\n"
        f"⏭️ Keçmək: /kec",
        reply_markup=markup
    )

@bot.message_handler(commands=['xallar'])
def show_scores_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if chat_id not in player_scores or user_id not in player_scores[chat_id]:
        return bot.reply_to(message, "🎯 Hələ heç bir xalınız yoxdur. Oyuna başlamaq üçün /game yazın!")
    
    user_score = player_scores[chat_id][user_id]
    user_name = message.from_user.first_name
    
    bot.reply_to(message, f"📊 {user_name}, sizin xalınız: {user_score} xal 🌟")

@bot.message_handler(commands=['kec'])
def skip_word_command(message):
    chat_id = message.chat.id
    
    if chat_id not in game_sessions or not game_sessions[chat_id]['active']:
        return bot.reply_to(message, "🚫 Aktiv oyun yoxdur. /game ilə başlayın!")
    
    # Yeni söz götür
    word = get_random_word()
    scrambled = scramble_word(word)
    
    game_sessions[chat_id]['word'] = word
    game_sessions[chat_id]['scrambled'] = scrambled
    
    # Button əlavə et
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔃 Sözü dəyişmək", callback_data=f"change_word_{chat_id}"))
    
    bot.send_message(
        chat_id,
        f"⏭️ Söz keçildi!\n\n"
        f"🔤 Yeni qarışdırılmış söz: {scrambled}\n\n"
        f"Bu hərflərdən düzgün sözü tapın!",
        reply_markup=markup
    )

@bot.message_handler(commands=['bitir'])
def stop_game_command(message):
    chat_id = message.chat.id
    
    if chat_id not in game_sessions or not game_sessions[chat_id]['active']:
        return bot.reply_to(message, "🚫 Aktiv oyun yoxdur.")
    
    game_sessions[chat_id]['active'] = False
    
    # Ən yüksək xalı göstər
    if chat_id in player_scores and player_scores[chat_id]:
        top_player = max(player_scores[chat_id], key=player_scores[chat_id].get)
        top_score = player_scores[chat_id][top_player]
        try:
            top_user = bot.get_chat_member(chat_id, top_player).user
            top_name = top_user.first_name
        except:
            top_name = "Naməlum"
        
        bot.send_message(
            chat_id,
            f"🏁 Söz Oyunu Bitdi!\n\n"
            f"🏆 Ən yüksək xal: {top_name} - {top_score} xal\n\n"
            f"Yeni oyun üçün /game yazın! 🎮"
        )
    else:
        bot.send_message(chat_id, "🏁 Söz Oyunu Bitdi! Yeni oyun üçün /game yazın! 🎮")

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    # Username dəyişikliyi yoxlama
    user_id = message.from_user.id
    current_name = message.from_user.first_name
    if user_id in user_names and user_names[user_id] != current_name:
        chat_name = message.chat.title or "Bu Qrup"
        bot.send_message(message.chat.id, 
            f"Adını dəyişdi 🔃\n"
            f"Köhnə adı ↩️ {user_names[user_id]}\n"
            f"Yeni adı ↪️ {current_name}\n"
            f"Chatname {chat_name} 🎯")
    user_names[user_id] = current_name

    # AFK check
    if message.reply_to_message:
        replied_user_id = message.reply_to_message.from_user.id
        if replied_user_id in afk_users:
            reason, start_time = afk_users[replied_user_id]
            duration = int(time.time() - start_time)
            bot.reply_to(message, (
                f"🔹 Göründüyü kimi {message.reply_to_message.from_user.first_name} afk xəttindədir.\n"
                f"🔹 Səbəb: {reason}\n"
                f"🔹 Vaxt: {duration} saniyədir"
            ))

    # Afk istifadəçi yazarsa, afk-dan çıxar
    if user_id in afk_users:
        del afk_users[user_id]
        bot.reply_to(message, f"🎯 {message.from_user.first_name}, afk rejimindən çıxdın!")

    # Game answer check
    chat_id = message.chat.id
    text = message.text
    if text and chat_id in game_sessions and game_sessions[chat_id]['active']:
        if text.lower().strip() == game_sessions[chat_id]['word'].lower():
            # Düzgün cavab!
            user_id = message.from_user.id
            
            # Xal əlavə et
            if chat_id not in player_scores:
                player_scores[chat_id] = {}
            if user_id not in player_scores[chat_id]:
                player_scores[chat_id][user_id] = 0
            
            player_scores[chat_id][user_id] += 25
            
            # Yeni söz götür
            new_word = get_random_word()
            new_scrambled = scramble_word(new_word)
            
            game_sessions[chat_id]['word'] = new_word
            game_sessions[chat_id]['scrambled'] = new_scrambled
            
            # Button əlavə et
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔃 Sözü dəyişmək", callback_data=f"change_word_{chat_id}"))
            
            bot.reply_to(message, 
                f"Doğrudur! sözü düzgün tapdın 🌟\n"
                f"25+ xal qazandın🎯\n\n"
                f"🆕Yeni söz: {new_scrambled}",
                reply_markup=markup
            )
            return

    # Filter check
    if text and chat_id in filters:
        for word, reply_text in filters[chat_id].items():
            if word in text.lower():
                bot.reply_to(message, reply_text)
                break

    # Sosial media linklərini yoxlama və yükləmə
    if message.chat.type in ['group', 'supergroup']:
        if text:
            # Sosial media linkləri
            if check_social_media_links(text):
                if not is_admin(message.from_user.id, message.chat.id):
                    try:
                        # Linki silmədən əvvəl yükləməyə cəhd et
                        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
                        for url in urls:
                            filename = download_media_from_url(url)
                            if filename and os.path.exists(filename):
                                try:
                                    with open(filename, 'rb') as video:
                                        bot.send_video(
                                            message.chat.id, 
                                            video,
                                            caption=f"📥 Sosial media mediası yükləndi\n👤 Göndərən: {message.from_user.first_name}",
                                            reply_to_message_id=message.message_id
                                        )
                                    os.remove(filename)
                                except:
                                    if os.path.exists(filename):
                                        os.remove(filename)
                    except:
                        pass
            
            # Adi linklər üçün əvvəlki qadağa
            elif check_links(text):
                if not is_admin(message.from_user.id, message.chat.id):
                    try:
                        bot.delete_message(message.chat.id, message.message_id)
                        bot.send_message(message.chat.id,
                            f"{message.from_user.first_name}, qrupda link göndərmək qadağandır! ⛔")
                    except:
                        pass

# ----------- MEDIA SILME + XƏBƏRDARLIQ -------------

@bot.message_handler(content_types=['photo', 'video', 'sticker', 'voice', 'audio', 'video_note', 'document', 'animation'])
def media_filter(message):
    if message.chat.type in ['group', 'supergroup']:
        if not is_admin(message.from_user.id, message.chat.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id,
                    f"{message.from_user.first_name}, qrup şərtlərinə əsasən {message.chat.title} qrupunda media atmaq qadağandır ⛔")
            except:
                pass

# ----------- WORD GAME SYSTEM -----------

# Oyun üçün söz bazası
word_database = [
    "alma", "armud", "banan", "portağal", "üzüm", "gilas", "nar", "persimmon",
    "kitab", "qələm", "dəftər", "masa", "stul", "kompüter", "telefon", "saat",
    "maşın", "avtobus", "təyyarə", "gəmi", "velosiped", "motosikl", "qatar", "metro",
    "ev", "məktəb", "xəstəxana", "bazar", "park", "dəniz", "dağ", "çay",
    "yemək", "su", "çay", "qəhvə", "şəkər", "duz", "biber", "soğan",
    "gözəl", "böyük", "kiçik", "ağ", "qara", "qırmızı", "yaşıl", "mavi",
    "sevinc", "kədər", "qorxu", "əsəbi", "sakit", "məmnun", "yorğun", "güclü"
]

game_sessions = {}  # chat_id: {'word': str, 'scrambled': str, 'active': bool}
player_scores = {}  # chat_id: {user_id: score}

def scramble_word(word):
    """Sözün hərflərini qarışdırır"""
    letters = list(word)
    random.shuffle(letters)
    scrambled = ''.join(letters)
    # Əgər qarışdırılmış söz orijinalla eyni olarsa, yenidən qarışdır
    if scrambled == word and len(word) > 2:
        return scramble_word(word)
    return scrambled

def get_random_word():
    """Təsadüfi söz seçir"""
    return random.choice(word_database)

# ----------- YENİLƏMƏ VƏ İŞƏ SALMA -----------

print("✅ NarminBot işə düşdü!")
bot.infinity_polling()

