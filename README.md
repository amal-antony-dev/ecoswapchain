# EcoSwapChain

A blockchain-backed **recommerce platform**: every second-hand item is minted as a **Solana NFT**, every sale goes through **escrow**, and keeping products in use earns **SwapCoin** rewards scored by a **sustainability model**.

Resale platforms struggle with authenticity, traceability and disputes. EcoSwapChain gives each item an on-chain identity and ownership history, holds the buyer's payment until the item is verified and delivered, and rewards people for keeping products in circulation.

> **Status:** my final-year college project (2025), built to learn how a whole product fits together: blockchain, payments, logistics, ML and a real-time UI. It runs on Solana **devnet**. See [Looking back](#looking-back) for what I'd change.
>
> Case study: [amal-antony-dev.vercel.app](https://amal-antony-dev.vercel.app/#work/ecoswapchain/overview)

## The four repositories

| Repo | Role |
|---|---|
| **ecoswapchain** | This repo: Django REST API, Celery workers, Django Channels websockets |
| [ESC-Frontend](https://github.com/amal-antony-dev/ESC-Frontend) | React + TypeScript web app; creates and encrypts wallets, mints and transfers NFTs |
| [ESC-BlockChain](https://github.com/amal-antony-dev/ESC-BlockChain) | Express service that holds the treasury wallet and pays out SwapCoin |
| [Sustainability-Prediction](https://github.com/amal-antony-dev/Sustainability-Prediction) | Dataset, training and the gradient-boosting scoring model |

## Features

- **Items as NFTs.** Listing a product mints it as a Solana NFT, paid for with 20 SwapCoin. Each sale transfers the NFT and records the transaction, so ownership history is traceable.
- **Escrow orders.** An order moves through eight states (pending → confirmed → processing → packed → shipped → completed → delivered, or cancelled), tracked alongside payment status (unpaid, escrow, paid, refunded) and ownership-transfer status. On delivery the escrowed SwapCoin goes to the seller and the NFT to the buyer.
- **Hub logistics.** Addresses are geocoded from their postal code and mapped to numbered districts. Each order gets the nearest hubs in the seller's and buyer's districts (or neighbouring ones), and hub shipping is used only when it beats the direct distance. Admins build the hub network on a map; Kruskal's algorithm forms a minimum spanning tree and Dijkstra finds the cheapest route.
- **Two shipping modes.** *Swap*: a hub manager verifies the item before escrow is released. *Self*: the seller ships and the buyer verifies on receipt.
- **Sustainability rewards.** A gradient-boosting model scores each item from its category, materials, condition and sustainability attributes. The score, the price and the number of previous owners set a SwapCoin reward, half of which goes to the seller when the item resells.
- **Live updates and chat.** Websockets push order events (shipping chosen, hubs assigned, escrow started, ownership transferred) to both sides, alongside a chat for negotiating price.
- **Client-side wallet security.** Private keys are encrypted in the browser with AES-GCM using a password-derived key (PBKDF2), so every on-chain action needs the user's password.

## Architecture

```
React app (ESC-Frontend) ──REST + WebSocket──► Django API (this repo) ──► PostgreSQL
        │  signs with the user's wallet              │
        ▼                                            ├──► Celery workers (via Redis): geocoding, hub
     Solana devnet ◄── SwapCoin rewards ── ESC-BlockChain    assignment, sustainability scoring,
                                            (treasury)       NFT transfer, reward payout
                                                     └──► Django Channels (Redis): order events, chat
```

Django signals queue the slow work on Celery so requests return quickly.

![architecture](https://github.com/user-attachments/assets/63e27a3a-c39e-4cd4-b3cd-d136108b93bc)

![system design](https://github.com/user-attachments/assets/3c8d1327-10ab-4010-82ba-fe0758cce093)

### Django apps

| App | Responsibility |
|---|---|
| `esc_user`, `esc_trader` | Accounts, OTP registration, trader profiles and addresses |
| `esc_wallet`, `esc_tokens`, `esc_transaction` | SwapCoin balances, escrow, token and NFT transaction records |
| `esc_product`, `esc_nft` | Products, NFT minting, sustainability scoring and rewards |
| `esc_order` | Orders, state machine, hub finder, geocoding, order chat |
| `esc_hub` | Hubs, routes, MST and shortest-path routing |
| `esc_verification` | Hub-manager and buyer verification |
| `esc_admin` | Admin dashboard API |

## User flow

1. **Onboard.** Register with an email OTP (in development the OTP is printed in the server log). A wallet is generated and encrypted in the browser, the user stores the key, adds an address in a district with a hub, and receives 100 SwapCoin.
2. **List.** Fill in the product form, pay 20 SwapCoin, sign with the password, and the NFT is minted.
3. **Buy.** The buyer orders, both sides negotiate in chat, then buyer and seller confirm.
4. **Ship and verify.** Hubs are assigned by district. With *swap* shipping, the hub manager verifies the item, the buyer's payment moves to escrow and the NFT is transferred; with *self* shipping, the buyer verifies on receipt.
5. **Relist and earn.** Owners can view an item's history, relist or unlist it, and earn rewards based on its sustainability score and transfer count.

## Run it locally

You need Python 3.10+, Node 18+, PostgreSQL, Redis, the Solana CLI and a free [Pinata](https://www.pinata.cloud/) account for NFT metadata.

> **Note:** `ecoswapchain/settings.py` is not committed because it held secrets. Create it with the usual Django settings, reading the variables below from `.env` (the project uses `python-decouple`), plus DRF + SimpleJWT, CORS, Channels with `channels_redis`, and `CELERY_BROKER_URL` pointing at Redis.

### 1. Solana devnet

```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
solana config set --url https://api.devnet.solana.com
solana-keygen new --outfile ~/treasury.json     # the treasury wallet
solana config set --keypair ~/treasury.json
solana airdrop 2

cargo install spl-token-cli                     # needs Rust: https://rustup.rs
spl-token create-token                          # copy the mint address → SwapCoin
spl-token create-account <MINT_ADDRESS>
spl-token mint <MINT_ADDRESS> 1000000
```

### 2. Treasury service

Clone [ESC-BlockChain](https://github.com/amal-antony-dev/ESC-BlockChain) and follow its README. It runs on `http://localhost:3000` and must be up before the backend.

### 3. Backend (this repo)

```bash
git clone https://github.com/amal-antony-dev/ecoswapchain.git
cd ecoswapchain
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` next to `manage.py`:

```ini
SECRET_KEY=change-me
DEBUG=True
DB_NAME=ecoswapchain
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
SENDGRID_API_KEY=            # optional: OTP email; otherwise read OTPs from the log
token_mint_address=<MINT_ADDRESS>
treasury_key=<TREASURY_PUBLIC_KEY>
devnet_url=https://api.devnet.solana.com
PINATA_JWT=<PINATA_JWT>
JWT_SECRET=<same value as ESC-BlockChain>
```

Then run each in its own terminal:

```bash
python manage.py migrate
python manage.py runserver                    # API + websockets (Daphne/Channels)
celery -A ecoswapchain worker -l info         # background tasks
```

### 4. Frontend

Clone [ESC-Frontend](https://github.com/amal-antony-dev/ESC-Frontend), set `BASE_URL` in `src/Components/API/api.tsx` to `http://localhost:8000/`, then:

```bash
cd EcoSwapChain && npm install && npm run dev
```

## Tech

**Backend:** Django 5 · Django REST Framework · SimpleJWT · Django Channels + Daphne · Celery · Redis · PostgreSQL · geopy
**Frontend:** React · TypeScript · Vite · Material UI · Redux Toolkit · Leaflet
**Blockchain:** Solana · SPL Token · Metaplex Token Metadata · Pinata (IPFS)
**ML:** scikit-learn (gradient boosting)

## Looking back

This was built before I'd worked on production systems. With what I know now, I'd:

- make escrow release and NFT transfer **one idempotent, retried workflow** instead of separate tasks that can leave an order half-finished;
- move business logic out of views into a service layer;
- replace hardcoded paths and service URLs with configuration, and commit a `settings.py` that reads everything from the environment;
- cache geocoding results;
- add tests, starting with the order state machine and hub assignment.

The sustainability model is trained on synthetic data scored by a formula, so its scores show how the reward mechanism works, not real environmental impact. Details are in [Sustainability-Prediction](https://github.com/amal-antony-dev/Sustainability-Prediction#limitations).
