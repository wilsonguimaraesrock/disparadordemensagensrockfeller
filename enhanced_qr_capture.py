#!/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright
import base64
import json
import time

async def enhanced_qr_capture():
    """Captura melhorada do QR code do WAHA com foco em modais e diálogos"""
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
            
            # Captura screenshot inicial
            await page.screenshot(path='step1_initial.png', full_page=True)
            print("Screenshot inicial salvo")
            
            # Procura e clica no botão "Start New"
            start_button_found = False
            start_selectors = [
                'button:has-text("Start New")',
                'button:has-text("Start")',
                'button:has-text("New")',
                '.p-button:has-text("Start")',
                '[data-testid="start-session"]',
                'button[class*="start"]'
            ]
            
            for selector in start_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible():
                        print(f"Clicando no botão: {selector}")
                        await button.click()
                        start_button_found = True
                        await page.wait_for_timeout(2000)
                        break
                except Exception as e:
                    continue
            
            if start_button_found:
                await page.screenshot(path='step2_after_start.png', full_page=True)
                print("Screenshot após clicar em Start salvo")
            
            # Aguarda um pouco mais para ver se aparece alguma modal
            await page.wait_for_timeout(5000)
            
            # Procura por modais, diálogos ou overlays
            modal_selectors = [
                '.p-dialog',
                '.modal',
                '.p-overlay',
                '[role="dialog"]',
                '.p-component-overlay',
                '.p-dialog-content',
                '.overlay',
                '.popup'
            ]
            
            modal_found = False
            for selector in modal_selectors:
                try:
                    modals = page.locator(selector)
                    count = await modals.count()
                    if count > 0:
                        print(f"Encontradas {count} modais com seletor: {selector}")
                        for i in range(count):
                            modal = modals.nth(i)
                            if await modal.is_visible():
                                await modal.screenshot(path=f'modal_{selector.replace(".", "").replace("[", "").replace("]", "")}_{i}.png')
                                print(f"Screenshot da modal salvo")
                                modal_found = True
                except Exception as e:
                    continue
            
            # Procura especificamente por QR codes em toda a página
            qr_selectors = [
                'canvas',
                '[data-testid*="qr"]',
                '[class*="qr"]',
                '[id*="qr"]',
                'img[alt*="QR"]',
                'img[alt*="qr"]',
                'img[src*="qr"]',
                'img[src*="data:image"]',
                '.p-image',
                'svg[viewBox]',
                'div[class*="qr"]'
            ]
            
            qr_found = False
            for selector in qr_selectors:
                try:
                    elements = page.locator(selector)
                    count = await elements.count()
                    
                    if count > 0:
                        print(f"Encontrados {count} elementos QR potenciais com: {selector}")
                        
                        for i in range(count):
                            element = elements.nth(i)
                            if await element.is_visible():
                                try:
                                    # Verifica o tamanho do elemento
                                    box = await element.bounding_box()
                                    if box and box['width'] > 50 and box['height'] > 50:
                                        screenshot_path = f'potential_qr_{selector.replace(".", "").replace("[", "").replace("]", "")}_{i}.png'
                                        await element.screenshot(path=screenshot_path)
                                        print(f"QR potencial salvo: {screenshot_path} (tamanho: {box['width']}x{box['height']})")
                                        
                                        # Se for canvas, tenta extrair dados
                                        tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                                        if tag_name == 'canvas':
                                            try:
                                                canvas_data = await element.evaluate('el => el.toDataURL()')
                                                if canvas_data and 'data:image' in canvas_data:
                                                    with open(f'qr_canvas_data_{i}.txt', 'w') as f:
                                                        f.write(canvas_data)
                                                    print(f"Dados do canvas QR salvos: qr_canvas_data_{i}.txt")
                                                    qr_found = True
                                            except Exception as e:
                                                print(f"Erro ao extrair canvas: {e}")
                                        
                                        # Se for imagem, verifica src
                                        if tag_name == 'img':
                                            try:
                                                src = await element.get_attribute('src')
                                                if src:
                                                    with open(f'qr_img_src_{i}.txt', 'w') as f:
                                                        f.write(src)
                                                    print(f"Src da imagem QR salvo: qr_img_src_{i}.txt")
                                                    if 'data:image' in src:
                                                        qr_found = True
                                            except Exception as e:
                                                print(f"Erro ao extrair src: {e}")
                                
                                except Exception as e:
                                    print(f"Erro ao processar elemento {i}: {e}")
                except Exception as e:
                    print(f"Erro ao procurar {selector}: {e}")
            
            # Aguarda mais tempo para ver se o QR code aparece
            print("Aguardando 15 segundos para o QR code aparecer...")
            await page.wait_for_timeout(15000)
            
            # Screenshot final
            await page.screenshot(path='step3_final.png', full_page=True)
            print("Screenshot final salvo")
            
            # Salva o HTML final
            html_content = await page.content()
            with open('final_page_content.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            print("HTML final salvo")
            
            # Tenta procurar por elementos que possam ter aparecido dinamicamente
            print("Procurando por novos elementos...")
            all_images = page.locator('img')
            img_count = await all_images.count()
            print(f"Total de imagens na página: {img_count}")
            
            all_canvas = page.locator('canvas')
            canvas_count = await all_canvas.count()
            print(f"Total de canvas na página: {canvas_count}")
            
            # Se encontrou canvas, tenta capturar todos
            if canvas_count > 0:
                for i in range(canvas_count):
                    try:
                        canvas = all_canvas.nth(i)
                        if await canvas.is_visible():
                            await canvas.screenshot(path=f'final_canvas_{i}.png')
                            print(f"Canvas {i} capturado")
                    except Exception as e:
                        print(f"Erro ao capturar canvas {i}: {e}")
            
            if not qr_found:
                print("QR code ainda não encontrado. Pode ser necessário aguardar mais tempo ou o QR pode estar em uma área específica.")
            
        except Exception as e:
            print(f"Erro durante a captura: {e}")
        
        finally:
            # Mantém o navegador aberto por mais tempo para observação manual
            print("Mantendo navegador aberto por 30 segundos para observação manual...")
            await page.wait_for_timeout(30000)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(enhanced_qr_capture())