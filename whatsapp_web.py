import asyncio
import base64
import logging
from playwright.async_api import async_playwright

# Configuração do logger
logger = logging.getLogger(__name__)

class WhatsAppWebManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        self.connection_status = "disconnected"
        self.lock = asyncio.Lock()

    async def ensure_browser_is_running(self):
        async with self.lock:
            if not self.browser or not self.browser.is_connected():
                logger.info("Browser not running. Starting new session...")
                await self.start_session()

    async def start_session(self):
        logger.info("Attempting to start Playwright session...")
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            self.connection_status = "pending_qr"
            logger.info("Playwright session started successfully.")
            return True
        except Exception as e:
            self.connection_status = "error"
            logger.error(f"Error starting Playwright session: {e}", exc_info=True)
            await self.close_session() # Garante que tudo seja limpo em caso de falha
            return False

    async def get_qr_code(self):
        logger.info("Attempting to get QR code...")
        await self.ensure_browser_is_running()
        if not self.page:
            logger.warning("get_qr_code called but page is not initialized.")
            return None, "Session not started."

        try:
            logger.info("Navigating to WhatsApp Web...")
            await self.page.goto("https://web.whatsapp.com", timeout=60000)
            logger.info("Page loaded. Waiting for QR code selector...")
            # Tentar múltiplos seletores para o QR Code
            qr_selectors = [
                'canvas',
                'div[data-ref] canvas',
                '[data-testid="qr-code"]',
                'div._2EZ_m canvas',
                'div[data-testid="qr-code-container"] canvas'
            ]
            
            qr_element = None
            for selector in qr_selectors:
                try:
                    logger.info(f"Trying selector: {selector}")
                    await self.page.wait_for_selector(selector, timeout=30000)  # Aumentado para 30s
                    qr_element = await self.page.query_selector(selector)
                    if qr_element:
                        logger.info(f"QR code found with selector: {selector}")
                        break
                except Exception as e:
                    logger.warning(f"Selector {selector} failed: {e}")
                    continue
            
            if not qr_element:
                logger.error("QR code element not found with any selector.")
                await self.page.screenshot(path='debug_screenshot.png', full_page=True)
                logger.info("Debug screenshot saved as debug_screenshot.png")
                return None, "Could not find QR code element."

            logger.info("Taking screenshot of QR code...")
            screenshot_bytes = await qr_element.screenshot()
            qr_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            self.connection_status = "waiting_scan"
            logger.info("QR code generated successfully.")
            return qr_base64, None
        except Exception as e:
            self.connection_status = "error"
            logger.error(f"Error getting QR code: {e}", exc_info=True)
            return None, f"Error getting QR code: {e}"

    def get_connection_status(self):
        # This method should be lightweight and not perform async operations.
        # It just returns the current state.
        return {'status': self.connection_status}

    async def check_connection_status_periodically(self):
        if self.page and self.connection_status == "waiting_scan":
            logger.info("Checking connection status...")
            try:
                # Wait for the QR code canvas to disappear.
                logger.info("Waiting for QR code canvas to disappear...")
                await self.page.wait_for_selector('canvas', state='hidden', timeout=10000)
                logger.info("QR code canvas is hidden. Checking for main chat interface...")

                # Check if the main chat interface is loaded by looking for a stable element.
                # Using the search input container as it's usually reliable.
                await self.page.wait_for_selector('div[data-testid="search-input-container"]', timeout=15000)
                self.connection_status = "connected"
                logger.info("Connection status is now 'connected'.")
            except Exception as e:
                logger.warning(f"Failed to confirm connection: {e}")
                # If it fails, we check if we are still on the main page or if there was a redirect/error.
                if "https://web.whatsapp.com/" in self.page.url:
                    # Still on the main page, maybe the QR code just timed out and will refresh.
                    self.connection_status = "pending_qr" # Reset to allow getting a new QR
                    logger.info("QR code likely timed out. Resetting status to 'pending_qr'.")
                else:
                    self.connection_status = "timeout"
                    logger.warning("Page URL changed or timed out. Status set to 'timeout'.")
        return self.get_connection_status()

    async def close_session(self):
        async with self.lock:
            if self.browser and self.browser.is_connected():
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop() # Encerra o processo do Playwright
            self.browser = None
            self.page = None
            self.context = None
            self.playwright = None
            self.connection_status = "disconnected"
            logger.info("Playwright session closed.")

# Singleton instance
whatsapp_manager = WhatsAppWebManager()