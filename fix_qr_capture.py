#!/usr/bin/env python3
"""
Script para corrigir a captura do QR code do WAHA
Este script navega especificamente para a página de sessões e captura o QR code corretamente
"""

import asyncio
import base64
from playwright.async_api import async_playwright
import json

async def capture_waha_qr_code():
    """Captura o QR code do WAHA navegando para a página correta"""
    
    async with async_playwright() as p:
        # Usar Chromium em modo não-headless para debug
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        try:
            print("🌐 Navegando para o dashboard WAHA...")
            await page.goto('http://localhost:3000/dashboard/', wait_until='networkidle')
            
            # Aguardar a página carregar completamente
            print("⏳ Aguardando página carregar...")
            await page.wait_for_timeout(5000)
            
            # Tentar aguardar que o loading desapareça
            try:
                await page.wait_for_selector('#loading-body', state='hidden', timeout=10000)
                print("✅ Loading desapareceu")
            except:
                print("⚠️ Loading não encontrado ou não desapareceu")
            
            # Aguardar mais um pouco
            await page.wait_for_timeout(3000)
            
            # Capturar screenshot da página completa para análise
            print("📸 Capturando screenshot da página completa...")
            full_screenshot = await page.screenshot(full_page=True)
            with open('waha_dashboard_full.png', 'wb') as f:
                f.write(full_screenshot)
            print("💾 Screenshot salvo como 'waha_dashboard_full.png'")
            
            # Procurar por elementos que podem ser o QR code ou botões relacionados
            print("🔍 Procurando por elementos na página...")
            
            # Primeiro, vamos procurar por botões ou links que possam levar ao QR code
            possible_buttons = [
                'button:has-text("Connect")',
                'button:has-text("Start")', 
                'button:has-text("QR")',
                'a:has-text("Connect")',
                'a:has-text("Start")',
                '[data-testid*="connect"]',
                '[data-testid*="start"]',
                '.p-button:has-text("Connect")',
                '.p-button:has-text("Start")',
                'button[class*="connect"]',
                'button[class*="start"]'
            ]
            
            button_found = None
            for selector in possible_buttons:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        button_text = await button.text_content()
                        print(f"🔘 Botão encontrado: '{button_text}' com seletor: {selector}")
                        button_found = button
                        break
                except:
                    continue
            
            if button_found:
                print("🖱️ Clicando no botão para gerar QR code...")
                await button_found.click()
                
                # Aguardar o QR code aparecer
                await page.wait_for_timeout(5000)
                
                # Capturar screenshot após clicar
                after_click_screenshot = await page.screenshot(full_page=True)
                with open('waha_after_click.png', 'wb') as f:
                    f.write(after_click_screenshot)
                print("💾 Screenshot após clique salvo como 'waha_after_click.png'")
            
            # Agora procurar pelo QR code com seletores mais específicos
            qr_selectors = [
                'canvas',  # QR code geralmente é renderizado em canvas
                'img[alt*="QR"]',
                'img[alt*="qr"]', 
                'img[src*="qr"]',
                'img[src*="data:image"]',  # Base64 images
                '[data-testid="qr-code"]',
                '[data-testid="qr"]',
                '.qr-code',
                '#qr-code',
                'svg',  # QR code pode ser SVG
                '.p-image img',  # PrimeVue image component
                '[role="img"]',  # Elementos com role de imagem
                'div[class*="qr"] img',
                'div[class*="qr"] canvas',
                'div[id*="qr"] img',
                'div[id*="qr"] canvas'
            ]
            
            qr_elements_found = []
            for selector in qr_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for i, element in enumerate(elements):
                        try:
                            # Verificar se o elemento é visível
                            is_visible = await element.is_visible()
                            if is_visible:
                                # Obter informações do elemento
                                tag_name = await element.evaluate('el => el.tagName')
                                class_name = await element.get_attribute('class') or ''
                                id_attr = await element.get_attribute('id') or ''
                                src = await element.get_attribute('src') or ''
                                
                                element_info = {
                                    'selector': selector,
                                    'index': i,
                                    'tag': tag_name,
                                    'class': class_name,
                                    'id': id_attr,
                                    'src': src[:100] if src else '',  # Primeiros 100 chars do src
                                    'visible': is_visible
                                }
                                qr_elements_found.append(element_info)
                                
                                # Capturar screenshot do elemento
                                try:
                                    element_screenshot = await element.screenshot()
                                    clean_selector = selector.replace('[', '').replace(']', '').replace(':', '_').replace('*', 'any').replace('"', '').replace("'", '')
                                    filename = f"element_{tag_name.lower()}_{i}_{clean_selector}.png"
                                    # Limpar nome do arquivo
                                    filename = filename.replace('/', '_').replace('\\', '_').replace('>', '_').replace('<', '_')
                                    with open(filename, 'wb') as f:
                                        f.write(element_screenshot)
                                    print(f"📸 Screenshot do elemento salvo: {filename}")
                                except Exception as e:
                                    print(f"❌ Erro ao capturar screenshot do elemento: {e}")
                        except Exception as e:
                            print(f"❌ Erro ao processar elemento: {e}")
                except Exception as e:
                    print(f"❌ Erro com seletor {selector}: {e}")
            
            # Salvar informações dos elementos encontrados
            with open('qr_elements_found.json', 'w', encoding='utf-8') as f:
                json.dump(qr_elements_found, f, indent=2, ensure_ascii=False)
            print(f"💾 Informações dos elementos salvos em 'qr_elements_found.json'")
            print(f"📊 Total de elementos encontrados: {len(qr_elements_found)}")
            
            # Salvar HTML da página para análise
            page_content = await page.content()
            with open('waha_page_analysis.html', 'w', encoding='utf-8') as f:
                f.write(page_content)
            print("💾 HTML da página salvo como 'waha_page_analysis.html'")
            
            # Se encontramos elementos, vamos tentar capturar o que parece ser um QR code
            if qr_elements_found:
                print("\n🎯 Elementos encontrados que podem ser QR codes:")
                for i, elem in enumerate(qr_elements_found):
                    print(f"  {i+1}. {elem['tag']} - {elem['selector']} - Class: {elem['class']} - ID: {elem['id']}")
                
                # Procurar por canvas ou imagens que possam ser QR codes
                best_candidates = []
                for elem in qr_elements_found:
                    if elem['tag'].lower() == 'canvas':
                        best_candidates.append(elem)
                    elif 'qr' in elem['class'].lower() or 'qr' in elem['id'].lower():
                        best_candidates.append(elem)
                    elif elem['src'] and ('qr' in elem['src'].lower() or 'data:image' in elem['src']):
                        best_candidates.append(elem)
                
                if best_candidates:
                    print(f"\n🏆 Melhores candidatos para QR code: {len(best_candidates)}")
                    for candidate in best_candidates:
                        print(f"  - {candidate['tag']} com seletor: {candidate['selector']}")
            
            # Aguardar um pouco antes de fechar para permitir análise visual
            print("\n⏳ Aguardando 10 segundos para análise visual...")
            await page.wait_for_timeout(10000)
            
        except Exception as e:
            print(f"❌ Erro durante a captura: {e}")
        finally:
            await browser.close()
            print("🔚 Navegador fechado")

if __name__ == "__main__":
    print("🚀 Iniciando análise do QR code do WAHA...")
    asyncio.run(capture_waha_qr_code())
    print("✅ Análise concluída!")