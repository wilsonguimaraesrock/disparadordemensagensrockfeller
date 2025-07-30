#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import base64
import json
import time

async def capture_qr_code():
    """Captura o QR code do dashboard do WAHA"""
    async with async_playwright() as p:
        # Lança o navegador
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        try:
            print("Navegando para o dashboard do WAHA...")
            await page.goto('http://localhost:3000/dashboard', wait_until='networkidle')
            
            # Aguarda um pouco para a página carregar completamente
            await page.wait_for_timeout(3000)
            
            # Captura screenshot da página completa primeiro
            await page.screenshot(path='waha_dashboard_current.png', full_page=True)
            print("Screenshot da página completa salvo como 'waha_dashboard_current.png'")
            
            # Procura por botões que possam iniciar uma sessão
            possible_buttons = [
                'button:has-text("Start")',
                'button:has-text("Connect")',
                'button:has-text("New")',
                'button:has-text("Conectar")',
                'button:has-text("Iniciar")',
                '[data-testid="start-session"]',
                '.p-button:has-text("Start")',
                '.btn:has-text("Start")',
                'button[class*="start"]',
                'button[class*="connect"]'
            ]
            
            button_clicked = False
            for selector in possible_buttons:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible():
                        print(f"Encontrado botão: {selector}")
                        await button.click()
                        button_clicked = True
                        print(f"Clicou no botão: {selector}")
                        await page.wait_for_timeout(2000)
                        break
                except Exception as e:
                    continue
            
            if not button_clicked:
                print("Nenhum botão de início encontrado, tentando procurar QR code diretamente...")
            
            # Aguarda um pouco mais após clicar
            await page.wait_for_timeout(5000)
            
            # Lista de seletores para procurar QR code
            qr_selectors = [
                'canvas',
                '[data-testid="qr-code"]',
                '.qr-code',
                '#qr-code',
                'img[alt*="QR"]',
                'img[alt*="qr"]',
                'img[src*="qr"]',
                'img[src*="data:image"]',
                '.p-image',
                '[role="img"]',
                'svg[width][height]',
                '.qr',
                '[class*="qr"]',
                '[id*="qr"]'
            ]
            
            qr_found = False
            for i, selector in enumerate(qr_selectors):
                try:
                    elements = page.locator(selector)
                    count = await elements.count()
                    
                    if count > 0:
                        print(f"Encontrados {count} elementos com seletor: {selector}")
                        
                        for j in range(count):
                            element = elements.nth(j)
                            if await element.is_visible():
                                try:
                                    # Captura screenshot do elemento
                                    screenshot_path = f'qr_element_{i}_{j}.png'
                                    await element.screenshot(path=screenshot_path)
                                    print(f"Screenshot do elemento salvo: {screenshot_path}")
                                    
                                    # Verifica se é um canvas e tenta extrair dados
                                    tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                                    if tag_name == 'canvas':
                                        try:
                                            canvas_data = await element.evaluate('el => el.toDataURL()')
                                            if canvas_data and 'data:image' in canvas_data:
                                                # Salva os dados do canvas
                                                with open(f'canvas_data_{i}_{j}.txt', 'w') as f:
                                                    f.write(canvas_data)
                                                print(f"Dados do canvas salvos: canvas_data_{i}_{j}.txt")
                                                qr_found = True
                                        except Exception as e:
                                            print(f"Erro ao extrair dados do canvas: {e}")
                                    
                                    # Verifica se é uma imagem com src
                                    if tag_name == 'img':
                                        try:
                                            src = await element.get_attribute('src')
                                            if src and ('data:image' in src or 'qr' in src.lower()):
                                                with open(f'img_src_{i}_{j}.txt', 'w') as f:
                                                    f.write(src)
                                                print(f"Src da imagem salvo: img_src_{i}_{j}.txt")
                                                qr_found = True
                                        except Exception as e:
                                            print(f"Erro ao extrair src da imagem: {e}")
                                    
                                except Exception as e:
                                    print(f"Erro ao capturar screenshot do elemento {j}: {e}")
                except Exception as e:
                    print(f"Erro ao procurar elementos com seletor {selector}: {e}")
            
            if not qr_found:
                print("QR code não encontrado, capturando screenshot da área central...")
                # Captura uma área central da tela onde o QR code provavelmente estaria
                await page.screenshot(
                    path='qr_area_center.png',
                    clip={'x': 400, 'y': 200, 'width': 400, 'height': 400}
                )
                print("Screenshot da área central salvo como 'qr_area_center.png'")
            
            # Salva o HTML atual da página
            html_content = await page.content()
            with open('current_page_content.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("Conteúdo HTML salvo como 'current_page_content.html'")
            
            # Aguarda um pouco mais para ver se algo muda
            print("Aguardando mais 10 segundos para observar mudanças...")
            await page.wait_for_timeout(10000)
            
            # Captura screenshot final
            await page.screenshot(path='waha_dashboard_final.png', full_page=True)
            print("Screenshot final salvo como 'waha_dashboard_final.png'")
            
        except Exception as e:
            print(f"Erro durante a captura: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_qr_code())