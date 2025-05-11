🌿 EcoSwapChain

EcoSwapChain is a blockchain-powered recommerce platform that addresses the environmental challenges of consumerism and product waste by enabling secure, transparent, and eco-conscious second-hand trading. Traditional resale platforms often lack authenticity, traceability, and trust, leading to fraud and disputes. EcoSwapChain solves these problems by integrating NFT-backed product ownership, escrow-based payments, and carbon credit incentives.
🧠 Key Features

    NFT-backed Products: Each listed product is minted as an NFT, ensuring verifiable authenticity and traceable ownership.

    Escrow-based Transactions: Funds are securely held until both buyer and seller fulfill their obligations.

    SwapCoin Utility Token: A custom Solana token for all payments and incentives.

    Carbon Credit Rewards: Users are rewarded based on sustainability metrics and product transfer count.

    District-based Hub Assignment: Smart logistics with optimal hub assignments for product verification and delivery.

    Secure On-chain Interaction: Private keys are encrypted and stored client-side; all transactions require password-based authorization.

🔧 Tech Stack

    Frontend: React + Vite + Material UI

    Backend: Django + Django REST Framework

    Blockchain: Solana (NFTs, SwapCoin token, ownership transfer)

    Machine Learning: Scikit-learn (Gradient Boosting for sustainability prediction)

    Database: PostgreSQL

    Others: Redis, Celery, WebSockets (Django Channels)

🚀 Installation & Setup
1. Clone the Repository

git clone https://github.com/yourusername/ecoswapchain.git
cd ecoswapchain

2. Backend Setup (Django)

cd backend
python -m venv venv
source venv/bin/activate         # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

3. Frontend Setup (React + Vite)

cd frontend
npm install
npm run dev

🔄 Workflow Overview
System Purpose

EcoSwapChain acts as a middleware between users and the blockchain. It stores crucial blockchain metadata to reduce query load and minimize on-chain transaction costs.

Workflow Overview
User Onboarding

    Register using OTP verification.

    Wallet generated and encrypted using symmetric encryption.

    User receives encryption key (must be stored securely).

    Add a default address in a district with an available shipping hub.

    Get rewarded with 100 SWAPCOINS upon successful registration.

🪙 NFT Minting Flow

    Go to Create Product.

    Fill out the product form.

    On submission, 20 SWAPCOINS are deducted.

    User signs transaction using their stored transaction password.

    NFT minted, transaction hash and address sent to backend and linked to user.

    You can verify the minting at Solana Explorer (Devnet).

🛒 Order Creation & Chat Workflow

    Open a second browser and register a new user.

    New user explores and orders a listed NFT.

    Real-time chat allows negotiation (built using WebSockets).

    Buyer confirms negotiated price.

    Seller performs final confirmation.

📦 Logistics & Shipping Logic

    A background process assigns hubs based on the districts of both parties.

    Shipping methods:

        Swap (platform-verified & shipped)

        Self (user-verified & collected)

✅ Product Verification & Transactions
If shipping method is Swap:

    Hub Manager logs in to verify the product.

    If valid, the system allows:

        Buyer to pay in SWAPCOINS (escrowed).

        Seller to transfer NFT ownership.

If shipping method is Self:

    Seller initiates verification.

    Buyer manually validates the product.

    Both complete payment and ownership transfer.

🔐 All blockchain actions require the transaction password stored during registration.
🔁 Relisting and Rewards

    Ownership history viewable in the NFT detail page.

    Owner can choose to list or unlist the NFT.

    Rewards based on:

        Sustainability Score

        Transfer Count

🏆 Rewards are distributed in SWAPCOINS, calculated using a trained Gradient Boosting Regressor on synthetic data with 90%+ training accuracy.
🛠 Admin Dashboard

    Add shipping hubs via map interface.

    Create routes between hubs.

    Manage logistics visually and efficiently.

🧱 System Architecture

High-level Architecture

Component Diagram
📚 Summary

EcoSwapChain merges blockchain innovation with sustainable commerce. It offers:

    Transparent product history through NFTs.

    Fraud-proof transactions via escrow.

    A carbon-conscious incentive model.

    Real-time order communication and verification.

    Smart logistics with dynamic hub assignments.

    Empowering users to buy and sell responsibly while contributing to a greener planet.
