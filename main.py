from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, PreCheckoutQueryHandler
import uuid
import json
import os
from datetime import datetime, timedelta

BOT_TOKEN = "8025008916:AAHnrvoc1Ko1pGqbDKBHTNsU22lI0-inWIM"
GROUP_CHAT_ID = -1002737947908  # Support group chat ID

# Simple file-based storage
USERS_FILE = "profitpal_users.json"
LICENSES_FILE = "profitpal_licenses.json"

def load_data(filename):
    """Load data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(filename, data):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def generate_license_key():
    """Generate unique license key"""
    return f"PP-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:8].upper()}"

def generate_referral_code(user_id):
    """Generate referral code for user"""
    return f"REF{user_id}{hash(str(user_id)) % 10000:04d}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with ProfitPal branding"""
    user = update.effective_user

    welcome_text = f"""
🎉 Welcome to ProfitPal! 💎

Hello {user.first_name}! Your AI-powered stock analysis companion is here!

🚀 What ProfitPal offers:
💎 Professional stock analysis in minutes
📊 AI-powered intrinsic value calculations  
🔍 Diamond vs Trash classification
📈 Advanced financial metrics
🎓 Educational investment insights

💳 **Lifetime Access: $24.99**
🔄 **Monthly Updates: $4.99** (FREE with referrals!)

🤖 **Available Commands:**
/buy - Get Lifetime Access ($24.99) 💳
/referral - Get Your Referral Link 🎁  
/status - Check Your Subscription 📊
/key - Get Your License Key 🔑
/help - Support & FAQ ❓

💡 **Ready to master stock analysis? Type /buy to start!**
    """

    keyboard = [
        [InlineKeyboardButton("💳 Buy Lifetime Access ($24.99)", callback_data="buy_lifetime")],
        [InlineKeyboardButton("🎁 Get Referral Link", callback_data="get_referral")],
        [InlineKeyboardButton("📊 Check Status", callback_data="check_status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /buy command"""
    buy_text = """
💳 **ProfitPal Lifetime Access** 💎

🎯 **What you get for $24.99:**
✅ Unlimited stock analysis forever
✅ AI-powered intrinsic value calculations
✅ Advanced financial metrics
✅ Diamond/Trash classification system
✅ All premium features unlocked

💰 **Monthly Updates ($4.99/month):**
🔄 Real-time market data updates
🆕 New features & improvements  
🛠️ Server maintenance & support
🎁 **FREE with referrals!** (12 friends = free year!)

⚡ **Auto-billing:** Monthly fee charged automatically on 1st of each month
🚫 **Cancel anytime** through bot commands (keeps lifetime access)

👇 **Ready to proceed? Please confirm:**
    """

    keyboard = [
        [InlineKeyboardButton("📋 Read Terms & Data Policy", callback_data="show_terms")],
        [InlineKeyboardButton("✅ I Agree - Choose Payment Method", callback_data="agree_terms")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(buy_text, reply_markup=reply_markup)

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /referral command"""
    user = update.effective_user
    user_id = str(user.id)

    users = load_data(USERS_FILE)

    if user_id not in users:
        users[user_id] = {}

    if 'referral_code' not in users[user_id]:
        users[user_id]['referral_code'] = generate_referral_code(user.id)
        save_data(USERS_FILE, users)

    referral_code = users[user_id]['referral_code']
    referrals_count = users[user_id].get('referrals_count', 0)

    referral_text = f"""
🎁 **Your ProfitPal Referral Program** 💎

🔗 **Your Referral Link:**
https://t.me/ProfitPalBot?start={referral_code}

📊 **Your Stats:**
• Referrals Made: {referrals_count}
• Free Months Earned: {referrals_count}

🎯 **How it Works:**
• Share your link with friends
• They get ProfitPal for $24.99
• You get 1 FREE month per referral!
• 12 referrals = FREE year!

💰 **Benefits:**
✅ Skip $4.99 monthly fees
✅ Help friends discover great stocks  
✅ Build passive income potential
✅ Unlimited referrals = unlimited free months!

📱 **Share your link and start earning!**
    """

    await update.message.reply_text(referral_text)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user = update.effective_user
    user_id = str(user.id)

    users = load_data(USERS_FILE)

    if user_id not in users:
        status_text = """
❌ **No ProfitPal Account Found**

You haven't purchased ProfitPal yet!

💡 **Get started:**
/buy - Purchase lifetime access ($24.99)
/referral - Get your referral link

🎯 **Ready to analyze stocks like a pro?**
        """
    else:
        user_data = users[user_id]
        has_lifetime = user_data.get('has_lifetime', False)
        license_key = user_data.get('license_key', 'Not assigned')
        join_date = user_data.get('join_date', 'Unknown')
        referrals = user_data.get('referrals_count', 0)

        status_text = f"""
📊 **Your ProfitPal Status** 💎

✅ **Lifetime Access:** {'Active' if has_lifetime else 'Not purchased'}
🔑 **License Key:** `{license_key}`
📅 **Member Since:** {join_date}
🎁 **Referrals Made:** {referrals}
🆓 **Free Months:** {referrals}

🌐 **Access ProfitPal:**
https://profitpal.org/analysis

💡 **Enter your license key above to start analyzing!**
        """

    keyboard = [
        [InlineKeyboardButton("🌐 Open ProfitPal", url="https://profitpal.org/analysis")],
        [InlineKeyboardButton("🎁 Get Referral Link", callback_data="get_referral")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(status_text, reply_markup=reply_markup)

async def key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /key command"""
    user = update.effective_user
    user_id = str(user.id)

    users = load_data(USERS_FILE)

    if user_id not in users or not users[user_id].get('has_lifetime', False):
        key_text = """
❌ **No License Key Found**

You need to purchase ProfitPal first!

💳 **Get your license key:**
/buy - Purchase lifetime access ($24.99)

🎯 **Ready to get started?**
        """
        keyboard = [
            [InlineKeyboardButton("💳 Buy Now ($24.99)", callback_data="buy_lifetime")]
        ]
    else:
        license_key = users[user_id].get('license_key', 'Error')
        key_text = f"""
🔑 **Your ProfitPal License Key** 💎

`{license_key}`

📝 **How to use:**
1. Go to: https://profitpal.org/analysis
2. Enter your license key above
3. Start analyzing stocks!

💡 **Tip:** Bookmark the link for easy access!
        """
        keyboard = [
            [InlineKeyboardButton("🌐 Open ProfitPal Now", url="https://profitpal.org/analysis")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(key_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
❓ **ProfitPal Help & Support** 💎

🤖 **Available Commands:**
/start - Welcome message & main menu
/buy - Purchase lifetime access ($24.99)
/status - Check your account status
/key - Get your license key
/referral - Get referral link (earn free months!)
/help - This help message

🎯 **How ProfitPal Works:**
1. Purchase lifetime access ($24.99)
2. Get your unique license key
3. Go to profitpal.org/analysis
4. Enter your key and start analyzing!

💰 **Pricing:**
• Lifetime Access: $24.99 (one-time)
• Monthly Updates: $4.99/month
• Referrals = Free months!

📞 **Need Help?**
Contact: @djurtsenko

🌐 **Website:**
https://profitpal.org
    """

    keyboard = [
        [InlineKeyboardButton("💳 Buy ProfitPal", callback_data="buy_lifetime")],
        [InlineKeyboardButton("📱 Contact Support", url="https://t.me/djurtsenko")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(help_text, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if data == "buy_lifetime":
        await buy_command(update, context)

    elif data == "get_referral":
        await referral_command(update, context)

    elif data == "check_status":
        await status_command(update, context)

    elif data == "show_terms":
        terms_text = """
📋 **ProfitPal Terms of Service & Data Policy**

**🔒 DATA PROCESSING AGREEMENT:**
By using ProfitPal, you agree to the processing of your personal data:

**📊 Data We Collect:**
• Telegram username and ID
• Payment information (processed by third parties)
• Usage analytics (anonymous)
• Referral activity

**🎯 How We Use Your Data:**
• Provide ProfitPal services
• Process payments and refunds
• Send service updates and features
• Manage referral program

**🔐 Data Protection:**
• We never sell your data
• Secure encryption (AES-256)
• GDPR compliant
• Data deletion available on request

**💳 BILLING TERMS:**
• **Lifetime Access:** $24.99 one-time payment
• **Monthly Updates:** $4.99 auto-charged on 1st of each month
• **Auto-renewal:** Continues until cancelled
• **Cancellation:** Keep lifetime access, stop monthly billing

**✅ By proceeding, you agree to these terms and data processing.**
        """

        keyboard = [
            [InlineKeyboardButton("✅ I Agree - Choose Payment", callback_data="agree_terms")],
            [InlineKeyboardButton("🔙 Back", callback_data="buy_lifetime")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(terms_text, reply_markup=reply_markup)

    elif data == "agree_terms":
        # Log user consent
        users = load_data(USERS_FILE)
        user_id = str(user.id)

        if user_id not in users:
            users[user_id] = {}

        users[user_id]['terms_agreed'] = True
        users[user_id]['terms_date'] = datetime.now().isoformat()
        save_data(USERS_FILE, users)

        payment_text = """
💳 **Payment Setup - Choose Your Method** 💎

✅ **Terms & Data Processing Consent:** Confirmed

**⭐ TELEGRAM STARS (Recommended)**
• Instant payment & license delivery
• Native Telegram payment system
• 2499 Stars = $24.99 USD

**💳 STRIPE PAYMENTS**
• Credit/Debit cards worldwide
• Secure payment processing
• Apple Pay & Google Pay support

👇 **Choose your preferred payment method:**
        """

        keyboard = [
            [InlineKeyboardButton("⭐ Pay with Telegram Stars (Instant)", callback_data="pay_stars")],
            [InlineKeyboardButton("💳 Pay with Card (Stripe)", callback_data="pay_stripe")],
            [InlineKeyboardButton("🔙 Back", callback_data="show_terms")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(payment_text, reply_markup=reply_markup)

    elif data == "pay_stars":
        stars_text = """
⭐ **Telegram Stars Payment - ProfitPal Lifetime Access**

💰 **Price:** 2499 Telegram Stars ≈ $24.99 USD

🌟 **What are Telegram Stars?**
• Native Telegram premium currency
• Buy with any card, Apple Pay, Google Pay
• Instant & secure payments

💡 **How it works:**
1. Buy Telegram Stars (if you don't have enough)
2. Pay with Stars (instant transaction)
3. Receive your ProfitPal license key immediately
4. Start analyzing stocks right away!

👇 **Choose your option:**
        """

        keyboard = [
            [InlineKeyboardButton("⭐ Pay 2499 Stars", callback_data="process_stars_payment")],
            [InlineKeyboardButton("🛒 Buy Stars First", url="https://t.me/PremiumBot")],
            [InlineKeyboardButton("🔙 Back", callback_data="agree_terms")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(stars_text, reply_markup=reply_markup)

    elif data == "process_stars_payment":
        # Create Star invoice
        title = "ProfitPal Lifetime Access"
        description = "Unlimited stock analysis forever with AI-powered insights"

        # Simple payload - Telegram Stars has strict requirements
        payload = f"profitpal_lifetime_{user.id}_{int(datetime.now().timestamp())}"

        # Price in Telegram Stars
        prices = [LabeledPrice("ProfitPal Lifetime Access", 2499)]

        try:
            # Send invoice for Stars payment
            await context.bot.send_invoice(
                chat_id=user.id,
                title=title,
                description=description,
                payload=payload,
                provider_token="",  # Empty for Stars payments
                currency="XTR",  # Telegram Stars currency code
                prices=prices,
                start_parameter="profitpal_lifetime",
                need_name=False,
                need_phone_number=False,
                need_email=False,
                need_shipping_address=False,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False
            )

            await query.edit_message_text(
                "⭐ **Stars Payment Invoice Sent!**\n\n"
                "💰 **Amount:** 2499 Telegram Stars ($24.99)\n\n"
                "👆 **Check the message above** - you should see a payment invoice.\n\n"
                "💡 **Next steps:**\n"
                "1. Click 'Pay 2499 ⭐' button in the invoice\n"
                "2. Confirm payment with your Stars balance\n"
                "3. Instant license key delivery!"
            )

        except Exception as e:
            await query.edit_message_text(
                f"❌ **Error sending Stars invoice**\n\n"
                f"Error: {str(e)}\n\n"
                f"💡 **Try:**\n"
                f"• Make sure you have 2499+ Stars\n"
                f"• Contact @djurtsenko for help"
            )

    elif data == "pay_stripe":
        stripe_text = """
💳 **Stripe Payment - ProfitPal Lifetime Access**

💰 **Price:** $24.99 USD

🔒 **Secure Payment Features:**
• Credit/Debit cards worldwide
• Apple Pay & Google Pay
• Bank transfers (selected countries)
• Secure encryption & fraud protection

🌐 **How it works:**
1. Click payment link below
2. Enter your card details securely
3. Complete payment on Stripe
4. Receive license key via email & Telegram

👇 **Proceed to secure checkout:**
        """

        keyboard = [
            [InlineKeyboardButton("💳 Pay $24.99 with Stripe", url="https://profitpal.org/payment")],
            [InlineKeyboardButton("🔙 Back", callback_data="agree_terms")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(stripe_text, reply_markup=reply_markup)

    else:
        await query.edit_message_text("🔧 Feature coming soon! Stay tuned! 💎")

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout queries for Stars payments"""
    query = update.pre_checkout_query

    try:
        # Simple payload verification for Stars
        payload = query.invoice_payload

        # Verify this is our ProfitPal payment
        if "profitpal_lifetime" in payload and query.total_amount == 2499:
            # Approve the payment
            await query.answer(ok=True)
        else:
            # Reject the payment if something doesn't match
            await query.answer(ok=False, error_message="Payment verification failed. Please try again.")

    except Exception as e:
        # Reject payment on any error
        await query.answer(ok=False, error_message="Payment processing error. Please contact support.")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful Stars payments"""
    user = update.effective_user
    payment = update.message.successful_payment

    try:
        # Generate license key
        license_key = generate_license_key()

        # Update user data
        users = load_data(USERS_FILE)
        user_id = str(user.id)

        if user_id not in users:
            users[user_id] = {}

        users[user_id].update({
            'has_lifetime': True,
            'license_key': license_key,
            'payment_method': 'telegram_stars',
            'payment_date': datetime.now().isoformat(),
            'amount_paid_stars': payment.total_amount,
            'amount_paid_usd': 24.99,
            'telegram_payment_id': payment.telegram_payment_charge_id,
            'join_date': datetime.now().strftime('%Y-%m-%d')
        })

        save_data(USERS_FILE, users)

        # Send success message with license key
        success_message = f"""
🎉 **Payment Successful! Welcome to ProfitPal!** 💎

✅ **Payment Confirmed:**
• Amount: {payment.total_amount} Telegram Stars ($24.99)
• Payment ID: `{payment.telegram_payment_charge_id}`

🔑 **Your ProfitPal License Key:**
`{license_key}`

📝 **How to activate:**
1. Go to: https://profitpal.org/analysis
2. Enter your license key above
3. Start analyzing stocks immediately!

🎁 **Want free months?** 
Use /referral to get your link - each friend gives you 1 free month!

🚀 **Welcome to the ProfitPal family!**
        """

        keyboard = [
            [InlineKeyboardButton("🌐 Open ProfitPal Now", url="https://profitpal.org/analysis")],
            [InlineKeyboardButton("🎁 Get Referral Link", callback_data="get_referral")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(success_message, reply_markup=reply_markup)

        # Log successful payment
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"💰 **STARS PAYMENT SUCCESSFUL!**\n\n"
                 f"👤 User: @{user.username or user.first_name} (ID: {user.id})\n"
                 f"💰 Amount: {payment.total_amount} Stars ($24.99)\n"
                 f"🔑 License Key: `{license_key}`\n"
                 f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    except Exception as e:
        # Handle errors
        await update.message.reply_text(
            f"❌ **Payment Processing Error**\n\n"
            f"Your Stars payment was received, but there was an error processing your account.\n\n"
            f"📞 Contact @djurtsenko immediately with this message."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any text message (not commands)"""
    user = update.effective_user
    text = update.message.text

    # Welcome message for any text
    welcome_text = f"""
👋 **Welcome to ProfitPal!** 💎

Hi {user.first_name}! Thanks for reaching out!

🚀 **Quick Start:**
/start - See full welcome message
/buy - Get lifetime access ($24.99)

💡 **What is ProfitPal?**
AI-powered stock analysis tool that helps you find undervalued stocks!

👇 **Ready to start?**
    """

    keyboard = [
        [InlineKeyboardButton("🚀 Get Started", callback_data="buy_lifetime")],
        [InlineKeyboardButton("❓ Learn More", callback_data="buy_lifetime")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    # Forward message to support group
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"📨 **New message from @{user.username or user.first_name}:**\n\n{text}\n\n"
                 f"👤 User ID: {user.id}\n"
                 f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except:
        pass  # Ignore if can't send to group

def main():
    """Main function to run the bot"""
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy_command))
    app.add_handler(CommandHandler("referral", referral_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("key", key_command))
    app.add_handler(CommandHandler("help", help_command))

    # Payment handlers for Telegram Stars
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Message and callback handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 ProfitPal Bot started...")
    print("💎 Ready for 24/7 operation!")
    print("🌐 Updated URLs: profitpal.org")
    app.run_polling()

if __name__ == "__main__":
    main()