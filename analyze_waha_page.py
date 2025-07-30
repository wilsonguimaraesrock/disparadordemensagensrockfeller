#!/usr/bin/env python3
"""
Script para analisar a página do WAHA e identificar onde está o QR code
"""

import asyncio
from playwright.async_api import async_playwright
import base64
import json

async def analyze_waha_page():
    """Analisa a página do WAHA para encontrar o QR code"""
    
    async with async_playwright() as p:
        # Usar Chromium em modo não-headless para ver o que está acontecendo
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        
        try:
            print("🌐 Navegando para o dashboard WAHA...")
            await page.goto('http://localhost:3000/dashboard/', wait_until='networkidle')
            
            print("⏳ Aguardando carregamento da página...")
            await page.wait_for_timeout(5000)
            
            # Aguardar que o loading desapareça
            try:
                await page.wait_for_selector('#loading-body', state='hidden', timeout=10000)
                print("✅ Loading desapareceu")
            except:
                print("⚠️ Loading não encontrado ou não desapareceu")
            
            # Aguardar mais um pouco
            await page.wait_for_timeout(3000)
            
            # Capturar screenshot da página completa
            print("📸 Capturando screenshot da página completa...")
            full_screenshot = await page.screenshot(full_page=True)
            with open('waha_full_page.png', 'wb') as f:
                f.write(full_screenshot)
            print("💾 Screenshot salvo como 'waha_full_page.png'")
            
            # Obter HTML da página
            print("📄 Obtendo HTML da página...")
            page_content = await page.content()
            with open('waha_page_content.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            print("💾 HTML salvo como 'waha_page_content.html'")
            
            # Procurar por elementos que podem conter QR code
            print("🔍 Procurando por elementos QR code...")
            
            qr_selectors = [
                'canvas',
                '[data-testid="qr-code"]',
                '.qr-code',
                '#qr-code',
                'img[alt*="QR"]',
                'img[src*="qr"]',
                'svg',
                '.p-image',
                '[role="img"]',
                '.qr',
                '[class*="qr"]',
                '[id*="qr"]'
            ]
            
            found_elements = []
            
            for selector in qr_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"✅ Encontrado {len(elements)} elemento(s) com seletor: {selector}")
                        for i, element in enumerate(elements):
                            # Obter informações do elemento
                            tag_name = await element.evaluate('el => el.tagName')
                            class_name = await element.evaluate('el => el.className')
                            element_id = await element.evaluate('el => el.id')
                            
                            element_info = {
                                'selector': selector,
                                'index': i,
                                'tag': tag_name,
                                'class': class_name,
                                'id': element_id
                            }
                            
                            found_elements.append(element_info)
                            
                            # Capturar screenshot do elemento
                            try:
                                element_screenshot = await element.screenshot()
                                # Limpar o seletor para nome de arquivo
                                clean_selector = selector.replace('[', '').replace(']', '').replace('"', '').replace('*', '').replace('=', '_').replace('.', '').replace('#', '')
                                filename = f"element_{clean_selector}_{i}.png"
                                with open(filename, 'wb') as f:
                                    f.write(element_screenshot)
                                print(f"📸 Screenshot do elemento salvo como '{filename}'")
                            except Exception as e:
                                print(f"❌ Erro ao capturar screenshot do elemento: {e}")
                                
                except Exception as e:
                    print(f"❌ Erro com seletor {selector}: {e}")
            
            # Salvar informações dos elementos encontrados
            with open('found_elements.json', 'w', encoding='utf-8') as f:
                json.dump(found_elements, f, indent=2, ensure_ascii=False)
            print("💾 Informações dos elementos salvas em 'found_elements.json'")
            
            # Aguardar um pouco para visualização
            print("👀 Aguardando 10 segundos para visualização...")
            await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            await browser.close()
            print("🔚 Navegador fechado")

if __name__ == '__main__':
    asyncio.run(analyze_waha_page())