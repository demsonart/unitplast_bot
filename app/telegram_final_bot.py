import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID
from app.database import Database
from app.image_export import ImageExporter
from app.unified_inbox import Channel, UnifiedInbox, LeadStatus

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# FSM STATES
# ═══════════════════════════════════════════════════════════════════════════════

class OrderForm(StatesGroup):
    """FSM для создания заказов"""
    waiting_material = State()
    waiting_quantity = State()
    waiting_size = State()
    waiting_company = State()
    waiting_contact = State()
    waiting_phone = State()
    waiting_email = State()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN BOT
# ═══════════════════════════════════════════════════════════════════════════════

class TelegramFinalBot:
    """
    Production-ready Telegram bot for UNITPLAST SALES OS

    Features:
    - Unified inbox for all channels
    - Multiple document types (KP, catalog, price list, etc)
    - Full order management with FSM
    - Real-time notifications
    - Manager dashboard
    - Customer service features
    """

    def __init__(self, token: str = None, group_id: int = None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.group_id = group_id or TELEGRAM_GROUP_ID

        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()
        self.db = Database()
        self.image_exporter = ImageExporter()
        self.inbox = UnifiedInbox(db=self.db)

        self._setup_handlers()

    def _setup_handlers(self):
        """Register all message handlers"""
        # Main commands
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_admin, Command("admin"))
        self.dp.message.register(self.cmd_debug, Command("debug"))
        self.dp.message.register(self.cmd_catalog, Command("catalog"))
        self.dp.message.register(self.cmd_faq, Command("faq"))
        self.dp.message.register(self.cmd_inbox, Command("inbox"))
        self.dp.message.register(self.cmd_stats, Command("stats"))

        # Old deprecated commands (for backward compatibility)
        self.dp.message.register(self.cmd_deprecated, Command("kp"))
        self.dp.message.register(self.cmd_deprecated, Command("create_kp"))
        self.dp.message.register(self.cmd_deprecated, Command("orders"))
        self.dp.message.register(self.cmd_deprecated, Command("last_orders"))

        # Order form
        self.dp.message.register(self.cmd_order, Command("order"))
        self.dp.message.register(self.process_material, StateFilter(OrderForm.waiting_material))
        self.dp.message.register(self.process_quantity, StateFilter(OrderForm.waiting_quantity))
        self.dp.message.register(self.process_size, StateFilter(OrderForm.waiting_size))
        self.dp.message.register(self.process_company, StateFilter(OrderForm.waiting_company))
        self.dp.message.register(self.process_contact, StateFilter(OrderForm.waiting_contact))
        self.dp.message.register(self.process_phone, StateFilter(OrderForm.waiting_phone))
        self.dp.message.register(self.process_email, StateFilter(OrderForm.waiting_email))

        # Menu button handlers (only when no FSM state active)
        self.dp.message.register(self.handle_menu_button, StateFilter(None))

        # Callbacks
        self.dp.callback_query.register(self.button_handler)

    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    async def cmd_start(self, message: types.Message):
        """🏠 Main menu - Now Mini App based"""
        from aiogram.types import WebAppInfo
        import os

        # Mini App URL from environment or fallback
        mini_app_url = os.environ.get("MINI_APP_URL", "http://localhost:8000/")

        # Mini App is now the primary interface
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                # PRIMARY: Mini App (Main Interface)
                [
                    InlineKeyboardButton(
                        text="🚀 Открыть Mini App",
                        web_app=WebAppInfo(url=mini_app_url)
                    )
                ],
                # SECONDARY: Quick Admin Actions
                [
                    InlineKeyboardButton(text="📬 Email Center", callback_data="btn:inbox"),
                    InlineKeyboardButton(text="📊 Dashboard", callback_data="btn:stats"),
                ],
                [
                    InlineKeyboardButton(text="⚙️ Настройки", callback_data="btn:settings"),
                    InlineKeyboardButton(text="❓ Помощь", callback_data="btn:help"),
                ],
            ]
        )

        await message.answer(
            "🏭 <b>UNITPLAST SALES OS</b>\n\n"
            "<code>REAL_UNITPLAST_MINIAPP_RUNTIME_20260618</code>\n\n"
            "Основная работа теперь выполняется в Mini App.\n\n"
            "Нажмите кнопку ниже, чтобы открыть систему.",
            reply_markup=markup,
            parse_mode="HTML"
        )

    async def cmd_help(self, message: types.Message):
        """❓ Help"""
        help_text = """
<b>📚 Справка</b>

<b>Основные команды:</b>
/start - 🏠 Главное меню
/help - ❓ Эта справка
/admin - 🔐 Админ-панель
/debug - 🛠 Диагностика

<b>Все действия доступны через меню:</b>
📝 Новая заявка
📦 Каталог
💰 Получить КП
📂 Документы
📧 Email
🟩 Авито
📊 Статистика
👨‍💼 Менеджер
⚙ Настройки
❓ FAQ

<b>Поддержка:</b>
📞 +7 (495) 924-50-96
📧 id@unitplast.ru
"""
        await message.answer(help_text, parse_mode="HTML")

    async def cmd_catalog(self, message: types.Message):
        """📦 Product catalog"""
        materials = [
            ("ABS", "Прочный, ударостойкий", "500 ₽/шт"),
            ("PP", "Легкий, гибкий", "400 ₽/шт"),
            ("PET", "Прозрачный, жёсткий", "600 ₽/шт"),
            ("PVC", "Водостойкий", "450 ₽/шт"),
            ("PS", "Хрупкий, дешёвый", "350 ₽/шт"),
            ("Поликарбонат", "Ударопрочный, прозрачный", "800 ₽/шт"),
            ("Акрил", "Прозрачный как стекло", "700 ₽/шт"),
        ]

        catalog_text = "<b>📦 Каталог материалов</b>\n\n"

        for name, description, price in materials:
            catalog_text += f"<b>{name}</b>\n"
            catalog_text += f"  {description}\n"
            catalog_text += f"  💰 {price}\n\n"

        catalog_text += "Нажмите /order чтобы заказать материал"

        await message.answer(catalog_text, parse_mode="HTML")

    async def cmd_faq(self, message: types.Message):
        """❓ FAQ"""
        faq_text = """
<b>❓ Часто задаваемые вопросы</b>

<b>🕐 Какой срок изготовления?</b>
Стандартный срок: 7-14 рабочих дней
Срочные заказы: возможны исключения

<b>📦 Какой минимальный заказ?</b>
Для большинства материалов: 100 шт
Для малого объёма: возможны исключения

<b>💰 Как рассчитывается стоимость?</b>
Стоимость зависит от:
- Материала
- Количества
- Размера и сложности
- Доставки

<b>🚚 Как доставляется товар?</b>
✓ Курьер по Москве
✓ Самовывоз со склада
✓ Доставка по России

<b>📄 Нужен ли договор?</b>
Да, договор направляется после согласования КП

<b>❌ Что если я откажусь от заказа?</b>
Отмена возможна до начала производства

<b>Остались вопросы?</b>
📞 +7 (495) 924-50-96
📧 id@unitplast.ru
"""
        await message.answer(faq_text, parse_mode="HTML")

    async def cmd_inbox(self, message: types.Message):
        """📂 Unified inbox"""
        stats = self.inbox.get_statistics()

        dashboard = (
            "📂 <b>Мой Inbox</b>\n\n"
            f"<b>Всего заявок:</b> {stats['total_leads']}\n\n"
            "<b>По статусам:</b>\n"
        )

        for status, count in stats['by_status'].items():
            dashboard += f"{status}: {count}\n"

        dashboard += (
            "\n<b>По каналам:</b>\n"
            f"📧 Email: {stats['by_channel'].get('email', 0)}\n"
            f"💬 Telegram: {stats['by_channel'].get('telegram', 0)}\n"
            f"📷 Instagram: {stats['by_channel'].get('instagram', 0)}\n"
        )

        await message.answer(dashboard, parse_mode="HTML")

    async def cmd_stats(self, message: types.Message):
        """📊 Statistics"""
        stats = self.inbox.get_statistics()

        stats_text = (
            "📊 <b>Статистика</b>\n\n"
            f"<b>Всего лидов:</b> {stats['total_leads']}\n"
            f"<b>Не назначено:</b> {stats['unassigned']}\n\n"
            "<b>По источникам:</b>\n"
        )

        channels = {
            "email": "📧 Email",
            "instagram": "📷 Instagram",
            "telegram": "💬 Telegram",
            "whatsapp": "💚 WhatsApp",
            "facebook": "👥 Facebook",
        }

        for channel_key, channel_emoji in channels.items():
            count = stats['by_channel'].get(channel_key, 0)
            if count > 0:
                stats_text += f"{channel_emoji}: {count}\n"

        await message.answer(stats_text, parse_mode="HTML")

    async def cmd_admin(self, message: types.Message):
        """🔐 Admin panel"""
        await message.answer(
            "🔐 <b>АДМИН-ПАНЕЛЬ</b>\n"
            "════════════════════════\n\n"
            "<b>Статистика:</b>\n"
            f"👥 Пользователей: {len(self.inbox.leads)}\n"
            f"📦 Заказов: {self.inbox.get_statistics()['total_leads']}\n"
            f"⏱️ Работает: 24/7\n\n"
            "<b>Доступные команды:</b>\n"
            "/debug - Информация о боте\n"
            "/help - Справка\n"
            "/stats - Статистика",
            parse_mode="HTML"
        )

    async def cmd_deprecated(self, message: types.Message):
        """⚠️ Deprecated command handler"""
        cmd = message.text.split()[0] if message.text else "unknown"
        await message.answer(
            f"⚠️ <b>Команда устарела</b>\n\n"
            f"Команда <code>{cmd}</code> больше не поддерживается.\n\n"
            f"Используйте меню для всех действий:\n"
            f"🏠 Нажмите /start\n\n"
            f"Доступные команды:\n"
            f"/start - Главное меню\n"
            f"/help - Справка\n"
            f"/admin - Админ-панель\n"
            f"/debug - Диагностика",
            parse_mode="HTML"
        )

    async def cmd_debug(self, message: types.Message):
        """🐛 Debug information"""
        from datetime import datetime
        import os

        bot_info = (
            "🐛 <b>DEBUG INFORMATION</b>\n"
            "════════════════════════════════════\n\n"
            f"<b>Версия:</b> UNITPLAST SALES OS v2.0\n"
            f"<b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            f"<b>Python:</b> 3.13.14\n"
            f"<b>Статус:</b> 🟢 ONLINE\n\n"
            f"<b>Статистика:</b>\n"
            f"📦 Всего лидов: {self.inbox.get_statistics()['total_leads']}\n"
            f"💾 БД: SQLite ready\n"
            f"📧 Email: {os.getenv('YANDEX_EMAIL', 'N/A')}\n"
            f"🤖 Bot ID: {self.bot.token.split(':')[0]}\n\n"
            f"<b>Модули:</b>\n"
            f"✅ email_reader\n"
            f"✅ telegram_final_bot\n"
            f"✅ image_export\n"
            f"✅ unified_inbox"
        )

        await message.answer(bot_info, parse_mode="HTML")

    async def cmd_order(self, message: types.Message, state: FSMContext):
        """📝 Create new order - Start FSM"""
        await state.set_state(OrderForm.waiting_material)

        materials = ["ABS", "PP", "PET", "PVC", "PS", "Поликарбонат", "Акрил"]
        keyboard = []

        for i in range(0, len(materials), 2):
            row = []
            row.append(InlineKeyboardButton(
                text=materials[i],
                callback_data=f"mat:{materials[i]}"
            ))
            if i + 1 < len(materials):
                row.append(InlineKeyboardButton(
                    text=materials[i + 1],
                    callback_data=f"mat:{materials[i + 1]}"
                ))
            keyboard.append(row)

        keyboard.append([
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
        ])

        await message.answer(
            "📝 <b>Новая заявка</b>\n\n"
            "Выберите материал:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            parse_mode="HTML"
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # FSM HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    async def process_material(self, message: types.Message, state: FSMContext):
        """Process material selection"""
        await state.update_data(material=message.text)
        await state.set_state(OrderForm.waiting_quantity)

        await message.answer(
            "📦 Количество штук:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                    [KeyboardButton(text="❌ Отмена")]
                ],
                resize_keyboard=True
            )
        )

    async def process_quantity(self, message: types.Message, state: FSMContext):
        """Process quantity"""
        if message.text == "🏠 Главное меню":
            await state.clear()
            await self.cmd_start(message)
            return

        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Заявка отменена")
            await self.cmd_start(message)
            return

        if message.text == "⬅ Назад":
            await state.set_state(OrderForm.waiting_material)
            materials = ["ABS", "PP", "PET", "PVC", "PS", "Поликарбонат", "Акрил"]
            keyboard = []
            for i in range(0, len(materials), 2):
                row = []
                row.append(InlineKeyboardButton(
                    text=materials[i],
                    callback_data=f"mat:{materials[i]}"
                ))
                if i + 1 < len(materials):
                    row.append(InlineKeyboardButton(
                        text=materials[i + 1],
                        callback_data=f"mat:{materials[i + 1]}"
                    ))
                keyboard.append(row)
            keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
            await message.answer(
                "📝 <b>Новая заявка</b>\n\nВыберите материал:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode="HTML"
            )
            return

        try:
            quantity = int(message.text)
            await state.update_data(quantity=quantity)
            await state.set_state(OrderForm.waiting_size)

            await message.answer(
                "📏 Размеры (ширина x высота x глубина, мм):",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                        [KeyboardButton(text="❌ Отмена")]
                    ],
                    resize_keyboard=True
                )
            )
        except ValueError:
            await message.answer("❌ Пожалуйста, введите число")

    async def process_size(self, message: types.Message, state: FSMContext):
        """Process size"""
        if message.text == "🏠 Главное меню":
            await state.clear()
            await self.cmd_start(message)
            return

        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Заявка отменена")
            await self.cmd_start(message)
            return

        if message.text == "⬅ Назад":
            await state.set_state(OrderForm.waiting_quantity)
            await message.answer(
                "📦 Количество штук:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                        [KeyboardButton(text="❌ Отмена")]
                    ],
                    resize_keyboard=True
                )
            )
            return

        await state.update_data(size=message.text)
        await state.set_state(OrderForm.waiting_company)

        await message.answer(
            "🏢 Название компании:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                    [KeyboardButton(text="❌ Отмена")]
                ],
                resize_keyboard=True
            )
        )

    async def process_company(self, message: types.Message, state: FSMContext):
        """Process company"""
        if message.text == "🏠 Главное меню":
            await state.clear()
            await self.cmd_start(message)
            return

        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Заявка отменена")
            await self.cmd_start(message)
            return

        if message.text == "⬅ Назад":
            await state.set_state(OrderForm.waiting_size)
            await message.answer(
                "📏 Размеры (ширина x высота x глубина, мм):",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                        [KeyboardButton(text="❌ Отмена")]
                    ],
                    resize_keyboard=True
                )
            )
            return

        await state.update_data(company=message.text)
        await state.set_state(OrderForm.waiting_contact)

        await message.answer(
            "👤 Ваше имя:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                    [KeyboardButton(text="❌ Отмена")]
                ],
                resize_keyboard=True
            )
        )

    async def process_contact(self, message: types.Message, state: FSMContext):
        """Process contact name"""
        if message.text == "🏠 Главное меню":
            await state.clear()
            await self.cmd_start(message)
            return

        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Заявка отменена")
            await self.cmd_start(message)
            return

        if message.text == "⬅ Назад":
            await state.set_state(OrderForm.waiting_company)
            await message.answer(
                "🏢 Название компании:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                        [KeyboardButton(text="❌ Отмена")]
                    ],
                    resize_keyboard=True
                )
            )
            return

        await state.update_data(contact=message.text)
        await state.set_state(OrderForm.waiting_phone)

        await message.answer(
            "📞 Телефон:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                    [KeyboardButton(text="❌ Отмена")]
                ],
                resize_keyboard=True
            )
        )

    async def process_phone(self, message: types.Message, state: FSMContext):
        """Process phone"""
        if message.text == "🏠 Главное меню":
            await state.clear()
            await self.cmd_start(message)
            return

        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Заявка отменена")
            await self.cmd_start(message)
            return

        if message.text == "⬅ Назад":
            await state.set_state(OrderForm.waiting_contact)
            await message.answer(
                "👤 Ваше имя:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                        [KeyboardButton(text="❌ Отмена")]
                    ],
                    resize_keyboard=True
                )
            )
            return

        await state.update_data(phone=message.text)
        await state.set_state(OrderForm.waiting_email)

        await message.answer(
            "📧 Email:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="⬅ Назад"), KeyboardButton(text="🏠 Главное меню")],
                    [KeyboardButton(text="❌ Отмена")]
                ],
                resize_keyboard=True
            )
        )

    async def process_email(self, message: types.Message, state: FSMContext):
        """Process email and create order"""
        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer("❌ Заявка отменена")
            await self.cmd_start(message)
            return

        if message.text == "🏠 Главное меню":
            await state.clear()
            await self.cmd_start(message)
            return

        data = await state.get_data()
        data['email'] = message.text

        # Create lead
        lead_id = self.inbox.create_lead(Channel.TELEGRAM, {
            "user_id": message.from_user.id,
            "username": message.from_user.username or message.from_user.full_name,
            "material": data.get("material"),
            "quantity": data.get("quantity"),
            "size": data.get("size"),
            "company": data.get("company"),
            "contact": data.get("contact"),
            "phone": data.get("phone"),
            "email": data.get("email"),
        })

        # Generate PNG
        kp_number = f"КП-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        image_path = self.image_exporter.generate_commercial_offer({
            "kp_number": kp_number,
            "date": datetime.now().strftime('%d.%m.%Y'),
            "company": data.get("company"),
            "contact_name": data.get("contact"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "material": data.get("material"),
            "quantity": str(data.get("quantity")),
            "size": data.get("size"),
            "color": "На выбор",
            "lead_time": "7-14 дней",
            "cost": "По запросу",
            "description": f"{data.get('material')} пластик"
        })

        # Save to database
        order_id = self.db.add_order(
            email_id=None,
            client_name=data.get("company"),
            client_email=data.get("email"),
            client_phone=data.get("phone"),
            products=data.get("material"),
            delivery_type="Доставка",
            deadline=data.get("deadline", "7-14 дней"),
            comments="",
            pdf_path=image_path
        )

        # Save commercial offer
        self.db.add_commercial_offer(
            order_id=order_id,
            client_name=data.get("company"),
            pdf_path=image_path
        )

        logger.info(f"Order {order_id} created with KP {kp_number}")

        await message.answer(
            f"✅ <b>Заявка создана!</b>\n\n"
            f"<b>Номер:</b> {lead_id}\n"
            f"<b>КП:</b> {kp_number}\n\n"
            f"Менеджер свяжется с вами в ближайшее время.",
            parse_mode="HTML"
        )

        # Notify managers
        if image_path:
            try:
                with open(image_path, 'rb') as photo:
                    await self.bot.send_photo(
                        self.group_id,
                        photo,
                        caption=(
                            f"📝 <b>Новая заявка</b>\n\n"
                            f"🆔 {lead_id}\n"
                            f"🏢 {data.get('company')}\n"
                            f"👤 {data.get('contact')}\n"
                            f"📞 {data.get('phone')}\n"
                            f"📧 {data.get('email')}\n"
                            f"🧱 {data.get('material')}\n"
                            f"📦 {data.get('quantity')} шт\n\n"
                            f"[✅ Взять] [📄 КП] [💬 Ответить]"
                        ),
                        parse_mode="HTML"
                    )
            except Exception as e:
                logger.error(f"Error sending to group: {e}")

        await state.clear()

    # ═══════════════════════════════════════════════════════════════════════════
    # BUTTON HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    async def button_handler(self, query: types.CallbackQuery, state: FSMContext):
        """Handle inline buttons"""
        action = query.data
        await query.answer()  # Remove loading state

        if action == "cancel":
            await state.clear()
            await query.message.delete()
            await self.cmd_start(query.message)

        elif action.startswith("btn:"):
            # Main menu buttons
            button_type = action.split(":", 1)[1]

            if button_type == "order":
                await query.message.delete()
                await self.cmd_order(query.message, state)
            elif button_type == "catalog":
                await query.message.delete()
                await self.cmd_catalog(query.message)
                await self.cmd_start(query.message)
            elif button_type == "stats":
                await query.message.delete()
                await self.cmd_stats(query.message)
                await self.cmd_start(query.message)
            elif button_type == "inbox":
                await query.message.delete()
                await self.cmd_inbox(query.message)
                await self.cmd_start(query.message)
            elif button_type == "faq":
                await query.message.delete()
                await self.cmd_faq(query.message)
                await self.cmd_start(query.message)
            elif button_type == "contacts":
                contacts_text = (
                    "📞 <b>Контакты UNITPLAST</b>\n\n"
                    "📱 Телефон: +7 (495) 924-50-96\n"
                    "📧 Email: id@unitplast.ru\n"
                    "🌐 Сайт: www.unitplast.ru\n\n"
                    "Режим работы: Пн-Пт 09:00-18:00\n\n"
                    "⬇️ Нажмите ниже для главного меню"
                )
                back_markup = InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(text="🏠 Назад в меню", callback_data="btn:home")]]
                )
                await query.message.edit_text(contacts_text, reply_markup=back_markup, parse_mode="HTML")
            elif button_type == "home":
                await query.message.delete()
                await self.cmd_start(query.message)

        elif action.startswith("mat:"):
            material = action.split(":", 1)[1]
            await state.update_data(material=material)
            await state.set_state(OrderForm.waiting_quantity)
            await query.message.edit_text(f"✅ Выбран: {material}\n\n📦 Количество штук:")

    # ═══════════════════════════════════════════════════════════════════════════
    # MENU BUTTON HANDLER
    # ═══════════════════════════════════════════════════════════════════════════

    async def handle_menu_button(self, message: types.Message, state: FSMContext):
        """Handle main menu button clicks"""
        text = message.text

        # Clear any active FSM state
        current_state = await state.get_state()
        if current_state:
            await state.clear()

        # Route menu buttons to handlers
        if text == "🏠 Главное меню":
            await self.cmd_start(message)
        elif text == "📝 Новая заявка":
            await self.cmd_order(message, state)
        elif text == "📦 Каталог":
            await self.cmd_catalog(message)
        elif text == "📊 Статистика":
            await self.cmd_stats(message)
        elif text == "👨‍💼 Менеджер":
            await self.cmd_inbox(message)
        elif text == "❓ FAQ":
            await self.cmd_faq(message)
        elif text == "📞 Контакты":
            await message.answer(
                "📞 <b>Контакты UNITPLAST</b>\n\n"
                "📱 Телефон: +7 (495) 924-50-96\n"
                "📧 Email: id@unitplast.ru\n"
                "🌐 Сайт: www.unitplast.ru\n\n"
                "Режим работы: Пн-Пт 09:00-18:00",
                parse_mode="HTML"
            )
        else:
            # Unknown message - ask for clarification
            await message.answer(
                "❓ Я вас не понял.\n\n"
                "Пожалуйста, используйте меню или команды:\n"
                "/start - Главное меню\n"
                "/order - Новая заявка\n"
                "/catalog - Каталог\n"
                "/help - Справка"
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════════════════════

    async def send_order_to_group(self, summary: str, image_path: str, group_id: int = None):
        """Send order notification with PNG image to manager group"""
        if not image_path or not summary:
            logger.warning(f"Cannot send order: missing summary or image_path")
            return

        # Use provided group_id or fall back to default
        target_group = group_id or self.group_id

        if not target_group or target_group == -1001234567890:
            logger.warning(f"Cannot send: invalid group_id ({target_group})")
            return

        try:
            from aiogram.types import FSInputFile
            photo = FSInputFile(image_path)
            await self.bot.send_photo(
                target_group,
                photo,
                caption=summary,
                parse_mode="HTML"
            )
            logger.info(f"Order notification sent to group {target_group}")
        except Exception as e:
            logger.error(f"Error sending order to group {target_group}: {e}")

    # ═══════════════════════════════════════════════════════════════════════════
    # BOT LIFECYCLE
    # ═══════════════════════════════════════════════════════════════════════════

    async def start(self):
        """Start polling"""
        logger.info("🤖 UNITPLAST SALES OS Bot started")
        await self.dp.start_polling(self.bot)

    async def stop(self):
        """Stop bot"""
        logger.info("🤖 UNITPLAST SALES OS Bot stopped")
        await self.bot.session.close()
