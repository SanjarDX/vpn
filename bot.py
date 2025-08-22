import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, BOT_DESCRIPTION
from vpn_service import VPNService

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Initialize VPN service
vpn_service = VPNService()

# Store user VPN keys (user_id -> list of VPN subscription objects)
user_vpn_keys = {}

# Store referral relationships (referrer_id -> list of referred_user_ids)
referral_relationships = {}

# Store referral rewards (referrer_id -> list of reward objects)
referral_rewards = {}

# Counter for generating subscription numbers
subscription_counter = 1

# Bot ID constant
BOT_ID = "8202650359"

# Support contact
SUPPORT_USERNAME = "@DavirovDS"

# Download links
DOWNLOAD_LINKS = {
    "android": "https://play.google.com/store/apps/details?id=com.v2raytun.android",
    "windows": "https://storage.v2raytun.com/v2RayTun_Setup.exe",
    "iphone": "https://apps.apple.com/ru/app/v2raytun/id6476628951?platform=iphone",
    "mac": "https://apps.apple.com/en/app/v2raytun/id6476628951",
    "streisand": "https://apps.apple.com/app/id6450534064"
}

# Welcome message text
WELCOME_MESSAGE = f"""<b>{BOT_DESCRIPTION}</b>

Мы обеспечиваем защиту ваших данных, предоставляя надёжный и эффективный сервис VPN для безопасного и анонимного пользования интернетом. Ваши данные под защитой, а вы — в безопасности."""

# Tariff data structure
TARIFFS = {
    "multi": {
        "name": "Мульти",
        "icon": "🌐",
        "price": 449,
        "description": "Мульти — 449 Р/мес"
    },
    "russia": {
        "name": "Россия",
        "icon": "🇷🇺",
        "price": 75,
        "description": "Россия [YT, INST, DS] — 75 Р/мес",
        "services": "[YT, INST, DS]"
    },
    "netherlands": {
        "name": "Нидерланды",
        "icon": "🇳🇱",
        "price": 149,
        "description": "Нидерланды — 149 Р/мес"
    },
    "germany": {
        "name": "Германия",
        "icon": "🇩🇪",
        "price": 224,
        "description": "Германия — 224 Р/мес"
    },
    "france": {
        "name": "Франция",
        "icon": "🇫🇷",
        "price": 299,
        "description": "Франция — 299 Р/мес"
    },
    "usa": {
        "name": "США",
        "icon": "🇺🇸",
        "price": 329,
        "description": "США — 329 Р/мес"
    }
}

def get_main_menu() -> InlineKeyboardMarkup:
    """Create the main menu with all buttons except 'Создать бот'"""
    
    # First row - single button
    tariffs_button = InlineKeyboardButton(
        text="💎 Тарифы", 
        callback_data="tariffs"
    )
    
    # Second row - two buttons
    my_keys_button = InlineKeyboardButton(
        text="🔑 Мои ключи", 
        callback_data="my_keys"
    )
    my_account_button = InlineKeyboardButton(
        text="⚙️ Мой аккаунт", 
        callback_data="my_account"
    )
    
    # Third row - two buttons
    instructions_button = InlineKeyboardButton(
        text="📚 Инструкция", 
        callback_data="instructions"
    )
    help_button = InlineKeyboardButton(
        text="🆘 Помощь", 
        callback_data="help"
    )
    
    # Fourth row - two buttons (excluding 'Создать бот')
    partners_button = InlineKeyboardButton(
        text="🤝 Партнерам", 
        callback_data="partners"
    )
    
    # Create keyboard layout
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [tariffs_button],
        [my_keys_button, my_account_button],
        [instructions_button, help_button],
        [partners_button]
    ])
    
    return keyboard

