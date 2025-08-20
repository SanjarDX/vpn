import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, BOT_DESCRIPTION

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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
WELCOME_MESSAGE = f"""**{BOT_DESCRIPTION}**

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
            text=f"6 месяцев (-10%) — {month_6_original}-{month_6_discounted} ₽", 
            callback_data=f"period_{country_id}_6_{month_6_discounted}"
        )],
        [InlineKeyboardButton(
            text=f"12 месяцев (-20%) — {month_12_original}-{month_12_discounted} ₽", 
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
    bot_username = "TunnelFoxRobot"  # You can change this to your bot username
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

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command"""
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=get_main_menu(),
        parse_mode="Markdown"
    )

@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    """Handle button callbacks"""
    await callback.answer()
    
    if callback.data == "tariffs":
        # Show tariffs menu
        await callback.message.edit_text(
            "🌐 Выберите расположение сервера:\n\n⁉️ [Как выбрать тариф?](https://telegra.ph/Kak-vybrat-tarif-08-20)",
            reply_markup=get_tariffs_menu(),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    
    elif callback.data == "back_to_main":
        # Return to main menu
        await callback.message.edit_text(
            WELCOME_MESSAGE,
            reply_markup=get_main_menu(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "back_to_tariffs":
        # Return to tariffs menu
        await callback.message.edit_text(
            "🌐 Выберите расположение сервера:\n\n⁉️ [Как выбрать тариф?](https://telegra.ph/Kak-vybrat-tarif-08-20)",
            reply_markup=get_tariffs_menu(),
            parse_mode="Markdown",
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
            "📱 **Инструкция для Android:**\n\n"
            "1. **Скачайте приложение [V2RayTun](https://play.google.com/store/apps/details?id=com.v2raytun.android) из Google Play.**\n"
            "2. **Скопируйте ключ подписки в буфер обмена.**\n"
            "3. **Откройте приложение [V2RayTun](https://play.google.com/store/apps/details?id=com.v2raytun.android), разрешите доступ к сетям при необходимости.**\n"
            "4. **Добавьте профиль, нажав плюсик в правом верхнем углу приложения. Далее нажмите \"Добавить из буфера обмена\". Профиль появится в приложении.**\n"
            "5. **Для подключения к профилю vpn нажмите по центру экрана.**",
            reply_markup=get_android_instructions(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "instructions_windows":
        # Show Windows instructions
        await callback.message.edit_text(
            "💻 **Инструкция для Windows:**\n\n"
            "1. **Скачайте и установите приложение [V2RayTun](https://storage.v2raytun.com/v2RayTun_Setup.exe).**\n"
            "2. **Скопируйте ключ подписки в буфер обмена.**\n"
            "3. **Откройте приложение [V2RayTun](https://storage.v2raytun.com/v2RayTun_Setup.exe), разрешите доступ от имени администратора при необходимости.**\n"
            "4. **Добавьте профиль, нажав плюсик в правом верхнем углу приложения. Далее нажмите \"Добавить из буфера обмена\". Профиль появится в приложении.**\n"
            "5. **Для подключения к профилю vpn нажмите по центру экрана.**",
            reply_markup=get_windows_instructions(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "instructions_iphone":
        # Show iPhone instructions
        await callback.message.edit_text(
            "🍎 **Инструкция для Iphone:**\n\n"
            "1. **Скачайте приложение [v2RayTun](https://apps.apple.com/ru/app/v2raytun/id6476628951?platform=iphone) либо [Streisand](https://apps.apple.com/app/id6450534064) из App Store.**\n"
            "2. **Скопируйте ключ подписки в буфер обмена.**\n"
            "3. **Запустите приложение, нажмите плюсик -> \"Добавить из буфера\".**\n"
            "4. **Разрешите вставку ключ-ссылки из буфера.**\n"
            "5. **Профиль появится в нижней части экрана, нажмите на него и запустите.**",
            reply_markup=get_iphone_instructions(),
            parse_mode="Markdown"
        )
    
    elif callback.data == "instructions_mac":
        # Show Mac instructions
        await callback.message.edit_text(
            "🍏 **Инструкция для Mac:**\n\n"
            "1. **Скачайте и установите приложение [V2RayTun](https://apps.apple.com/en/app/v2raytun/id6476628951) из App Store.**\n"
            "2. **Скопируйте ключ подписки в буфер обмена.**\n"
            "3. **Откройте приложение [V2RayTun](https://apps.apple.com/en/app/v2raytun/id6476628951).**\n"
            "4. **Добавьте профиль, нажав плюсик в правом верхнем углу приложения. Далее нажмите \"Добавить из буфера обмена\". Профиль появится в приложении.**\n"
            "5. **Для подключения к профилю vpn нажмите по центру экрана.**",
            reply_markup=get_mac_instructions(),
            parse_mode="Markdown"
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
        user_id = generate_user_id()
        await callback.message.edit_text(
            f"🤝 **Партнерская программа**\n\n"
            f"Получите 3 дня подписки за каждого приглашенного друга!\n"
            f"Кроме этого, вы будете получать **30.0%** от всех их покупок!\n\n"
            f"**Условие для начисления награды:**\n"
            f"1. Приглашенный человек ранее не пользовался ботом\n"
            f"2. Приглашенный человек подключился к ВПН или оплатил подписку\n\n"
            f"**Ваша статистика:**\n"
            f"👣 Вы пригласили: 0\n"
            f"🎁 Бонусных дней: 0\n\n"
            f"**Ваша пригласительная ссылка:**\n"
            f"🔗 `https://t.me/TunnelFoxRobot?start=cl{user_id}`\n\n"
            f"*Нажмите, чтобы скопировать*",
            reply_markup=get_partners_menu(user_id),
            parse_mode="Markdown"
        )
    
    elif callback.data == "my_account":
        # Show my account menu
        user_id = generate_user_id()
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
        user_id = generate_user_id()
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
            f"**Тариф: {tariff_data['icon']} {tariff_data['name']} {tariff_data.get('services', '')}**\n\n"
            f"💰 **Стоимость: {tariff_data['price']} ₽ | Месяц**\n\n"
            f"При оплате на 6 месяцев — скидка 10%\n"
            f"При оплате на 12 месяцев — скидка 20%",
            reply_markup=get_time_periods_menu(country_id),
            parse_mode="Markdown"
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
            f"**Тариф: {tariff_data['icon']} {tariff_data['name']} {tariff_data.get('services', '')}**\n\n"
            f"**Период: {period_text}**\n\n"
            f"**Стоимость: {price} ₽**\n\n"
            "**Выберите метод оплаты:**",
            reply_markup=get_payment_methods_menu(country_id, period, price),
            parse_mode="Markdown"
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
            f"💰 **Счёт на оплату: {price}₽**\n\n"
            f"⏳ **Время на оплату: ~30 минут.**",
            reply_markup=get_payment_bill(country_id, period, price),
            parse_mode="Markdown"
        )
    
    elif callback.data.startswith("back_to_periods_"):
        # Return to time periods for specific country
        country_id = callback.data.split("_")[3]
        tariff_data = TARIFFS[country_id]
        
        await callback.message.edit_text(
            f"**Тариф: {tariff_data['icon']} {tariff_data['name']} {tariff_data.get('services', '')}**\n\n"
            f"💰 **Стоимость: {tariff_data['price']} ₽ | Месяц**\n\n"
            f"При оплате на 6 месяцев — скидка 10%\n"
            f"При оплате на 12 месяцев — скидка 20%",
            reply_markup=get_time_periods_menu(country_id),
            parse_mode="Markdown"
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
            f"**Тариф: {tariff_data['icon']} {tariff_data['name']} {tariff_data.get('services', '')}**\n\n"
            f"**Период: {period_text}**\n\n"
            f"**Стоимость: {price} ₽**\n\n"
            "**Выберите метод оплаты:**",
            reply_markup=get_payment_methods_menu(country_id, period, price),
            parse_mode="Markdown"
        )
    
    elif callback.data.startswith("pay_sbp_"):
        # Handle SBP payment (placeholder for now)
        await callback.message.answer("🚀 Платеж через СБП будет интегрирован позже.")
    
    elif callback.data == "my_keys":
        await callback.message.answer("🔑 Здесь будут показаны ваши VPN ключи.")

async def main():
    """Main function"""
    logging.info("Starting FoxVPN bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
