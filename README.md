# EcoSwapChain 

EcoSwapChain is a blockchain-powered recommerce platform that addresses the environmental challenges of consumerism and product waste by enabling secure, transparent, and eco-conscious second-hand trading. Traditional resale platforms often lack authenticity, traceability, and trust, leading to fraud and disputes. EcoSwapChain solves these problems by integrating NFT-backed product ownership, escrow-based payments, and carbon credit incentives.

## 🧠 Key Features

  **NFT-backed Products**
    : Each listed product is minted as an NFT, ensuring verifiable authenticity and traceable ownership.

  **Escrow-based Transactions**
    : Funds are securely held until both buyer and seller fulfill their obligations.

  **SwapCoin Utility Token**
    : A custom Solana token for all payments and incentives.

  **Carbon Credit Rewards**
    : Users are rewarded based on sustainability metrics and product transfer count.

  **District-based Hub Assignment**
    : mart logistics with optimal hub assignments for product verification and delivery.

  **Secure On-chain Interaction**
    : Private keys are encrypted and stored client-side; all transactions require password-based authorization.

## 🔧 Tech Stack

   **Frontend: React + Vite + Material UI**

   **Backend: Django + Django REST Framework**

   **Blockchain: Solana** (NFTs, SwapCoin token, ownership transfer)

   **Machine Learning: Scikit-learn** (Gradient Boosting for sustainability prediction)

   **Database: PostgreSQL**

   **Others: Redis, Celery, WebSockets** (Django Channels)

## 🚀 Installation & Setup

To run this project locally, you must run three servers simultaneously:**Django**, **React**, and **Express** (microservice).
Before that, **blockchain** setup is required.

### BlockChain SetUp(Solana)

#### 🧱 Solana CLI & SPL Token CLI Installation

##### 🪟 Windows Installation

1. Install Git & Windows Subsystem for Linux (WSL)

2. Install Git for Windows.

3. Enable WSL and install Ubuntu from the Microsoft Store.

4. Open the Ubuntu terminal and continue with the Linux instructions below.

(Alternative - Native Windows using Git Bash)

1. sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

2. Add Solana to PATH manually if not prompted:

3. export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

4. Restart terminal and verify installation:

solana --version

##### 🐧 Linux Installation

1. Install Solana CLI

2. sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

3. Add Solana to PATH

4. export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

5. Persist it by adding to ~/.bashrc or ~/.zshrc:

6. source ~/.bashrc

7. Verify Installation

solana --version

##### Set Devnet for Testing

solana config set --url https://api.devnet.solana.com

##### 💼 Solana Wallet Setup

1. Generate a New Keypair

solana-keygen new --outfile ~/my-wallet.json

2. 🔐 Save the mnemonic phrase securely.

3. Set Wallet as Default

solana config set --keypair ~/my-wallet.json

4. Airdrop SOL to Wallet (Devnet only)

solana airdrop 2

#### 💰 SPL Token Creation (Requires Rust)

##### 🦀 Rust Installation

**Linux**

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

source $HOME/.cargo/env

Verify:

rustc --version

cargo --version

**Windows**

Visit: https://www.rust-lang.org/tools/install

Download rustup-init.exe and run it.

Choose default installation.

Verify:

rustc --version

cargo --version

##### 📦 Install SPL CLI & Create Token

1. Install SPL CLI

cargo install spl-token-cli

2. Create the SPL Token

spl-token create-token

✅ Copy the returned Token Mint Address (e.g., Wxyz1234...)

3. Create Token Account

spl-token create-account <TOKEN_MINT_ADDRESS>

4. Mint Tokens

spl-token mint <TOKEN_MINT_ADDRESS> <AMOUNT>

5. Check Token Balance

spl-token accounts

### 🗂️ Pinata Setup (for NFT Metadata)
#### 🛠 Steps to Create a Free Pinata Account

Visit https://www.pinata.cloud/

