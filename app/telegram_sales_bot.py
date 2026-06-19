import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from .catalog_manager import CatalogManager
from .google_sheets_manager import GoogleSheetsManager
from .database import Database

logger = logging.getLogger(__name__)

class OrderStates(StatesGroup):
    """FSM states for order form"""
    company_name = State()
    contact_name = State()
    phone = State()
    email = State()
    inn = State()
    material = State()
    quantity = State()
    sizes = State()
    description = State()
    comments = State()
    photo = State()
    confirm = State()

class SalesBot:
    """Sales OS Telegram Bot with full UI"""

    def __init__(self, bot_token: str, admin_id: int, group_id: int):
        self.bot = Bot(token=bot_token)
        self.dp = Dispatcher()
        self.admin_id = admin_id
        self.group_id = group_id
        self.db = Database()
        self.catalog = CatalogManager()
        self.sheets = GoogleSheetsManager()

        self._setup_handlers()

    def _setup_handlers(self):
        """Setup all message and callback handlers"""
        # Commands
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_catalog, Command("catalog"))
        self.dp.message.register(self.cmd_faq, Command("faq"))
        self.dp.message.register(self.cmd_orders, Command("orders"))

        # Order form FSM
        self.dp.message.register(self.process_company_name, OrderStates.company_name)
        self.dp.message.register(self.process_contact_name, OrderStates.contact_name)
        # ... more state handlers

    def main_menu(self) -> ReplyKeyboardMarkup:
        """Build main menu keyboard"""
        buttons = [
            [KeyboardButton(text="📋 Оставить заявку")],
            [KeyboardButton(text="📦 Каталог продукции")],
            [KeyboardButton(text="💰 Получить КП")],
            [KeyboardButton(text="📄 Скачать документы")],
            [KeyboardButton(text="📞 Связаться с менеджером")],
            [KeyboardButton(text="📍 Контакты")],
            [KeyboardButton(text="❓ Частые вопросы")]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    async def cmd_start(self, message: Message, state: FSMContext):
        """Start command - show main menu"""
        await message.answer(
            "👋 Добро пожаловать в UNITPLAST!\n\n"
            "Я помогу вам быстро оставить заявку на пластиковые изделия, "
            "получить коммерческое предложение и связаться с нашим менеджером.\n\n"
            "Выберите действие:",
            reply_markup=self.main_menu()
        )

    async def cmd_help(self, message: Message):
        """Help command"""
        await message.answer(
            "📚 Справка по командам:\n\n"
            "/start - Главное меню\n"
            "/catalog - Каталог продукции\n"
            "/faq - Частые вопросы\n"
            "/orders - Мои заявки\n"
            "/help - Эта справка\n\n"
            "Или просто выберите нужный пункт в меню ниже:",
            reply_markup=self.main_menu()
        )

    async def cmd_catalog(self, message: Message):
        """Show product catalog"""
        materials = self.catalog.get_all_materials()

        buttons = [[InlineKeyboardButton(text=m, callback_data=f"material_{m}")] for m in materials]
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(
            "📦 Выберите материал из каталога:\n\n"
            "(Нажмите на материал, чтобы узнать подробнее)",
            reply_markup=keyboard
        )

    async def cmd_faq(self, message: Message):
        """Show FAQ"""
        faq_list = self.catalog.get_faq_list()

        buttons = [[InlineKeyboardButton(text=title, callback_data=f"faq_{key}")]
                   for key, title in faq_list.items()]
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])

        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(
            "❓ Часто задаваемые вопросы:\n\n"
            "Выберите интересующий вас вопрос:",
            reply_markup=keyboard
        )

    async def cmd_orders(self, message: Message):
        """Show user's orders"""
        # Get orders from database for this user
        await message.answer(
            "📋 Ваши заявки\n\n"
            "(функция будет реализована с интеграцией аккаунтов)"
        )

    async def process_company_name(self, message: Message, state: FSMContext):
        """Process company name from order form"""
        await state.update_data(company_name=message.text)
        await message.answer("Как вас зовут? (Имя контактного лица)")
        await state.set_state(OrderStates.contact_name)

    def get_status_emoji(self, status: str) -> str:
        """Get emoji for order status"""
        statuses = {
            "new": "🟢 Новая",
            "in_progress": "🟡 В работе",
            "quote_sent": "🔵 КП отправлено",
            "negotiation": "🟠 Согласование",
            "production": "🟣 Производство",
            "closed": "⚫ Закрыта"
        }
        return statuses.get(status, "⚪ Неизвестно")

    def format_notification(self, order_data: dict) -> str:
        """Format order notification for manager group"""
        return f"""
🔔 <b>Новая заявка</b>

<b>Компания:</b> {order_data.get('company_name', 'N/A')}
<b>Контакт:</b> {order_data.get('contact_name', 'N/A')}
<b>Телефон:</b> {order_data.get('phone', 'N/A')}
<b>Email:</b> {order_data.get('email', 'N/A')}

<b>Материал:</b> {order_data.get('material', 'N/A')}
<b>Количество:</b> {order_data.get('quantity', 'N/A')}
<b>Размеры:</b> {order_data.get('sizes', 'N/A')}

<b>Номер заявки:</b> {order_data.get('order_id', 'N/A')}
<b>Статус:</b> {self.get_status_emoji('new')}

<b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
