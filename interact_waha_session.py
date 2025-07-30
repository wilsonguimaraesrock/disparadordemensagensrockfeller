import asyncio
from playwright.async_api import async_playwright
import json
import time

async def interact_with_waha_session():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("Navegando para o dashboard do WAHA...")
            await page.goto('http://localhost:3000/dashboard')
            await page.wait_for_load_state('networkidle')
            
            # Screenshot inicial
            await page.screenshot(path='session_step1_dashboard.png')
            print("Screenshot do dashboard salvo")
            
            # Procurar pela linha da sessão WAHA
            waha_row = page.locator('tr:has-text("WAHA")')
            if await waha_row.count() > 0:
                print("Sessão WAHA encontrada")
                
                # Procurar por botões de ação na linha
                action_buttons = waha_row.locator('button, a, [role="button"]')
                button_count = await action_buttons.count()
                print(f"Encontrados {button_count} botões de ação")
                
                # Tentar clicar em cada botão para ver se abre o QR
                for i in range(button_count):
                    button = action_buttons.nth(i)
                    button_text = await button.text_content() or ""
                    button_title = await button.get_attribute('title') or ""
                    print(f"Botão {i}: '{button_text}' (title: '{button_title}')")
                    
                    # Clicar no botão
                    await button.click()
                    await page.wait_for_timeout(3000)
                    
                    # Screenshot após clicar
                    await page.screenshot(path=f'session_step2_after_button_{i}.png')
                    
                    # Procurar por QR code após clicar
                    qr_selectors = [
                        'canvas',
                        'img[src*="qr"]',
                        'img[alt*="qr"]',
                        'img[alt*="QR"]',
                        '[class*="qr"]',
                        '[id*="qr"]',
                        'svg',
                        '.p-dialog canvas',
                        '.p-dialog img',
                        '.p-dialog svg',
                        '[role="dialog"] canvas',
                        '[role="dialog"] img',
                        '.modal canvas',
                        '.modal img'
                    ]
                    
                    qr_found = False
                    for selector in qr_selectors:
                        elements = page.locator(selector)
                        count = await elements.count()
                        if count > 0:
                            print(f"Encontrados {count} elementos com seletor: {selector}")
                            for j in range(count):
                                element = elements.nth(j)
                                try:
                                    clean_selector = selector.replace("[", "").replace("]", "").replace('"', "").replace("*", "").replace("=", "")
                                    await element.screenshot(path=f'qr_candidate_{i}_{j}_{clean_selector}.png')
                                    qr_found = True
                                    print(f"Screenshot do elemento QR candidato salvo: qr_candidate_{i}_{j}")
                                except Exception as e:
                                    print(f"Erro ao capturar elemento: {e}")
                    
                    # Verificar se apareceu um modal ou dialog
                    modals = page.locator('.p-dialog, [role="dialog"], .modal')
                    modal_count = await modals.count()
                    if modal_count > 0:
                        print(f"Encontrados {modal_count} modais/dialogs")
                        for j in range(modal_count):
                            modal = modals.nth(j)
                            await modal.screenshot(path=f'modal_{i}_{j}.png')
                            print(f"Screenshot do modal salvo: modal_{i}_{j}.png")
                    
                    if qr_found:
                        print("✅ QR code encontrado!")
                        break
                    
                    # Aguardar um pouco antes do próximo botão
                    await page.wait_for_timeout(2000)
            
            else:
                print("❌ Sessão WAHA não encontrada")
            
            # Screenshot final
            await page.screenshot(path='session_final.png')
            print("Screenshot final salvo")
            
            # Salvar HTML final
            html_content = await page.content()
            with open('session_final_content.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("HTML final salvo")
            
            print("Mantendo navegador aberto por 30 segundos para observação...")
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(interact_with_waha_session())