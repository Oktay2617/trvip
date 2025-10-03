import re
import os
import sys
import time
from playwright.sync_api import sync_playwright, Error as PlaywrightError

def find_working_domain(page):
    """Verilen aralıkta çalışan ve doğru formattaki trgoals domain'ini bulur."""
    
    MANUAL_DOMAIN = "https://trgoals1423.xyz"
    print(f"\n🔍 Öncelikli domain deneniyor: {MANUAL_DOMAIN}")
    try:
        response = page.goto(MANUAL_DOMAIN, timeout=20000, wait_until='domcontentloaded')
        if response and response.ok:
            # Sayfa URL'sinin sonundaki '/' işaretini kaldır
            final_url = page.url.rstrip('/')
            print(f"✅ Öncelikli domain başarıyla bulundu: {final_url}")
            return final_url
    except PlaywrightError as e:
        print(f"⚠️ Öncelikli domain'e bağlanılamadı (Hata: {e.__class__.__name__}). Otomatik arama başlatılacak...")

    base = "https://trgoals"
    start_range = 1400
    end_range = 2500
    domain_pattern = re.compile(r'https://trgoals[0-9]+\.xyz')

    print(f"\n🔍 Otomatik arama: trgoals{start_range}.xyz → trgoals{end_range-1}.xyz")
    for i in range(start_range, end_range):
        test_domain = f"{base}{i}.xyz"
        try:
            response = page.goto(test_domain, timeout=15000, wait_until='domcontentloaded')
            final_url = page.url.rstrip('/')
            
            if response and response.ok and domain_pattern.match(final_url):
                print(f"✅ Otomatik arama ile domain bulundu: {final_url}")
                return final_url
        except PlaywrightError:
            continue
            
    return None

def main():
    with sync_playwright() as p:
        print("🚀 Playwright ile M3U8 Kanal İndirici Başlatılıyor...")
        
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        domain = find_working_domain(page)

        if not domain:
            print("❌ UYARI: Hiçbir geçerli domain bulunamadı - işlem sonlandırılacak.")
            browser.close()
            sys.exit(1)

        print(f"\n📡 Kanallar ana sayfadan çekiliyor: {domain}")
        try:
            page.goto(domain, timeout=20000, wait_until='domcontentloaded')
            
            channels = {}
            # --- BURASI DÜZELTİLDİ ---
            tab_content = page.locator('div[id="24-7-tab"]')
            
            channel_links = tab_content.locator('a.channel-item').all()

            for link in channel_links:
                href = link.get_attribute('href')
                name_div = link.locator('div.channel-name')
                if href and name_div and 'id=' in href:
                    channel_id = href.split('id=')[-1]
                    channel_name = name_div.inner_text().strip()
                    channels[channel_id] = (channel_name, "7/24 Kanallar")
            
            print(f"✅ {len(channels)} adet 7/24 kanalı başarıyla bulundu.")
        except PlaywrightError as e:
            print(f"❌ Ana sayfa okunurken hata oluştu: {e}")
            browser.close()
            sys.exit(1)

        if not channels:
            print("❌ Hiç kanal bulunamadı. İşlem durduruluyor.")
            browser.close()
            sys.exit(1)

        m3u_content = []
        output_filename = "kanallar.m3u8"
        print(f"\n📺 {len(channels)} kanal için linkler işleniyor...")
        created = 0
        
        for i, (channel_id, (channel_name, category)) in enumerate(channels.items(), 1):
            try:
                print(f"[{i}/{len(channels)}] {channel_name} işleniyor...", end=' ')
                url = f"{domain}/channel.html?id={channel_id}"
                page.goto(url, timeout=15000, wait_until='domcontentloaded')
                
                content = page.content()
                match = re.search(r'const baseurl = "(.*?)"', content)

                if not match:
                    print("-> ❌ BaseURL bulunamadı.")
                    continue
                
                baseurl = match.group(1)
                direct_url = f"{baseurl}{channel_id}.m3u8"
                
                m3u_content.append(f'#EXTINF:-1 tvg-name="{channel_name}" group-title="{category}",{channel_name}')
                m3u_content.append(direct_url)
                
                print("-> ✅ Link bulundu.")
                created += 1
                time.sleep(0.5)
            except PlaywrightError:
                print("-> ❌ Sayfaya ulaşılamadı.")
                continue

        browser.close()

        if created > 0:
            header = f"""#EXTM3U
#EXT-X-USER-AGENT:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36
#EXT-X-REFERER:{domain}/
#EXT-X-ORIGIN:{domain}
"""
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(header)
                f.write("\n\n")
                f.write("\n".join(m3u_content))
            print(f"\n📂 {created} kanal başarıyla '{output_filename}' dosyasına kaydedildi.")
        else:
            print("\nℹ️  BaseURL içeren hiçbir kanal linki bulunamadığı için dosya oluşturulmadı.")

        print("\n" + "="*50)
        print("📊 İŞLEM SONUCLARI")
        print("="*50)
        print(f"✅ Başarıyla oluşturulan link: {created}")
        print(f"❌ Başarısız veya atlanan kanal: {len(channels) - created}")
        print("\n🎉 İşlem başarıyla tamamlandı!")

if __name__ == "__main__":
    main()