def get_tariffs_menu() -> InlineKeyboardMarkup:
    """Create the tariffs selection menu"""
    
    buttons = []
    
    # Add all tariff options
    for tariff_id, tariff_data in TARIFFS.items():
        button = InlineKeyboardButton(
            text=f"{tariff_data['icon']} {tariff_data['description']}", 
            callback_data=f"tariff_{tariff_id}"
        )
        buttons.append([button])
    
    # Add back button only
    back_button = InlineKeyboardButton(
        text="Вернуться", 
        callback_data="back_to_main"
    )
    
    buttons.append([back_button])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_time_periods_menu(country_id: str) -> InlineKeyboardMarkup:
    """Create the time period selection menu for a specific country"""
    
    tariff_data = TARIFFS[country_id]
    base_price = tariff_data['price']
    
    # Calculate prices for different periods
    month_1 = base_price
    month_3 = base_price * 3
    month_6_original = base_price * 6
    month_6_discounted = int(month_6_original * 0.9)  # 10% discount
    month_12_original = base_price * 12
    month_12_discounted = int(month_12_original * 0.8)  # 20% discount
    
    # Create strikethrough text using Unicode combining character
    def add_strikethrough(text):
        return ''.join(c + '\u0336' for c in str(text))
    
    buttons = [
        [InlineKeyboardButton(
            text=f"1 месяц — {month_1} ₽", 
            callback_data=f"period_{country_id}_1_{month_1}"
        )],
        [InlineKeyboardButton(
            text=f"3 месяца — {month_3} ₽", 
            callback_data=f"period_{country_id}_3_{month_3}"
        )],
        [InlineKeyboardButton(
            text=f"6 месяцев (-10%) — {add_strikethrough(month_6_original)}-{month_6_discounted} ₽", 
            callback_data=f"period_{country_id}_6_{month_6_discounted}"
        )],
        [InlineKeyboardButton(
            text=f"12 месяцев (-20%) — {add_strikethrough(month_12_original)}-{month_12_discounted} ₽", 
            callback_data=f"period_{country_id}_12_{month_12_discounted}"
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_tariffs"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_methods_menu(country_id: str, period: str, price: int) -> InlineKeyboardMarkup:
    """Create the payment method selection menu"""
    
    tariff_data = TARIFFS[country_id]
    period_text = f"{period} мес." if period != "1" else "1 мес."
    
    buttons = [
        [InlineKeyboardButton(
            text="СБП | Карта РФ", 
            callback_data=f"payment_sbp_{country_id}_{period}_{price}"
        )],
        [InlineKeyboardButton(
            text="Telegram Stars", 
            callback_data=f"payment_stars_{country_id}_{period}_{price}"
        )],
        [InlineKeyboardButton(
            text="Криптовалюта", 
            callback_data=f"payment_crypto_{country_id}_{period}_{price}"
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data=f"back_to_periods_{country_id}"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_bill(country_id: str, period: str, price: int) -> InlineKeyboardMarkup:
    """Create the payment bill with payment button"""
    
    buttons = [
        [InlineKeyboardButton(
            text="🚀 СБП", 
            callback_data=f"pay_sbp_{country_id}_{period}_{price}"
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data=f"back_to_payment_{country_id}_{period}_{price}"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_device_selection_menu() -> InlineKeyboardMarkup:
    """Create the device selection menu"""
    
    buttons = [
        [
            InlineKeyboardButton(
                text="📱 Android", 
                callback_data="instructions_android"
            ),
            InlineKeyboardButton(
                text="💻 Windows", 
                callback_data="instructions_windows"
            )
        ],
        [
            InlineKeyboardButton(
                text="🍎 Iphone", 
                callback_data="instructions_iphone"
            ),
            InlineKeyboardButton(
                text="🍏 Mac", 
                callback_data="instructions_mac"
            )
        ],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_android_instructions() -> InlineKeyboardMarkup:
    """Create Android instructions menu"""
    
    buttons = [
        [InlineKeyboardButton(
            text="Скачать", 
            url=DOWNLOAD_LINKS["android"]
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_devices"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_windows_instructions() -> InlineKeyboardMarkup:
    """Create Windows instructions menu"""
    
    buttons = [
        [InlineKeyboardButton(
            text="Скачать", 
            url=DOWNLOAD_LINKS["windows"]
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_devices"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_iphone_instructions() -> InlineKeyboardMarkup:
    """Create iPhone instructions menu"""
    
    buttons = [
        [InlineKeyboardButton(
            text="Скачать", 
            url=DOWNLOAD_LINKS["iphone"]
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_devices"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_mac_instructions() -> InlineKeyboardMarkup:
    """Create Mac instructions menu"""
    
    buttons = [
        [InlineKeyboardButton(
            text="Скачать", 
            url=DOWNLOAD_LINKS["mac"]
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_devices"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_help_menu() -> InlineKeyboardMarkup:
    """Create the help menu"""
    
    buttons = [
        [InlineKeyboardButton(
            text="❓ Часто задаваемые вопросы", 
            callback_data="faq"
        )],
        [InlineKeyboardButton(
            text="✉️ Написать в поддержку", 
            url=f"https://t.me/DavirovDS"
        )],
        [InlineKeyboardButton(
            text="🖨️ Пользовательское соглашение", 
            url="https://telegra.ph/Publichnaya-oferta-na-zaklyuchenie-licenzionnogo-dogovora-dlya-ispolzovaniya-VPN-servisa-08-20"
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_faq_menu() -> InlineKeyboardMarkup:
    """Create the FAQ menu"""
    
    buttons = [
        [InlineKeyboardButton(
            text="Где посмотреть стоимость подписки?", 
            callback_data="faq_cost"
        )],
        [InlineKeyboardButton(
            text="Какую информацию хранит сервис?", 
            callback_data="faq_privacy"
        )],
        [InlineKeyboardButton(
            text="У меня не работает VPN что делать?", 
            callback_data="faq_troubleshoot"
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_help"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_partners_menu(user_id: int) -> InlineKeyboardMarkup:
    """Create the partners menu"""
    
    # Generate referral link with user ID
    bot_username = "oweiurbot"  # Bot username
    referral_link = f"https://t.me/{bot_username}?start=cl{user_id}"
    
    buttons = [
        [InlineKeyboardButton(
            text="📤 Отправить друзьям Telegram", 
            url=f"https://t.me/share/url?url={referral_link}&text=Попробуйте%20быстрый%20и%20надежный%20VPN!%20%F0%9F%9A%80%EF%B8%8F"
        )],
        [InlineKeyboardButton(
            text="📤 Отправить друзьям WhatsApp", 
            url=f"https://wa.me/?text=Попробуйте%20быстрый%20и%20надежный%20VPN!%20%F0%9F%9A%80%EF%B8%8F%20{referral_link}"
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_my_account_menu(user_id: int) -> InlineKeyboardMarkup:
    """Create the my account menu"""
    
    buttons = [
        [InlineKeyboardButton(
            text="🎁 Активировать промокод", 
            callback_data="activate_promo"
        )],
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_main"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_promo_code_menu() -> InlineKeyboardMarkup:
    """Create the promo code input menu"""
    
    buttons = [
        [InlineKeyboardButton(
            text="Вернуться", 
            callback_data="back_to_account"
        )]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def generate_user_id() -> int:
    """Generate a unique user ID"""
    # Generate a 10-digit random number
    return random.randint(1000000000, 9999999999)

async def send_referral_notification(referrer_id: int, referred_user_id: int):
    """Send referral notification to referrer when referral makes a purchase"""
    try:
        # Create referral notification message in the style from the screenshot
        notification_text = (
            f"🎉 <b>Поздравляем! Ваш друг купил VPN</b>\n\n"
            f"Ваш реферал (ID: {referred_user_id}) только что оформил подписку!\n\n"
            f"🎁 <b>Ваша награда:</b> 7 дней бесплатного VPN в Германии\n\n"
            f"Нажмите кнопку ниже, чтобы активировать награду!"
        )
        
        # Create inline button similar to the screenshot style
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🎁 Активировать 7 дней бесплатно",
                callback_data=f"activate_referral_reward_{referrer_id}_{referred_user_id}"
            )]
        ])
        
        # Send notification to referrer
        await bot.send_message(
            chat_id=referrer_id,
            text=notification_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        logging.info(f"Sent referral notification to {referrer_id} for referral {referred_user_id}")
        
    except Exception as e:
        logging.error(f"Error sending referral notification: {e}")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command with referral tracking"""
    user_id = message.from_user.id
    
    # Check if this is a referral start
    if message.text and message.text.startswith('/start '):
        try:
            # Extract referral code from start command
            referral_code = message.text.split(' ')[1]
            if referral_code.startswith('cl'):
                referrer_id = int(referral_code[2:])
                
                # Store referral relationship
                if referrer_id not in referral_relationships:
                    referral_relationships[referrer_id] = []
                
                # Only add if not already referred and not self-referral
                if user_id not in referral_relationships[referrer_id] and user_id != referrer_id:
                    referral_relationships[referrer_id].append(user_id)
                    logging.info(f"New referral: {user_id} referred by {referrer_id}")
        except (ValueError, IndexError):
            # Invalid referral code, ignore
            pass
    
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    """Handle button callbacks"""
    global subscription_counter
    await callback.answer()
    
    if callback.data == "tariffs":
        # Show tariffs menu
        await callback.message.edit_text(
            "<b>🌐 Выберите расположение сервера:</b>\n\n⁉️ <a href=\"https://telegra.ph/Kak-vybrat-tarif-08-20\">Как выбрать тариф?</a>",
            reply_markup=get_tariffs_menu(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    
    elif callback.data == "back_to_main":
        # Return to main menu
        await callback.message.edit_text(
            WELCOME_MESSAGE,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    
    elif callback.data == "back_to_tariffs":
        # Return to tariffs menu
        await callback.message.edit_text(
            "<b>🌐 Выберите расположение сервера:</b>\n\n⁉️ <a href=\"https://telegra.ph/Kak-vybrat-tarif-20\">Как выбрать тариф?</a>",
            reply_markup=get_tariffs_menu(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    
    elif callback.data == "instructions":
        # Show device selection menu
        await callback.message.edit_text(
            "⚡ **Выберите устройство:**",
            reply_markup=get_device_selection_menu(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "back_to_devices":
        # Return to device selection menu
        await callback.message.edit_text(
            "⚡ **Выберите устройство:**",
            reply_markup=get_device_selection_menu(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "instructions_android":
        # Show Android instructions
        await callback.message.edit_text(
            "<b>📱 Инструкция для Android:</b>\n\n"
            "1. Скачайте приложение <a href=\"https://play.google.com/store/apps/details?id=com.v2raytun.android\">V2RayTun</a> из Google Play.\n"
            "2. Скопируйте ключ подписки в буфер обмена.\n"
            "3. Откройте приложение <a href=\"https://play.google.com/store/apps/details?id=com.v2raytun.android\">V2RayTun</a>, разрешите доступ к сетям при необходимости.\n"
            "4. Добавьте профиль, нажав плюсик в правом верхнем углу приложения. Далее нажмите \"Добавить из буфера обмена\". Профиль появится в приложении.\n"
            "5. Для подключения к профилю vpn нажмите по центру экрана.",
            reply_markup=get_android_instructions(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    
    elif callback.data == "instructions_windows":
        # Show Windows instructions
        await callback.message.edit_text(
            "<b>💻 Инструкция для Windows:</b>\n\n"
            "1. Скачайте и установите приложение <a href=\"https://storage.v2raytun.com/v2RayTun_Setup.exe\">V2RayTun</a>.\n"
            "2. Скопируйте ключ подписки в буфер обмена.\n"
            "3. Откройте приложение <a href=\"https://storage.v2raytun.com/v2RayTun_Setup.exe\">V2RayTun</a>, разрешите доступ от имени администратора при необходимости.\n"
            "4. Добавьте профиль, нажав плюсик в правом верхнем углу приложения. Далее нажмите \"Добавить из буфера обмена\". Профиль появится в приложении.\n"
            "5. Для подключения к профилю vpn нажмите по центру экрана.",
            reply_markup=get_windows_instructions(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    
    elif callback.data == "instructions_iphone":
        # Show iPhone instructions
        await callback.message.edit_text(
            "<b>🍎 Инструкция для Iphone:</b>\n\n"
            "1. Скачайте приложение <a href=\"https://apps.apple.com/ru/app/v2raytun/id6476628951?platform=iphone\">v2RayTun</a> либо <a href=\"https://apps.apple.com/app/id6450534064\">Streisand</a> из App Store.\n"
            "2. Скопируйте ключ подписки в буфер обмена.\n"
            "3. Запустите приложение, нажмите плюсик -> \"Добавить из буфера\".\n"
            "4. Разрешите вставку ключ-ссылки из буфера.\n"
            "5. Профиль появится в нижней части экрана, нажмите на него и запустите.",
            reply_markup=get_iphone_instructions(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    
    elif callback.data == "instructions_mac":
        # Show Mac instructions
        await callback.message.edit_text(
            "<b>🍏 Инструкция для Mac:</b>\n\n"
            "1. Скачайте и установите приложение <a href=\"https://apps.apple.com/en/app/v2raytun/id6476628951\">V2RayTun</a> из App Store.\n"
            "2. Скопируйте ключ подписки в буфер обмена.\n"
            "3. Откройте приложение <a href=\"https://apps.apple.com/en/app/v2raytun/id6476628951\">V2RayTun</a>.\n"
            "4. Добавьте профиль, нажав плюсик в правом верхнем углу приложения. Далее нажмите \"Добавить из буфера обмена\". Профиль появится в приложении.\n"
            "5. Для подключения к профилю vpn нажмите по центру экрана.",
            reply_markup=get_mac_instructions(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    
    elif callback.data == "help":
        # Show help menu
        await callback.message.edit_text(
            "🆘 **Помощь**",
            reply_markup=get_help_menu(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "back_to_help":
        # Return to help menu
        await callback.message.edit_text(
            "🆘 **Помощь**",
            reply_markup=get_help_menu(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "faq":
        # Show FAQ menu
        await callback.message.edit_text(
            "❓ **Часто задаваемые вопросы:**",
            reply_markup=get_faq_menu(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "faq_cost":
        # Show FAQ about subscription cost
        await callback.message.edit_text(
            "**Где посмотреть стоимость подписки?**\n\n"
            "В меню бота «🔑 Мои ключи» можно посмотреть стоимость указанных дней с учетом всех скидок и активированных промокодов. Указанная стоимость является окончательной на момент оформления.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться", callback_data="back_to_faq")]
            ]),
            parse_mode="Markdown"
        )
    
    elif callback.data == "faq_privacy":
        # Show FAQ about privacy
        await callback.message.edit_text(
            "**Какую информацию хранит сервис?**\n\n"
            "Наш сервис работает с открытым исходным кодом, что позволяет нам открыто заявлять, что мы не собираем и не храним личную информацию пользователей, такую как посещенные ресурсы или сайты, ведь трафик шифруется даже для нас.\n\n"
            "**Какую информацию мы храним?**\n\n"
            "• Публичный ID Telegram\n"
            "• Историю покупок в нашем сервисе\n"
            "• Информацию о вашей подписке",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться", callback_data="back_to_faq")]
            ]),
            parse_mode="Markdown"
        )
    
    elif callback.data == "faq_troubleshoot":
        # Show FAQ about troubleshooting
        await callback.message.edit_text(
            "**У меня не работает VPN что делать?**\n\n"
            "1. **Попробуйте удалить подписку в приложении и добавить ключ обратно.**\n"
            "2. **Отключите сторонние VPN-сервисы.**\n"
            "3. **Попробуйте установить альтернативное приложение:**\n"
            "   • **Android:** v2rayNG, Nekobox\n"
            "   • **Iphone:** Streisand, V2Box, FoXray\n"
            "   • **Windows:** NekoRay\n"
            "   • **MacOS:** Streisand, V2Box, FoXray\n"
            "4. **Обратитесь в техническую поддержку**",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться", callback_data="back_to_faq")]
            ]),
            parse_mode="Markdown"
        )
    
    elif callback.data == "back_to_faq":
        # Return to FAQ menu
        await callback.message.edit_text(
            "❓ **Часто задаваемые вопросы:**",
            reply_markup=get_faq_menu(),
            parse_mode="Markdown"
        )
    

    
    elif callback.data == "partners":
        # Show partners menu
        user_id = callback.from_user.id
        
        # Get referral statistics
        referred_count = len(referral_relationships.get(user_id, []))
        rewards_count = len(referral_rewards.get(user_id, []))
        
        await callback.message.edit_text(
            f"<b>🤝 Партнерская программа</b>\n\n"
            f"🎁 <b>Ваша награда:</b> 7 дней бесплатного VPN в Германии за каждого реферала!\n\n"
            f"<b>Условие для начисления награды:</b>\n"
            f"1. Приглашенный человек ранее не пользовался ботом\n"
            f"2. Приглашенный человек оплатил подписку\n\n"
            f"<b>Ваша статистика:</b>\n"
            f"👣 Вы пригласили: {referred_count}\n"
            f"🎁 Получено наград: {rewards_count}\n\n"
            f"<b>Ваша пригласительная ссылка:</b>\n"
            f"🔗 <code>https://t.me/oweiurbot?start=cl{user_id}</code>\n\n"
            f"<i>Нажмите, чтобы скопировать</i>",
            reply_markup=get_partners_menu(user_id),
            parse_mode="HTML"
        )
    
    elif callback.data == "my_account":
        # Show my account menu
        user_id = callback.from_user.id
        await callback.message.edit_text(
            f"**Мой аккаунт**\n\n"
            f"🆔 **Ваш ID:** `{user_id}`\n"
            f"🤖 **ID бота:** `{BOT_ID}`\n"
            f"💰 **Баланс:** `0₽`",
            reply_markup=get_my_account_menu(user_id),
            parse_mode="Markdown"
        )
    
    elif callback.data == "activate_promo":
        # Show promo code input
        await callback.message.edit_text(
            "🎁 **Введите промокод:**",
            reply_markup=get_promo_code_menu(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "back_to_account":
        # Return to account menu
        user_id = callback.from_user.id
        await callback.message.edit_text(
            f"**Мой аккаунт**\n\n"
            f"🆔 **Ваш ID:** `{user_id}`\n"
            f"🤖 **ID бота:** `{BOT_ID}`\n"
            f"💰 **Баланс:** `0₽`",
            reply_markup=get_my_account_menu(user_id),
            parse_mode="Markdown"
        )
    
    elif callback.data.startswith("tariff_"):
        # User selected a specific tariff
        country_id = callback.data.split("_")[1]
        tariff_data = TARIFFS[country_id]
        
        # Show time periods for selected country
        await callback.message.edit_text(
            f"<b>Тариф: {tariff_data['icon']} {tariff_data['name']} {tariff_data.get('services', '')}</b>\n\n"
            f"💰 Стоимость: <b>{tariff_data['price']} ₽</b> | Месяц\n\n"
            f"При оплате на 6 месяцев — <b>скидка 10%</b>\n"
            f"При оплате на 12 месяцев — <b>скидка 20%</b>",
            reply_markup=get_time_periods_menu(country_id),
            parse_mode="HTML"
        )
    
    elif callback.data.startswith("period_"):
        # User selected a time period
        parts = callback.data.split("_")
        country_id = parts[1]
        period = parts[2]
        price = int(parts[3])
        
        tariff_data = TARIFFS[country_id]
        period_text = f"{period} мес." if period != "1" else "1 мес."
        
        # Show payment methods
        await callback.message.edit_text(
            f"<b>Тариф:</b> {tariff_data['icon']} {tariff_data['name']} {tariff_data.get('services', '')}\n\n"
            f"<b>Период:</b> {period_text}\n\n"
            f"<b>Стоимость:</b> {price} ₽\n\n"
            "<b>Выберите метод оплаты:</b>",
            reply_markup=get_payment_methods_menu(country_id, period, price),
            parse_mode="HTML"
        )
    
    elif callback.data.startswith("payment_"):
        # User selected a payment method
        parts = callback.data.split("_")
        payment_method = parts[1]
        country_id = parts[2]
        period = parts[3]
        price = int(parts[4])
        
        # Show payment bill
        await callback.message.edit_text(
            f"💰 Счёт на оплату: <b>{price}₽</b>\n\n"
            f"⏳ Время на оплату: ~30 минут.",
            reply_markup=get_payment_bill(country_id, period, price),
            parse_mode="HTML"
        )
    
    elif callback.data.startswith("back_to_periods_"):
        # Return to time periods for specific country
        country_id = callback.data.split("_")[3]
        tariff_data = TARIFFS[country_id]
        
        await callback.message.edit_text(
            f"<b>Тариф: {tariff_data['icon']} {tariff_data['name']} {tariff_data.get('services', '')}</b>\n\n"
            f"💰 Стоимость: <b>{tariff_data['price']} ₽</b> | Месяц\n\n"
            f"При оплате на 6 месяцев — <b>скидка 10%</b>\n"
            f"При оплате на 12 месяцев — <b>скидка 20%</b>",
            reply_markup=get_time_periods_menu(country_id),
            parse_mode="HTML"
        )
    
    elif callback.data.startswith("back_to_payment_"):
        # Return to payment methods
        parts = callback.data.split("_")
        country_id = parts[3]
        period = parts[4]
        price = int(parts[5])
        
        tariff_data = TARIFFS[country_id]
        period_text = f"{period} мес." if period != "1" else "1 мес."
        
        await callback.message.edit_text(
            f"<b>Тариф:</b> {tariff_data['icon']} {tariff_data['name']} {tariff_data.get('services', '')}\n\n"
            f"<b>Период:</b> {period_text}\n\n"
            f"<b>Стоимость:</b> {price} ₽\n\n"
            "<b>Выберите метод оплаты:</b>",
            reply_markup=get_payment_methods_menu(country_id, period, price),
            parse_mode="HTML"
        )
    
    elif callback.data.startswith("pay_sbp_"):
        # Handle SBP payment - simulate successful payment and create VPN key
        parts = callback.data.split("_")
        country_id = parts[2]
        period = int(parts[3])
        price = int(parts[4])
        
        # Get tariff and user info
        tariff_data = TARIFFS[country_id]
        user_id = callback.from_user.id
        period_text = f"{period} мес." if period != 1 else "1 мес."
        
        # Show processing message
        await callback.message.edit_text(
            "⏳ <b>Обработка платежа...</b>\n\n"
            "Создаем ваш VPN ключ, пожалуйста подождите...",
            parse_mode="HTML"
        )
        
        try:
            # Create VPN user
            vpn_result = await vpn_service.create_vpn_user(
                user_id=user_id,
                country_id=country_id,
                period_months=period
            )
            
            if vpn_result.get("success"):
                # Store detailed VPN subscription information for this user
                subscription_url = vpn_result.get("subscription_url", "")
                if subscription_url:
                    if user_id not in user_vpn_keys:
                        user_vpn_keys[user_id] = []
                    
                    # Generate subscription number
                    global subscription_counter
                    subscription_number = subscription_counter
                    subscription_counter += 1
                    
                    # Calculate expiry date
                    from datetime import datetime, timedelta
                    expiry_date = datetime.now() + timedelta(days=vpn_result.get("expire_days", 30))
                    
                    # Create subscription object
                    subscription_info = {
                        "subscription_number": subscription_number,
                        "subscription_url": subscription_url,
                        "tariff_name": f"{tariff_data['icon']} {tariff_data['name']}",
                        "expiry_date": expiry_date,
                        "price": price,
                        "period_months": period,
                        "used_gb": 0,  # Start with 0 GB used
                        "status": "active" if expiry_date > datetime.now() else "expired"
                    }
                    
                    user_vpn_keys[user_id].append(subscription_info)
                
                # Check if this user was referred by someone and send notification
                for referrer_id, referred_users in referral_relationships.items():
                    if user_id in referred_users:
                        # Check if referrer already got reward for this user
                        if referrer_id not in referral_rewards:
                            referral_rewards[referrer_id] = []
                        
                        # Only send notification if this is the first purchase (no reward exists yet)
                        reward_exists = any(
                            reward.get("referred_user_id") == user_id 
                            for reward in referral_rewards[referrer_id]
                        )
                        
                        if not reward_exists:
                            # Send referral notification to referrer
                            await send_referral_notification(referrer_id, user_id)
                        break
                
                # Format success message
                key_message = vpn_service.format_user_key_message(
                    vpn_result, 
                    f"{tariff_data['icon']} {tariff_data['name']}", 
                    period_text
                )
                
                # Redirect to subscription detail view instead of showing success message
                await callback.message.edit_text(
                    "✅ <b>VPN ключ успешно создан!</b>\n\n"
                    "Перенаправляем вас к деталям подписки...",
                    parse_mode="HTML"
                )
                
                # Wait a moment and then show the subscription detail
                import asyncio
                await asyncio.sleep(1)
                
                # Show the subscription detail view
                subscription_index = len(user_vpn_keys[user_id]) - 1  # Get the newly created subscription
                subscription = user_vpn_keys[user_id][subscription_index]
                
                # Format expiry date
                expiry_str = subscription["expiry_date"].strftime("%d.%m.%y %H:%M")
                
                # Create clean subscription view matching your exact format
                subscription_text = (
                    f"<b>Подписка №{subscription['subscription_number']} {subscription['tariff_name']}</b>\n"
                    f"⏰ Активна до: {expiry_str} | {subscription['price']} ₽\n\n"
                    f"🔑 <b>Ключ подписки:</b>\n"
                    f"<pre><code>{subscription['subscription_url']}</code></pre>\n\n"
                                    f"📊 Использовано: {subscription.get('used_gb', 0)} ГБ\n"
                f"⏱ Период: {subscription['period_months'] if subscription['period_months'] >= 1 else '7 дней' if subscription.get('is_referral_reward') else f'{subscription['period_months']} дней'}{' мес.' if subscription['period_months'] >= 1 else ''}"
                )
                
                # Create action buttons in the exact layout from your screenshot
                action_buttons = []
                
                # Top row: Single centered import button
                import_url = f"https://import.vpn-club-service.ru/?url={subscription['subscription_url']}#oweiurbot"
                action_buttons.append([
                    InlineKeyboardButton(
                        text="📋 Импорт в V2RayTun", 
                        url=import_url
                    )
                ])
                
                # Middle row: Two buttons side by side
                action_buttons.append([
                    InlineKeyboardButton(
                        text="📚 Инструкция", 
                        callback_data="instructions"
                    ),
                    InlineKeyboardButton(
                        text="🔑 Мои ключи", 
                        callback_data="my_keys"
                    )
                ])
                
                # Bottom row: Single centered back button
                action_buttons.append([
                    InlineKeyboardButton(text="🔙 Вернуться", callback_data="my_keys")
                ])
                
                await callback.message.edit_text(
                    subscription_text,
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=action_buttons)
                )
                
                # Log successful creation
                logging.info(f"VPN key created for user {user_id}, country {country_id}, period {period} months")
                
            else:
                # Handle creation error
                await callback.message.edit_text(
                    "❌ <b>Ошибка при создании VPN ключа</b>\n\n"
                    "Произошла техническая ошибка. Ваш платеж будет возвращен.\n"
                    "Пожалуйста, обратитесь в поддержку.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="✉️ Написать в поддержку", url="https://t.me/DavirovDS")],
                        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                    ])
                )
                
        except Exception as e:
            logging.error(f"Error creating VPN key: {e}")
            await callback.message.edit_text(
                "❌ <b>Техническая ошибка</b>\n\n"
                "Не удалось создать VPN ключ. Обратитесь в поддержку.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✉️ Написать в поддержку", url="https://t.me/DavirovDS")],
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
            )
    
    elif callback.data == "my_keys":
        # Display user's VPN subscriptions in professional format
        user_id = callback.from_user.id
        if user_id in user_vpn_keys and user_vpn_keys[user_id]:
            subscriptions = user_vpn_keys[user_id]
            
            # Create subscription list text
            subscriptions_text = "<b>🔑 Список ваших подписок и ключей:</b>\n\n"
            
            # Create keyboard with subscription management buttons
            keyboard_buttons = []
            for i, sub in enumerate(subscriptions):
                # Create button text with flag, country name, and subscription number
                button_text = f"{sub['tariff_name']} #{sub['subscription_number']}"
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=button_text, 
                        callback_data=f"subscription_{user_id}_{i}"
                    )
                ])
            
            keyboard_buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")])
            
            await callback.message.edit_text(
                subscriptions_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            )
        else:
            await callback.message.edit_text(
                "<b>🔑 У вас пока нет VPN ключей</b>\n\n"
                "Оформите подписку, чтобы получить VPN ключ!",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💎 Тарифы", callback_data="tariffs")],
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
            )
    
    elif callback.data.startswith("subscription_"):
        # Handle subscription detail view
        parts = callback.data.split("_")
        user_id = int(parts[1])
        subscription_index = int(parts[2])
        
        if user_id in user_vpn_keys and subscription_index < len(user_vpn_keys[user_id]):
            subscription = user_vpn_keys[user_id][subscription_index]
            
            # Format expiry date
            expiry_str = subscription["expiry_date"].strftime("%d.%m.%y %H:%M")
            
            # Create detailed subscription view
            subscription_text = (
                f"<b>Подписка №{subscription['subscription_number']} {subscription['tariff_name']}</b>\n"
                f"Активна до: {expiry_str} | {subscription['price']}₽\n\n"
                f"🔑 <b>Ключ подписки:</b>\n"
                f"<pre><code>{subscription['subscription_url']}</code></pre>\n\n"
                f"📊 Использовано: {subscription.get('used_gb', 0)} ГБ\n"
                f"⏱ Период: {subscription['period_months'] if subscription['period_months'] >= 1 else '7 дней' if subscription.get('is_referral_reward') else f'{subscription['period_months']} дней'}{' мес.' if subscription['period_months'] >= 1 else ''}"
            )
            
            # Create action buttons in the exact layout from your screenshot
            action_buttons = []
            
            # Top row: Single centered import button
            import_url = f"https://import.vpn-club-service.ru/?url={subscription['subscription_url']}#oweiurbot"
            action_buttons.append([
                InlineKeyboardButton(
                    text="📋 Импорт в V2RayTun", 
                    url=import_url
                )
            ])
            
            # Middle row: Two buttons side by side
            action_buttons.append([
                InlineKeyboardButton(
                    text="📚 Инструкция", 
                    callback_data="instructions"
                ),
                InlineKeyboardButton(
                    text="🔑 Мои ключи", 
                    callback_data="my_keys"
                )
            ])
            
            # Renew button - only show for expired subscriptions (centered)
            if subscription["status"] == "expired":
                action_buttons.append([
                    InlineKeyboardButton(
                        text="🔄 Продлить подписку", 
                        callback_data=f"renew_{user_id}_{subscription_index}"
                    )
                ])
            
            # Bottom row: Single centered back button
            action_buttons.append([
                InlineKeyboardButton(text="🔙 Вернуться", callback_data="my_keys")
            ])
            
            await callback.message.edit_text(
                subscription_text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=action_buttons)
            )
    

    
    elif callback.data.startswith("renew_"):
        # Handle subscription renewal
        parts = callback.data.split("_")
        user_id = int(parts[1])
        subscription_index = int(parts[2])
        
        if user_id in user_vpn_keys and subscription_index < len(user_vpn_keys[user_id]):
            subscription = user_vpn_keys[user_id][subscription_index]
            
            # Get tariff ID from tariff name
            tariff_id = None
            for tid, tariff_data in TARIFFS.items():
                if tariff_data['name'] in subscription['tariff_name']:
                    tariff_id = tid
                    break
            
            if tariff_id:
                # Show renewal options
                await callback.message.edit_text(
                    f"🔄 <b>Продление подписки</b>\n\n"
                    f"Подписка: {subscription['tariff_name']} #{subscription['subscription_number']}\n"
                    f"Текущая цена: {subscription['price']}₽\n\n"
                    f"Выберите период продления:",
                    parse_mode="HTML",
                    reply_markup=get_time_periods_menu(tariff_id)
                )
            else:
                await callback.message.edit_text(
                    "❌ <b>Ошибка</b>\n\n"
                    "Не удалось определить тариф для продления.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 К подписке", callback_data=f"subscription_{user_id}_{subscription_index}")],
                        [InlineKeyboardButton(text="🔑 Мои ключи", callback_data="my_keys")]
                    ])
                )
    
    elif callback.data.startswith("activate_referral_reward_"):
        # Handle referral reward activation
        
        parts = callback.data.split("_")
        referrer_id = int(parts[3])
        referred_user_id = int(parts[4])
        
        # Verify this is the correct referrer
        if callback.from_user.id != referrer_id:
            await callback.answer("❌ Ошибка: это не ваша награда", show_alert=True)
            return
        
        # Check if reward already exists
        if referrer_id not in referral_rewards:
            referral_rewards[referrer_id] = []
        
        # Check if this specific reward was already claimed
        reward_exists = any(
            reward.get("referred_user_id") == referred_user_id 
            for reward in referral_rewards[referrer_id]
        )
        
        if reward_exists:
            await callback.answer("❌ Награда уже была получена за этого реферала", show_alert=True)
            return
        
        # Show processing message
        await callback.message.edit_text(
            "⏳ <b>Активация награды...</b>\n\n"
            "Создаем ваш бесплатный VPN ключ на 7 дней в Германии...",
            parse_mode="HTML"
        )
        
        try:
            # Create 7-day free VPN in Germany for referrer
            vpn_result = await vpn_service.create_vpn_user(
                user_id=referrer_id,
                country_id="germany",  # Always Germany for referral rewards
                period_months=7/30  # 7 days (7/30 months)
            )
            
            if vpn_result.get("success"):
                # Store VPN subscription information
                subscription_url = vpn_result.get("subscription_url", "")
                if subscription_url:
                    if referrer_id not in user_vpn_keys:
                        user_vpn_keys[referrer_id] = []
                    
                    # Generate subscription number
                    subscription_number = subscription_counter
                    subscription_counter += 1
                    
                    # Calculate expiry date (7 days from now)
                    from datetime import datetime, timedelta
                    expiry_date = datetime.now() + timedelta(days=7)
                     
                     # Create subscription object for referral reward
                    subscription_info = {
                         "subscription_number": subscription_number,
                         "subscription_url": subscription_url,
                         "tariff_name": "🇩🇪 Германия (Реферальная награда)",
                         "expiry_date": expiry_date,
                         "price": 0,  # Free
                         "period_months": 7/30,  # 7 days (7/30 months)
                         "used_gb": 0,
                         "status": "active",
                         "is_referral_reward": True
                     }
                    
                    user_vpn_keys[referrer_id].append(subscription_info)
                
                # Store referral reward record
                reward_record = {
                    "referred_user_id": referred_user_id,
                    "reward_date": datetime.now(),
                    "subscription_number": subscription_number,
                    "subscription_url": subscription_url
                }
                referral_rewards[referrer_id].append(reward_record)
                
                # Show success message
                await callback.message.edit_text(
                    "✅ <b>Реферальная награда активирована!</b>\n\n"
                    f"🎁 <b>Ваша награда:</b> 7 дней бесплатного VPN в Германии\n"
                    f"🔑 <b>Ключ подписки:</b>\n"
                    f"<pre><code>{subscription_url}</code></pre>\n\n"
                    f"📱 Ключ добавлен в раздел «Мои ключи»\n"
                    f"⏰ Активен до: {expiry_date.strftime('%d.%m.%y %H:%M')}",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        # First row: Single centered import button
                        [InlineKeyboardButton(
                            text="📋 Импорт в V2RayTun", 
                            url=f"https://import.vpn-club-service.ru/?url={subscription_url}#oweiurbot"
                        )],
                        # Second row: Two buttons side by side
                        [InlineKeyboardButton(
                            text="📚 Инструкция", 
                            callback_data="instructions"
                        ),
                        InlineKeyboardButton(
                            text="🔑 Мои ключи", 
                            callback_data="my_keys"
                        )],
                        # Third row: Single centered back button
                        [InlineKeyboardButton(
                            text="🏠 Главное меню", 
                            callback_data="back_to_main"
                        )]
                    ])
                )
                
                logging.info(f"Referral reward activated for {referrer_id} from referral {referred_user_id}")
                
            else:
                # Handle creation error
                await callback.message.edit_text(
                    "❌ <b>Ошибка при активации награды</b>\n\n"
                    "Произошла техническая ошибка. Пожалуйста, обратитесь в поддержку.",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="✉️ Написать в поддержку", url="https://t.me/DavirovDS")],
                        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                    ])
                )
                
        except Exception as e:
            logging.error(f"Error activating referral reward: {e}")
            await callback.message.edit_text(
                "❌ <b>Техническая ошибка</b>\n\n"
                "Не удалось активировать награду. Обратитесь в поддержку.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✉️ Написать в поддержку", url="https://t.me/DavirovDS")],
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
            )

async def main():
    """Main function"""
    logging.info("Starting FoxVPN bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
