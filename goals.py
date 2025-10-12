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
        user_agent_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=user_agent_string)
        page = context.new_page()

        domain = find_working_domain(page)

        if not domain:
            print("❌ UYARI: Hiçbir geçerli domain bulunamadı - işlem sonlandırılacak.")
            browser.close()
            sys.exit(1)

        channels = {
            # BeinSports Kategorisi
            "yayinzirve": ("beIN Sports 1 ☪️", "BeinSports"), "yayininat": ("beIN Sports 1 ⭐", "BeinSports"),
            "yayin1": ("beIN Sports 1 ♾️", "BeinSports"), "yayinb2": ("beIN Sports 2", "BeinSports"),
            "yayinb3": ("beIN Sports 3", "BeinSports"), "yayinb4": ("beIN Sports 4", "BeinSports"),
            "yayinb5": ("beIN Sports 5", "BeinSports"), "yayinbm1": ("beIN Sports 1 Max", "BeinSports"),
            "yayinbm2": ("beIN Sports 2 Max", "BeinSports"),
            # S Sports Kategorisi
            "yayinss": ("Saran Sports 1", "S Sports"), "yayinss2": ("Saran Sports 2", "S Sports"),
            # Tivibu Kategorisi
            "yayint1": ("Tivibu Sports 1", "Tivibu"), "yayint2": ("Tivibu Sports 2", "Tivibu"),
            "yayint3": ("Tivibu Sports 3", "Tivibu"), "yayint4": ("Tivibu Sports 4", "Tivibu"),
            # Smart Sports Kategorisi
            "yayinsmarts": ("Smart Sports", "Smart Sports"), "yayinsms2": ("Smart Sports 2", "Smart Sports"),
            # NBA Kategorisi
            "yayinnbatv": ("NBA TV", "NBA"),
            # Ulusal Kategorisi
            "yayinatv": ("ATV", "Ulusal"), "yayintv8": ("TV8", "Ulusal"), "yayintv85": ("TV8.5", "Ulusal"),
            "yayinas": ("A Spor", "Ulusal"),
            # Tabii Kategorisi
            "yayinex1": ("Tâbii 1", "Tabii"), "yayinex2": ("Tâbii 2", "Tabii"),
            "yayinex3": ("Tâbii 3", "Tabii"), "yayinex4": ("Tâbii 4", "Tabii"), "yayinex5": ("Tâbii 5", "Tabii"),
            "yayinex6": ("Tâbii 6", "Tabii"), "yayinex7": ("Tâbii 7", "Tabii"), "yayinex8": ("Tâbii 8", "Tabii"),
            # TRT Kategorisi
            "yayintrt1": ("TRT 1", "TRT"), "yayintrtspor": ("TRT Spor", "TRT"), "yayintrtspor2": ("TRT Spor 2", "TRT"),
            # Euro Sport Kategorisi
            "yayineu1": ("Euro Sport 1", "Euro Sport"), "yayineu2": ("Euro Sport 2", "Euro Sport"),
        }
        
        # Dosyaya yazmadan önce tüm başarılı kanal verilerini burada toplayacağız
        found_channels_data = []
        output_filename = "kanallar.m3u8"
        print(f"\n📺 {len(channels)} kanal için linkler işleniyor...")
        
        for i, (channel_id, (channel_name, category)) in enumerate(channels.items(), 1):
            try:
                print(f"[{i}/{len(channels)}] {channel_name} işleniyor...", end=' ')
                url = f"{domain}/channel.html?id={channel_id}"
                
                # KRİTİK DEĞİŞİKLİK: Sayfaya gitmeden önce .m3u8 ile biten bir ağ isteği beklediğimizi belirtiyoruz.
                with page.expect_request("**/*.m3u8", timeout=20000) as request_info:
                    # Bu eylem, yukarıdaki beklenen isteği tetikleyecek
                    page.goto(url, wait_until='domcontentloaded', timeout=20000)
                
                # İstek yakalandı, şimdi detaylarını alalım
                m3u8_request = request_info.value
                headers = m3u8_request.headers
                
                direct_url = m3u8_request.url
                # Gerçek başlıkları al, eğer yoksa domain'i yedek olarak kullan
                referer = headers.get('referer', f"{domain}/")
                origin = headers.get('origin', domain)

                # Bulunan tüm verileri daha sonra dosyaya yazmak üzere listeye ekle
                found_channels_data.append({
                    "channel_name": channel_name,
                    "category": category,
                    "direct_url": direct_url,
                    "referer": referer,
                    "origin": origin
                })
                
                print("-> ✅ Link ve başlıklar yakalandı.")
                time.sleep(0.5)
            except PlaywrightError:
                print("-> ❌ Sayfa veya .m3u8 isteği zaman aşımına uğradı.")
                continue

        browser.close()

        if found_channels_data:
            # M3U başlığı için İLK bulunan kanalın bilgilerini kullanalım, bu en doğrusu olacaktır.
            first_channel = found_channels_data[0]
            header = f"""#EXTM3U
#EXT-X-USER-AGENT:{user_agent_string}
#EXT-X-REFERER:{first_channel['referer']}
#EXT-X-ORIGIN:{first_channel['origin']}"""

            m3u_content = []
            for channel in found_channels_data:
                m3u_content.append(f'#EXTINF:-1 tvg-name="{channel["channel_name"]}" group-title="{channel["category"]}",{channel["channel_name"]}')
                m3u_content.append(channel["direct_url"])

            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(header)
                f.write("\n") 
                f.write("\n".join(m3u_content))
            print(f"\n📂 {len(found_channels_data)} kanal başarıyla '{output_filename}' dosyasına kaydedildi.")
        else:
            print("\nℹ️  Hiçbir kanaldan .m3u8 linki yakalanamadığı için dosya oluşturulmadı.")

        print("\n" + "="*50)
        print("📊 İŞLEM SONUCLARI")
        print("="*50)
        print(f"✅ Başarıyla yakalanan link: {len(found_channels_data)}")
        print(f"❌ Başarısız veya atlanan kanal: {len(channels) - len(found_channels_data)}")
        print("\n🎉 İşlem başarıyla tamamlandı!")

if __name__ == "__main__":
    main()
