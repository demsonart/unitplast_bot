import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID, TELEGRAM_ADMIN_ID
from .database import Database
from .image_export import ImageExporter

logger = logging.getLogger(__name__)

class OrderStates(StatesGroup):
    waiting_for_client_name = State()
    waiting_for_email = State()
    waiting_for_phone = State()
    waiting_for_products = State()
    waiting_for_quantity = State()
    waiting_for_material = State()
    waiting_for_color = State()
    waiting_for_sizes = State()
    waiting_for_delivery = State()
    waiting_for_deadline = State()
    waiting_for_comments = State()

class TelegramBot:
    def __init__(self, company_name, company_email, company_phone):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()
        self.db = Database()
        self.image_exporter = ImageExporter()
        self.company_name = company_name
        self.company_email = company_email
        self.company_phone = company_phone
        self._setup_handlers()

    def _setup_handlers(self):
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_help, Command("help"))
        self.dp.message.register(self.cmd_kp, Command("kp"))
        self.dp.message.register(self.cmd_orders, Command("orders"))

        # KP flow
        self.dp.message.register(self.kp_client_name, OrderStates.waiting_for_client_name)
        self.dp.message.register(self.kp_email, OrderStates.waiting_for_email)
        self.dp.message.register(self.kp_phone, OrderStates.waiting_for_phone)
        self.dp.message.register(self.kp_products, OrderStates.waiting_for_products)
        self.dp.message.register(self.kp_quantity, OrderStates.waiting_for_quantity)
        self.dp.message.register(self.kp_material, OrderStates.waiting_for_material)
        self.dp.message.register(self.kp_color, OrderStates.waiting_for_color)
        self.dp.message.register(self.kp_sizes, OrderStates.waiting_for_sizes)
        self.dp.message.register(self.kp_delivery, OrderStates.waiting_for_delivery)
        self.dp.message.register(self.kp_deadline, OrderStates.waiting_for_deadline)
        self.dp.message.register(self.kp_comments, OrderStates.waiting_for_comments)

    async def cmd_start(self, message: Message):
        await message.reply(
            f"👋 Добро пожаловать в {self.company_name}!\n\n"
            f"Я помогу вам управлять заказами и коммерческими предложениями.\n\n"
            f"Используйте /help для справки по командам."
        )

    async def cmd_help(self, message: Message):
        help_text = """
📋 <b>Доступные команды:</b>

/start - Начать работу
/kp - Создать коммерческое предложение вручную
/orders - Показать последние заказы
/help - Справка по командам
"""
        await message.reply(help_text, parse_mode="HTML")

    async def cmd_kp(self, message: Message, state: FSMContext):
        await message.reply(
            "📝 Начнем создание коммерческого предложения.\n"
            "Введите ФИ / Название компании клиента:"
        )
        await state.set_state(OrderStates.waiting_for_client_name)
        await state.update_data(kp_data={})

    async def kp_client_name(self, message: Message, state: FSMContext):
        await state.update_data(client_name=message.text)
        await message.reply("Email клиента:")
        await state.set_state(OrderStates.waiting_for_email)

    async def kp_email(self, message: Message, state: FSMContext):
        await state.update_data(client_email=message.text)
        await message.reply("Телефон клиента:")
        await state.set_state(OrderStates.waiting_for_phone)

    async def kp_phone(self, message: Message, state: FSMContext):
        await state.update_data(client_phone=message.text)
        await message.reply("Описание изделий:")
        await state.set_state(OrderStates.waiting_for_products)

    async def kp_products(self, message: Message, state: FSMContext):
        await state.update_data(products=message.text)
        await message.reply("Количество:")
        await state.set_state(OrderStates.waiting_for_quantity)

    async def kp_quantity(self, message: Message, state: FSMContext):
        await state.update_data(quantity=message.text)
        await message.reply("Материал:")
        await state.set_state(OrderStates.waiting_for_material)

    async def kp_material(self, message: Message, state: FSMContext):
        await state.update_data(material=message.text)
        await message.reply("Цвет:")
        await state.set_state(OrderStates.waiting_for_color)

    async def kp_color(self, message: Message, state: FSMContext):
        await state.update_data(color=message.text)
        await message.reply("Размеры:")
        await state.set_state(OrderStates.waiting_for_sizes)

    async def kp_sizes(self, message: Message, state: FSMContext):
        await state.update_data(sizes=message.text)
        await message.reply("Способ доставки:")
        await state.set_state(OrderStates.waiting_for_delivery)

    async def kp_delivery(self, message: Message, state: FSMContext):
        await state.update_data(delivery_type=message.text)
        await message.reply("Срок исполнения:")
        await state.set_state(OrderStates.waiting_for_deadline)

    async def kp_deadline(self, message: Message, state: FSMContext):
        await state.update_data(deadline=message.text)
        await message.reply("Дополнительные комментарии (или пропустите, нажав /skip):")
        await state.set_state(OrderStates.waiting_for_comments)

    async def kp_comments(self, message: Message, state: FSMContext):
        data = await state.get_data()
        comments = message.text if message.text != "/skip" else ""
        data['comments'] = comments

        # Generate PNG image for commercial offer
        client_name = data.get('client_name', 'Unknown')
        kp_number = f"КП-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        image_path = self.image_exporter.generate_commercial_offer({
            "kp_number": kp_number,
            "date": datetime.now().strftime('%d.%m.%Y'),
            "company": client_name,
            "contact_name": client_name,
            "email": data.get('client_email', ''),
            "phone": data.get('client_phone', ''),
            "material": data.get('material', ''),
            "quantity": data.get('quantity', ''),
            "size": data.get('sizes', ''),
            "color": data.get('color', ''),
            "lead_time": data.get('deadline', '7-14 дней'),
            "cost": "По запросу",
            "description": data.get('products', '')
        })

        await state.clear()

        if image_path:
            # Save to DB
            self.db.add_commercial_offer(
                order_id=None,
                client_name=client_name,
                pdf_path=image_path
            )

            # Send to admin as photo
            try:
                photo_file = FSInputFile(image_path)
                await self.bot.send_photo(
                    chat_id=TELEGRAM_ADMIN_ID,
                    photo=photo_file,
                    caption=f"📄 КП для {client_name}\n\nТребует проверки и утверждения перед отправкой клиенту."
                )
                await message.reply(
                    f"✅ КП создано успешно!\n\n"
                    f"Изображение отправлено администратору на проверку."
                )
            except Exception as e:
                logger.error(f"Error sending KP to admin: {e}")
                await message.reply("❌ Ошибка при отправке КП администратору.")
        else:
            await message.reply("❌ Ошибка при создании КП.")

    async def cmd_orders(self, message: Message):
        orders = self.db.get_recent_orders(limit=5)
        if not orders:
            await message.reply("📭 Недавних заказов не найдено.")
            return

        text = "📋 <b>Последние заказы:</b>\n\n"
        for order in orders:
            text += f"""ID: {order[0]}
Клиент: {order[2]}
Email: {order[3]}
Дата: {order[9]}
---
"""
        await message.reply(text, parse_mode="HTML")

    async def send_order_to_group(self, order_summary: str, image_path: str):
        """Sends order summary and PNG image to Telegram group"""
        try:
            image_file = FSInputFile(image_path)
            await self.bot.send_photo(
                chat_id=TELEGRAM_GROUP_ID,
                photo=image_file,
                caption=order_summary,
                parse_mode="HTML"
            )
            logger.info(f"Order with PNG image sent to Telegram group")
        except Exception as e:
            logger.error(f"Error sending order to Telegram: {e}")

    async def start(self):
        logger.info("Telegram bot started")
        await self.dp.start_polling(self.bot)

    async def stop(self):
        await self.bot.session.close()
