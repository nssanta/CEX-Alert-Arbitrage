# CEX Flash Arbitrage Bot

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance asynchronous arbitrage bot designed for centralized exchanges (CEX). It monitors price discrepancies across multiple exchanges in real-time and notifies opportunities via Telegram.

[Русская версия](README_RU.md) | [English](README.md)

![Interface](Screen.png)

---

## 🚀 Features

*   **Multi-Exchange Support:** Integrated with Bybit, OKX, Gate.io, KuCoin, Mexc, CoinW.
*   **Asynchronous Architecture:** Built on `asyncio` for low-latency data fetching and processing.
*   **Real-time Alerts:** Instant notifications via Telegram Bot API.
*   **Flexible Configuration:** Adjustable spread thresholds, volume filters, and timer settings via UI.
*   **Experimental Strategy:** Includes a module for triangular arbitrage logic (currently in experimental phase).

---

## 🔔 Notifications

The bot sends real-time alerts to Telegram with the following structure:

*   **Exchange Pair:** Shows the direction of the trade (e.g., `Binance ➤ Bybit`).
*   **Coin:** The asset being arbitraged (e.g., `BTCUSDT`).
*   **Price & Volume:** Detailed price and 24h volume for both exchanges to assess liquidity.
*   **Spread:** Calculated profit margin in percentage.

---

## ⚡ Performance Note

> **Disclaimer:** This is a **proof-of-concept (PoC)** version designed to demonstrate the architectural logic of CEX arbitrage.
> 
> While the current asynchronous engine is functional, it is optimized for code readability and educational purposes. For a production-grade High-Frequency Trading (HFT) environment, the core engine could be accelerated by **10x** or more by:
> *   Refactoring critical paths using Rust or Cython.
> *   Implementing direct WebSocket streams instead of REST API polling.
> *   Using a lower-level networking library.

---

## 🛠 Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/cex-flash-arbitrage.git
    cd cex-flash-arbitrage
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration:**
    Copy the example environment file and configure your API keys:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and fill in your Exchange API keys and Telegram Bot Token.

---

## 🧩 Project Structure

*   `Core/`: Main data handling and processing logic.
*   `exchange/`: API wrappers for individual exchanges (Bybit, OKX, etc.).
*   `TelBot/`: Telegram bot interface and handler logic.
*   `strategies/`: Arbitrage strategies, including the experimental triangular logic.

---

## ⚠️ Experimental: Triangular Arbitrage

The file `strategies/triangular_logic.py` contains the mathematical core for triangular arbitrage loops. 
> **Note:** This strategy is currently experimental. High-frequency triangular arbitrage on CEXs is subject to strict rate limits and execution latency, which may affect profitability in live environments.

---


## 📝 License

MIT License. See [LICENSE](LICENSE) for more information.
