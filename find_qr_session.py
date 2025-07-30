#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import json
import time

async def find_qr_in_session():
    """Procura especificamente por QR code em sessões do WAHA"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        try:
            print("Navegando para o dashboard do WAHA...")
            await page.goto('http://localhost:3000/dashboard', wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # Captura screenshot inicial
            await page.screenshot(path='session_step1_dashboard.png', full_page=True)
            print("Screenshot do dashboard salvo")
            
            # Procura por botões relacionados a sessões
            session_buttons = [
                'button:has-text("Start New")',
                'button:has-text("New Session")',
                'button:has-text("Create Session")',
                'button:has-text("Add Session")',
                'button:has-text("Connect")',
                '.p-button:has-text("Start")',
                '[data-testid*="session"]',
                '[data-testid*="start"]'
            ]
            
            session_started = False
            for selector in session_buttons:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible():
                        print(f"Clicando em: {selector}")
                        await button.click()
                        session_started = True
                        await page.wait_for_timeout(3000)
                        break
                except Exception as e:
                    continue
            
            if session_started:
                await page.screenshot(path='session_step2_after_start.png', full_page=True)
                print("Screenshot após iniciar sessão salvo")
            
            # Aguarda um pouco para ver se aparece alguma modal ou diálogo
            await page.wait_for_timeout(5000)
            
            # Procura por modais ou diálogos que podem conter o QR
            modal_selectors = [
                '.p-dialog-content',
                '.p-dialog',
                '.modal-content',
                '.modal',
                '[role="dialog"]',
                '.p-overlay-modal',
                '.p-component-overlay'
            ]
            
            for selector in modal_selectors:
                try:
                    modals = page.locator(selector)
                    count = await modals.count()
                    if count > 0:
                        print(f"Encontradas {count} modais com: {selector}")
                        for i in range(count):
                            modal = modals.nth(i)
                            if await modal.is_visible():
                                await modal.screenshot(path=f'session_modal_{i}.png')
                                print(f"Modal {i} capturada")
                except Exception as e:
                    continue
            
            # Procura especificamente por elementos de QR code
            qr_selectors = [
                'canvas',
                'img[alt*="QR"]',
                'img[alt*="qr"]',
                'img[src*="qr"]',
                'img[src*="data:image"]',
                '[data-testid*="qr"]',
                '[class*="qr"]',
                '[id*="qr"]',
                'svg[width="256"]',  # QR codes são frequentemente 256x256
                'svg[width="200"]',
                'div[class*="qr-code"]',
                '.qr-container',
                '.qr-display'
            ]
            
            qr_elements_found = []
            
            for selector in qr_selectors:
                try:
                    elements = page.locator(selector)
                    count = await elements.count()
                    
                    if count > 0:
                        print(f"Encontrados {count} elementos QR com: {selector}")
                        
                        for i in range(count):
                            element = elements.nth(i)
                            if await element.is_visible():
                                try:
                                    box = await element.bounding_box()
                                    if box and box['width'] > 100 and box['height'] > 100:  # QR codes são geralmente grandes
                                        screenshot_path = f'qr_found_{selector.replace(".", "").replace("[", "").replace("]", "")}_{i}.png'
                                        await element.screenshot(path=screenshot_path)
                                        
                                        element_info = {
                                            'selector': selector,
                                            'index': i,
                                            'screenshot': screenshot_path,
                                            'size': f"{box['width']}x{box['height']}",
                                            'position': f"{box['x']},{box['y']}"
                                        }
                                        
                                        # Verifica o tipo de elemento
                                        tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                                        element_info['tag'] = tag_name
                                        
                                        if tag_name == 'canvas':
                                            try:
                                                canvas_data = await element.evaluate('el => el.toDataURL()')
                                                if canvas_data and 'data:image' in canvas_data:
                                                    data_file = f'qr_canvas_data_{i}.txt'
                                                    with open(data_file, 'w') as f:
                                                        f.write(canvas_data)
                                                    element_info['canvas_data'] = data_file
                                                    print(f"QR Canvas encontrado! Dados salvos em: {data_file}")
                                            except Exception as e:
                                                print(f"Erro ao extrair canvas: {e}")
                                        
                                        elif tag_name == 'img':
                                            try:
                                                src = await element.get_attribute('src')
                                                if src:
                                                    element_info['src'] = src
                                                    if 'data:image' in src:
                                                        print(f"QR Image encontrada! Src: {src[:100]}...")
                                            except Exception as e:
                                                print(f"Erro ao extrair src: {e}")
                                        
                                        qr_elements_found.append(element_info)
                                        print(f"QR potencial salvo: {screenshot_path} ({element_info['size']})")
                                
                                except Exception as e:
                                    print(f"Erro ao processar elemento {i}: {e}")
                except Exception as e:
                    print(f"Erro ao procurar {selector}: {e}")
            
            # Salva informações dos elementos encontrados
            with open('qr_elements_session.json', 'w') as f:
                json.dump(qr_elements_found, f, indent=2)
            print(f"Informações salvas em qr_elements_session.json")
            
            # Aguarda mais tempo para observar
            print("Aguardando 20 segundos para observação...")
            await page.wait_for_timeout(20000)
            
            # Screenshot final
            await page.screenshot(path='session_step3_final.png', full_page=True)
            print("Screenshot final salvo")
            
            # Verifica se há elementos de sessão ativos
            session_info = []
            session_selectors = [
                '.session-item',
                '.session-card',
                '[data-testid*="session"]',
                '.p-datatable-tbody tr',
                'table tbody tr'
            ]
            
            for selector in session_selectors:
                try:
                    elements = page.locator(selector)
                    count = await elements.count()
                    if count > 0:
                        print(f"Encontradas {count} sessões com: {selector}")
                        for i in range(count):
                            element = elements.nth(i)
                            if await element.is_visible():
                                text = await element.inner_text()
                                session_info.append({
                                    'selector': selector,
                                    'index': i,
                                    'text': text[:200]  # Primeiros 200 caracteres
                                })
                except Exception as e:
                    continue
            
            with open('session_info.json', 'w') as f:
                json.dump(session_info, f, indent=2)
            print(f"Informações de sessão salvas em session_info.json")
            
            if qr_elements_found:
                print(f"\n✅ Encontrados {len(qr_elements_found)} elementos QR potenciais!")
                for elem in qr_elements_found:
                    print(f"  - {elem['tag']} ({elem['size']}) -> {elem['screenshot']}")
            else:
                print("\n❌ Nenhum QR code encontrado. Pode ser necessário:")
                print("  1. Aguardar mais tempo")
                print("  2. Interagir com elementos específicos")
                print("  3. Verificar se o WAHA está configurado corretamente")
            
        except Exception as e:
            print(f"Erro durante a busca: {e}")
        
        finally:
            print("Mantendo navegador aberto por 30 segundos para observação...")
            await page.wait_for_timeout(30000)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(find_qr_in_session())