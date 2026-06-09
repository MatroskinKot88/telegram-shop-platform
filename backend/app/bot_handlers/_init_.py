from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session # Создадим эту функцию ниже
from app.models import User, Company, UserType

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    # 1. Получаем аргумент после /start (например, "company_123")
    # Если аргумента нет, используем заглушку или просим ввести
    company_id = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "default_company"
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name or "Пользователь"

    # 2. Проверяем или создаем пользователя в БД
    stmt = select(User).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Проверяем, существует ли компания (для безопасности)
        comp_stmt = select(Company).where(Company.id == company_id)
        comp_result = await session.execute(comp_stmt)
        company = comp_result.scalar_one_or_none()
        
        if not company:
            # Если компании нет, создаем тестовую (в реальности это делает админ)
            company = Company(id=company_id, name="Тестовая Компания", bot_token="test", theme_config={})
            session.add(company)
            await session.flush() # Чтобы получить ID

        # Создаем нового пользователя
        user = User(
            telegram_id=telegram_id,
            fio=first_name,
            user_type=UserType.B2C, # По умолчанию B2C, пока не выберет
            company_id=company.id
        )
        session.add(user)
        await session.commit()

    # 3. Формируем клавиатуру для выбора типа аккаунта
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="👤 Я частное лицо (B2C)", callback_data="set_type_b2c"),
            InlineKeyboardButton(text="🏢 Я представитель компании (B2B)", callback_data="set_type_b2b")
        ]
    ])

    await message.answer(
        f"Привет, {first_name}! 👋\n\n"
        f"Добро пожаловать в систему заказов.\n"
        f"Пожалуйста, выберите тип вашего аккаунта, чтобы мы могли показать актуальные цены и условия:",
        reply_markup=keyboard
    )

# Заглушки для обработки выбора (допишем на следующем шаге)
@router.callback_query(F.data == "set_type_b2c")
async def set_b2c(callback: types.CallbackQuery):
    await callback.answer("Вы выбрали B2C. Скоро здесь будет ссылка на Mini App!", show_alert=True)

@router.callback_query(F.data == "set_type_b2b")
async def set_b2b(callback: types.CallbackQuery):
    await callback.answer("Вы выбрали B2B. Скоро здесь будет форма регистрации юр. лица!", show_alert=True)