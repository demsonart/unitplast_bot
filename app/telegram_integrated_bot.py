import logging
import os
from typing import Optional
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from app.unified_inbox import Channel, UnifiedInbox, LeadStatus
from app.channel_router import ChannelRouter
from app.file_manager import FileManager
from app.auto_responder import AutoResponder
from app.instagram_manager import InstagramManager
from app.database import Database

logger = logging.getLogger(__name__)

class OrderForm(StatesGroup):
    """FSM states for order form collection"""
    waiting_material = State()
    waiting_quantity = State()
    waiting_size = State()
    waiting_color = State()
    waiting_delivery = State()
    waiting_description = State()
    waiting_contact = State()

class TelegramIntegratedBot:
    """
    Telegram bot with full integration:
    - Unified inbox for all channels
    - Lead management
    - File handling
    - Auto-responder
    - Instagram integration
    """

    def __init__(self, token: str, group_id: int, db: Database = None):
        self.token = token
        self.group_id = group_id
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.db = db

        # Initialize components
        self.inbox = UnifiedInbox(db=db)
        self.router = ChannelRouter(self.inbox)
        self.file_manager = FileManager()
        self.auto_responder = AutoResponder()
        self.instagram_manager = InstagramManager()

        # Setup handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup all message handlers"""
        # Commands
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_inbox, Command("inbox"))
        self.dp.message.register(self.cmd_new_order, Command("order"))
        self.dp.message.register(self.cmd_stats, Command("stats"))
        self.dp.message.register(self.cmd_settings, Command("settings"))

        # FSM handlers for order form
        self.dp.message.register(
            self.process_material_selection,
            StateFilter(OrderForm.waiting_material)
        )
        self.dp.message.register(
            self.process_quantity,
            StateFilter(OrderForm.waiting_quantity)
        )
        self.dp.message.register(
            self.process_size,
            StateFilter(OrderForm.waiting_size)
        )

        # Callback queries
        self.dp.callback_query.register(self.handle_button)

    async def cmd_start(self, message: types.Message):
        """Start command"""
        markup = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📥 Inbox"), KeyboardButton(text="📊 Stats")],
                [KeyboardButton(text="➕ New Order"), KeyboardButton(text="⚙️ Settings")],
            ],
            resize_keyboard=True
        )

        await message.answer(
            "🎯 <b>UNITPLAST Sales OS</b>\n\n"
            "Добро пожаловать в единую систему управления обращениями.\n\n"
            "Все сообщения из Instagram, Email, WhatsApp и других каналов "
            "автоматически поступают сюда.",
            reply_markup=markup,
            parse_mode="HTML"
        )

    async def cmd_inbox(self, message: types.Message):
        """Show unified inbox"""
        try:
            dashboard = self.router.get_dashboard_summary()

            await message.answer(
                dashboard,
                parse_mode="HTML"
            )

            # Get unassigned leads
            unassigned = self.inbox.get_unassigned_leads()

            if unassigned:
                await message.answer(
                    f"\n📋 <b>Новые лиды ({len(unassigned)})</b>\n\n"
                    f"Используйте /take &lt;lead_id&gt; для взятия заявки",
                    parse_mode="HTML"
                )

                for lead in unassigned[:5]:  # Show first 5
                    await self._format_lead_message(message, lead)

        except Exception as e:
            logger.error(f"Error showing inbox: {e}")
            await message.answer(f"❌ Ошибка: {e}")

    async def cmd_new_order(self, message: types.Message, state: FSMContext):
        """Start new order creation via FSM"""
        await state.set_state(OrderForm.waiting_material)

        materials = ["ABS", "PP", "PET", "PVC", "PS", "Поликарбонат", "Акрил"]

        keyboard = []
        for i in range(0, len(materials), 2):
            row = []
            row.append(InlineKeyboardButton(
                text=materials[i],
                callback_data=f"material:{materials[i]}"
            ))
            if i + 1 < len(materials):
                row.append(InlineKeyboardButton(
                    text=materials[i + 1],
                    callback_data=f"material:{materials[i + 1]}"
                ))
            keyboard.append(row)

        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await message.answer(
            "🔨 Выберите материал:",
            reply_markup=markup,
            parse_mode="HTML"
        )

    async def process_material_selection(self, message: types.Message, state: FSMContext):
        """Process material selection"""
        await state.update_data(material=message.text)
        await state.set_state(OrderForm.waiting_quantity)

        await message.answer("📦 Укажите количество (шт):")

    async def process_quantity(self, message: types.Message, state: FSMContext):
        """Process quantity"""
        try:
            quantity = int(message.text)
            await state.update_data(quantity=quantity)
            await state.set_state(OrderForm.waiting_size)

            await message.answer("📏 Укажите размеры (ширина x высота x толщина):")

        except ValueError:
            await message.answer("❌ Пожалуйста, введите число")

    async def process_size(self, message: types.Message, state: FSMContext):
        """Process size"""
        await state.update_data(size=message.text)

        # Create order
        data = await state.get_data()

        lead_id = self.inbox.create_lead(Channel.TELEGRAM, {
            "user_id": message.from_user.id,
            "username": message.from_user.username or message.from_user.full_name,
            "material": data.get("material"),
            "quantity": data.get("quantity"),
            "size": data.get("size"),
            "message": f"Заказ: {data.get('material')} x {data.get('quantity')} шт"
        })

        if lead_id:
            await message.answer(
                f"✅ Заявка создана: <code>{lead_id}</code>\n\n"
                f"Материал: {data.get('material')}\n"
                f"Количество: {data.get('quantity')} шт\n"
                f"Размеры: {data.get('size')}",
                parse_mode="HTML"
            )

            # Notify group
            await self.bot.send_message(
                self.group_id,
                f"📝 Новая заявка: {lead_id}\n\n"
                f"От пользователя: @{message.from_user.username or message.from_user.full_name}",
                parse_mode="HTML"
            )

        await state.clear()

    async def cmd_stats(self, message: types.Message):
        """Show statistics"""
        try:
            stats = self.inbox.get_statistics()

            stats_text = "📊 <b>Статистика</b>\n\n"
            stats_text += f"<b>Всего лидов:</b> {stats['total_leads']}\n\n"

            stats_text += "<b>По каналам:</b>\n"
            for channel, count in stats["by_channel"].items():
                stats_text += f"  • {channel}: {count}\n"

            stats_text += "\n<b>По статусам:</b>\n"
            for status, count in stats["by_status"].items():
                stats_text += f"  • {status}: {count}\n"

            stats_text += f"\n<b>Не назначено:</b> {stats['unassigned']}\n"

            await message.answer(stats_text, parse_mode="HTML")

            # Storage info
            storage_info = self.file_manager.format_storage_info()
            await message.answer(storage_info, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Error showing stats: {e}")
            await message.answer(f"❌ Ошибка: {e}")

    async def cmd_settings(self, message: types.Message):
        """Show settings"""
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🤖 Auto-responder " + ("ON" if self.auto_responder.is_enabled() else "OFF"),
                callback_data="toggle_auto_responder"
            )],
            [InlineKeyboardButton(
                text="📧 Email Settings",
                callback_data="email_settings"
            )],
            [InlineKeyboardButton(
                text="📷 Instagram Settings",
                callback_data="instagram_settings"
            )],
        ])

        await message.answer(
            "⚙️ <b>Настройки</b>",
            reply_markup=markup,
            parse_mode="HTML"
        )

    async def handle_button(self, query: types.CallbackQuery, state: FSMContext):
        """Handle inline buttons"""
        action = query.data

        if action == "toggle_auto_responder":
            self.auto_responder.toggle()
            status = "✅ Включен" if self.auto_responder.is_enabled() else "❌ Отключен"
            await query.answer(f"Auto-responder {status}", show_alert=True)

        elif action.startswith("material:"):
            material = action.split(":", 1)[1]
            await state.update_data(material=material)
            await state.set_state(OrderForm.waiting_quantity)
            await query.message.edit_text(f"Выбран материал: {material}\n\nУкажите количество (шт):")

    async def _format_lead_message(self, message: types.Message, lead: dict):
        """Format lead information for Telegram"""
        try:
            channel = lead.get("channel")
            data = lead.get("data", {})

            text = f"""
<b>Лид:</b> {lead['id']}
<b>Канал:</b> {channel}
<b>Статус:</b> {lead['status']}
<b>Создана:</b> {lead['created_at']}

<b>Данные:</b>
"""

            # Format based on channel
            if channel == "instagram":
                text += f"@{data.get('username', 'unknown')}\n"
                text += f"{data.get('message', '')}\n"
            elif channel == "email":
                text += f"От: {data.get('from', '')}\n"
                text += f"{data.get('message', '')}\n"
            elif channel == "telegram":
                text += f"@{data.get('username', '')}\n"
                text += f"{data.get('message', '')}\n"

            # Add action buttons
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Взять", callback_data=f"take:{lead['id']}"),
                    InlineKeyboardButton(text="💬 Ответить", callback_data=f"reply:{lead['id']}")
                ],
                [
                    InlineKeyboardButton(text="📄 КП", callback_data=f"kp:{lead['id']}"),
                    InlineKeyboardButton(text="📞 Позвонить", callback_data=f"call:{lead['id']}")
                ]
            ])

            await message.answer(text, reply_markup=buttons, parse_mode="HTML")

        except Exception as e:
            logger.error(f"Error formatting lead message: {e}")

    async def notify_group_about_lead(self, lead_id: str):
        """Notify group about new lead"""
        try:
            lead = self.inbox.get_lead(lead_id)

            if not lead:
                return

            notification = self.router._format_notification(
                lead,
                Channel(lead["channel"])
            )

            await self.bot.send_message(
                self.group_id,
                notification,
                parse_mode="HTML"
            )

        except Exception as e:
            logger.error(f"Error notifying group: {e}")

    async def start(self):
        """Start the bot"""
        logger.info("Starting Telegram integrated bot...")
        await self.dp.start_polling(self.bot)

    async def stop(self):
        """Stop the bot"""
        logger.info("Stopping bot...")
        await self.bot.session.close()
