# Daily Riddle Wars

Daily Riddle Wars is a Telegram Mini App that delivers a fun and competitive riddle-solving experience. Players can choose between Free, Premium, and VIP modes, earn coins, unlock riddles, and compete on leaderboards for cash or airtime rewards.

---

## Features

- **Daily Riddles**  
  - Free: 7 riddles per day  
  - Premium/VIP: Option to unlock all 50 riddles instantly  
  - Saturday: 10 mandatory riddles for all players (counts toward leaderboard)  

- **Leaderboard & Rewards**  
  - Automatic tracking for Premium and VIP players  
  - Weekly leaderboard updates  
  - Manual payouts in cash or airtime  

- **Coin System**  
  - Daily login reward: 5 coins  
  - Hint cost: 10 coins  
  - Streak rewards:  
    - 3-day streak: +10 coins  
    - 5-day streak: +25 coins  
    - 7-day streak: +40 coins  
  - Refer-a-friend: +10 coins when they buy coins or hints  

- **Admin Panel**  
  - Track winners and payments  
  - Export winners to CSV for manual payout  

---

## Pricing

### Entry Fees
- **Premium Entry**: ₦500  
- **Unlock All Riddles (Premium)**: ₦100  
- **VIP Entry**: ₦2000  
- **Unlock All Riddles (VIP)**: ₦200  

### Coin Packs
- 50 coins = ₦200  
- 100 coins = ₦350  
- 200 coins = ₦600  
- 500 coins = ₦1200  

---

## Tech Stack

- **Backend**: Python (Flask)  
- **Database**: JSON files  
- **Frontend**: Telegram WebApp  
- **Payment Gateway**: Paystack  

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- A Telegram Bot (created via BotFather)
- Paystack account

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/daily-riddle-wars.git
   cd daily-riddle-wars
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_token
   PAYSTACK_SECRET_KEY=your_paystack_secret
   PAYSTACK_PUBLIC_KEY=your_paystack_public
    MONETAG_KEY = "your-monetag-key-here"

   ``` 

4. Run the app:
   ```bash
   python app.py
   ```

5. Set your bot webhook:
   ```bash
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-domain.com/webhook
   ```

---

## File Structure
```
daily-riddle-wars/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Dependencies
├── data/                  # JSON storage
│   ├── users.json
│   ├── scores.json
│   ├── riddles_free.json
│   ├── riddles_premium.json
│   ├── riddles_vip.json
│   └── riddles_saturday.json
├── static/                # Frontend assets
├── templates/             # HTML templates
└── README.md              # This file
```

---

## Gameplay Overview

1. Player chooses Free, Premium, or VIP mode.
2. Riddles are presented daily; hints cost coins.
3. Correct answers earn points (10 points; hints reduce to 7 points).
4. Saturday riddles are mandatory for all.
5. Leaderboard updated weekly; top scorers win prizes.

---

## Rewards & Payments

- **Manual payouts**: Winners receive cash or airtime after admin confirmation.
- **Admin CSV export**: Used for tracking payouts.

---

## License

This project is licensed under the MIT License — you are free to use, modify, and distribute it.
