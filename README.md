# 🔶 NOTIF_MANAGER (Notification manager)

---

### Работа процессоров:

```
1. TelegramNotification -> Для работы необходим bot-токен и user_id, т.к сообщение отсылается прямиком в личный чат с пользователем (Используется pool сессий)
2. SMSNotification -> Для работы необходим api_token провайдера sms.ru (Используется pool сессий)
3. EmailNotification -> Для работы необходим address, с которого будут уходить сообщения и app_password, создаваемый в разделе безопасности (Можно настроить pool через asyncio.Queue + workers)
```

---

### Примеры работы процессоров:

#### 1. Telegram - notifictaion:

```
# .env.test:
TELEGRAM_BOT_TOKEN=<ВАШ_ТОКЕН>

# some_file.py
from asyncio import run as run_async

from src.notifications.processors.telegram import TelegramNotificationProcessor
from src.notifications.core.schemas import BaseResponse

async def tg_notif() -> None:
    notif_processor: TelegramNotificationProcessor = TelegramNotificationProcessor(
        token=<ВАШ_ТОКЕН>  # или os.getenv("TELEGRAM_BOT_TOKEN")
    )
    result: BaseResponse = await notif_processor.send(
        text="Hello from notif. Service!",
        chat_id=<ID_НУЖНОГО_ЧАТА_С_ПОЛЬЗОВАТЕЛЕМ>
    )
    print(result)  # Опционально, для просмотра результата
    
run_async(tg_notif())
```

---

#### 2. SMS - notification:

```
# .env.test:
SMS_RU_TOKEN=<ВАШ_ТОКЕН>

# some_file.py
from asyncio import run as run_async

from src.notifications.processors.sms import SMSNotificationProcessor
from src.notifications.core.schemas import BaseResponse

async def sms_notif() -> None:
    notif_processor: SMSNotificationProcessor = SMSNotificationProcessor(
        token=<ВАШ_ТОКЕН>  # или os.getenv("SMS_RU_TOKEN")
    )
    result: BaseResponse = await notif_processor.send(
        text="Hello phone!",
        phone_number=<НУЖНЫЙ_НОМЕР_ТЕЛЕФОНА>
    )
    print(result)  # Опционально, для просмотра результата
    
run_async(sms_notif())
```

---

#### 3. Email -> notification:

```
# .env.test:
GMAIL_ADDRESS=<АДРЕСС_С_КОТОРОГО_БУДУТ_УХОДИТЬ_ПИСЬМА>
GMAIL_APP_PASSWORD=<ПАРОЛЬ_ПРИЛОЖЕНИЯ_ДАННОГО_GMAIL_Адрес>

# some_file.py
from asyncio import run as run_async

from src.notifications.processors.email import GmailNotificationProcessor
from src.notifications.core.schemas import BaseResponse

async def gmail_notif() -> None:
    notif_processor: GmailNotificationProcessor = GmailNotificationProcessor(
        # Все базовые параметры уже переданы, главные из них:
        # gmail_address=<GMAIL_ADDRESS>,
        # gmail_app_password=<GMAIL_APP_PASSWORD>
    )
    result: BaseResponse = await notif_processor.send(
        text="Hello from another domain",
        subject=<ТЕМА_СООБЩЕНИЯ>,
        to_email=<НА_КАКОЙ_EMAIL_ОТПРАВИТЬ>
    )
    print(result)  # Опционально, для просмотра результата
    
run_async(gmail_notif())
```

---

### Доп. инструменты:

#### Линтер:
```bash
flake8 ./
```

#### Типизатор:
```bash
mypy ./
```

---