Click Sign Up → Choose "Pinata Free" Plan

Fill in Name, Email, Password

Verify email using confirmation link

Log in and navigate to API Keys tab to generate a JWT

Use https://gateway.pinata.cloud/ipfs/<hash> for accessing files

**After setting up solana, its best you clone the microservice before backend and frontend. This microservice allows the seamless admin blockchain interactions and must be run before the backend as a good practice**

### Microservice setup

1. clone this repo as a seperate project

2. cd project-name

**Create a .env file at the root dir and add these**

token_mint_address=<YOUR_TOKEN_MINT_ADDRESS>

devnet_url=https://api.devnet.solana.com

treasury_wallet_path=path where you saved the previously generated keypair

JWT_SECRET=a random hash used for authentication(same for both django and express servers)

4. npm install

5. nodemon index.js

### ⚙️ Backend Setup (Django)

python -m venv venv-name

source venv/bin/activate  

Windows: venv\Scripts\activate

git clone https://github.com/antonyamal-3-6-9/ecoswapchain.git

cd ecoswapchain

**Create .env file near manage.py and include:**

SECRET_KEY=some-random-key

SENDGRID_API_KEY=...

DEBUG=True

DB_NAME=...

DB_USER=...

DB_PASSWORD=...

DB_HOST=...

DB_PORT=...

token_mint_address=<YOUR_TOKEN_MINT_ADDRESS>

treasury_key=<TREASURY_PUBLIC_KEY>

devnet_url=https://api.devnet.solana.com

PINATA_JWT=<YOUR_PINATA_JWT>

JWT_SECRET=a random hash used for authentication(same for both django and express servers)

Then:

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver

### 🌐 Frontend Setup (React + Vite)

1. clone repo

2. cd frontend

3. npm install

4. npm run dev

##🔄 Workflow Overview

###👤 User Onboarding

Register using OTP(by default, otp can be read from server log)

Wallet is generated and encrypted

User stores encryption key securely

Add address in a district with shipping hub

Receive 100 SWAPCOINS

### 🪙 NFT Minting Flow

Create Product → Fill Form

Deduct 20 SWAPCOINS

Sign transaction with password

NFT minted and linked to user

### 🛒 Order & Chat

Buyer explores & orders NFT

Chat for negotiation (WebSocket)

Buyer confirms → Seller confirms

### 📦 Logistics & Shipping

Hubs assigned based on districts

Shipping Methods:

Swap (platform-managed)

Self (user-managed)

### ✅ Product Verification

Swap:

    Hub manager verifies

    Buyer pays (escrow)

    NFT transferred

Self:

    Seller initiates

    Buyer verifies

    Transfer & payment completed

### 🔐 Blockchain Actions

**All on-chain actions require the transaction password.**

### 🔁 Relisting & Rewards

    View NFT ownership history

    List/unlist owned NFTs

    Rewards based on:

        Sustainability score predicted using **Gradient Boosting model trained with 90% accuracy**

        Transfer count

🏆 Rewards = SWAPCOINS

### 🛠 Admin Dashboard

    Add hubs via map UI

    Create routes between hubs

    Manage logistics visually

## 🧱 System Architecture

    Frontend ↔ Backend ↔ Blockchain ↔ ML Model

    Redis/Celery for async tasks

    WebSockets for live chat

    PostgreSQL for data
    
![architecture](https://github.com/user-attachments/assets/63e27a3a-c39e-4cd4-b3cd-d136108b93bc)

![arctec](https://github.com/user-attachments/assets/3c8d1327-10ab-4010-82ba-fe0758cce093)


## 📚 Summary

EcoSwapChain merges blockchain and sustainability, offering:

    Transparent product history via NFTs

    Escrow-protected transactions

    Carbon-conscious incentives

    Real-time negotiation

    Smart logistics and dynamic hub assignments

**Empowering users to buy and sell responsibly, while contributing to a greener planet 🌍**
