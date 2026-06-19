import telebot
from telebot import types
import os

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
# ===== قاعدة بيانات وهمية عشان يشتغل بدون ملفات خارجية =====
db = {
    'admins': [],
    'clients': {},
    'settings': {
        'welcome_text': 'مرحبا {name}!\n\nأهلاً بك في متجرنا',
        'store_status': 'active'
    },
    'categories': [
        {'id': 1, 'name': 'شحن ألعاب'},
        {'id': 2, 'name': 'بطاقات'},
        {'id': 3, 'name': 'اشتراكات'}
    ],
    'products': [],
    'orders': []
}

# ===== نظام الستيت =====
user_states = {}

def set_state(user_id, state, data=None):
    user_states[user_id] = {'state': state, 'data': data or {}}

def get_state(user_id):
    return user_states.get(user_id, {})

def clear_state(user_id):
    user_states.pop(user_id, None)

def is_admin(user_id):
    if not db['admins']:
        db['admins'].append(user_id)  # أول شخص بيعمل /admin بصير أدمن
        return True
    return user_id in db['admins']

def register_client(user_id, username, first_name):
    if user_id not in db['clients']:
        db['clients'][user_id] = {
            'id': user_id,
            'username': username,
            'first_name': first_name,
            'balance': 0
        }

def get_client(user_id):
    return db['clients'].get(user_id)

def get_settings():
    return db['settings']

def get_store_status():
    return db['settings']['store_status']

def get_categories():
    return db['categories']

# ===== لوحة الأدمن =====
def send_admin_panel(chat_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('📊 الإحصائيات العامة', callback_data='admin_stats'),
        types.InlineKeyboardButton('💰 التقارير المالية', callback_data='admin_finance')
    )
    markup.add(types.InlineKeyboardButton('⚙️ حالة المتجر: [ يعمل ]', callback_data='admin_status'))
    markup.add(
        types.InlineKeyboardButton('🔌 مصادر الربط API', callback_data='admin_api'),
        types.InlineKeyboardButton('📦 الأقسام والمنتجات', callback_data='admin_products')
    )
    markup.add(
        types.InlineKeyboardButton('💳 الإيداعات والمحافظ', callback_data='admin_wallets'),
        types.InlineKeyboardButton('📋 الطلبات', callback_data='admin_orders')
    )
    markup.add(types.InlineKeyboardButton('❌ إلغاء الإجراء', callback_data='cancel_action'))
    
    text = "[ لوحة التحكم ]\n--------------------\n■ مرحباً بك في مركز الإدارة\n■ الرجاء اختيار القسم المطلوب ⬇️"
    bot.send_message(chat_id, text, reply_markup=markup)

# ===== /start - بدون كيبورد تحت =====
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    register_client(user.id, user.username or '', user.first_name or '')
    s = get_settings()
    
    if get_store_status() != 'active':
        bot.send_message(message.chat.id, 'المتجر مغلق حالياً.')
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('🏪 المنتجات', callback_data='browse_store'),
        types.InlineKeyboardButton('📦 طلباتي', callback_data='my_orders')
    )
    markup.add(
        types.InlineKeyboardButton('💰 رصيدي', callback_data='my_balance'),
        types.InlineKeyboardButton('🎁 كود هدية', callback_data='redeem_gift')
    )
    markup.add(types.InlineKeyboardButton('📞 الدعم', callback_data='support'))
    
    welcome = s
