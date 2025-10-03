import requests
import re
import os
import sys
import time
from bs4 import BeautifulSoup

def main():
    print("🚀 PyGoals M3U8 Kanal İndirici Başlatılıyor...")
    print("⏰ Lütfen işlemin tamamlanmasını bekleyin...")
    
    base = "https://trgoals"
    domain = ""
    
    start_range = 1400
    end_range = 2500

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    
    domain_pattern = re.compile(r'https://trgoals[0-9]+\.xyz')

    print(f"\n🔍 Doğru domain aranıyor: trgoals{start_range}.xyz → trgoals{end_range-1}.xyz")
    for i in range(start_range, end_range):
        test_domain = f"{base}{i}.xyz"
        try:
            response = requests.get(test_domain, timeout=10, allow_redirects=True, headers=headers)
            final_url = response.url.rstrip('/')

            if response.status_code == 200 and domain_pattern.match(final_url):
                domain = final_url
                print(f"✅ Geçerli ve numaralı domain bulundu: {domain}")
                break
            else:
                print(f"⏳ Denenen domain: {test_domain} -> Yönlendi: {final_url} (Geçersiz format, devam ediliyor...)")

        except requests.exceptions.RequestException:
            # Bu hataları log'da daha temiz tutmak için sessizce geçebiliriz.
            continue
    
    if not domain:
        print("❌ UYARI: Hiçbir geçerli domain bulunamadı - işlem sonlandırılacak.")
        sys.exit(1)

    # --- YENİ MANTIK: KANALLARI ANA SAYFADAN OTOMATİK ÇEKME ---
    print(f"\n📡 Kanallar ana sayfadan çekiliyor: {domain}")
    try:
        main_page_response = requests.get(domain, headers=headers, timeout=10)
        soup = BeautifulSoup(main_page_response.text, 'html.parser')
        
        channels = {}
        # 7/24 Kanallar sekmesini bul
        tab_content = soup.find('div', {'id': '24-7-tab'})
        if tab_content:
            # Sekme içindeki tüm kanal linklerini bul
            channel_links = tab_content.find_all('a', class_='channel-item')
            for link in channel_links:
                href = link.get('href')
                name_div = link.find('div', class_='channel-name')
                if href and name_div and 'id=' in href:
                    channel_id = href.split('id=')[-1]
                    channel_name = name_div.text.strip()
                    # Şimdilik hepsine genel bir kategori atayalım
                    channels[channel_id] = (channel_name, "7/24 Kanallar")
            print(f"✅ {len(channels)} adet 7/24 kanalı başarıyla bulundu.")
        else:
            print("❌ '7/24 Kanallar' sekmesi bulunamadı. Sayfa yapısı değişmiş olabilir.")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"❌ Ana sayfa okunurken hata oluştu: {e}")
        sys.exit(1)

    if not channels:
        print("❌ Hiç kanal bulunamadı. İşlem durduruluyor.")
        sys.exit(1)

    # --- KODUN GERİ KALANI BU DİNAMİK LİSTE ÜZERİNDEN DEVAM EDİYOR ---
    m3u_content = []
    output_filename = "kanallar.m3u8"

    print(f"\n📺 {len(channels)} kanal için linkler işleniyor...")
    created = 0
    failed = 0
    
    for i, (channel_id, (channel_name, category)) in enumerate(channels.items(), 1):
        try:
            print(f"[{i}/{len(channels)}] {channel_name} işleniyor...", end=' ')
            url = f"{domain}/channel.html?id={channel_id}"
            # baseurl'yi bulmak için bu sefer sayfanın tamamını indirmemiz gerekmeyebilir.
            # HEAD isteği ile daha hızlı kontrol edebiliriz, eğer olmazsa GET'e döneriz.
            channel_page_response = requests.get(url, headers=headers, timeout=10)
            
            if channel_page_response.status_code != 200:
                print(f"-> ❌ Sayfa Hatası: {channel_page_response.status_code}")
                failed += 1
                continue
            
            match = re.search(r'const baseurl = "(.*?)"', channel_page_response.text)
            if not match:
                # BAZI KANALLARIN baseurl'si olmayabilir, bu normal. Hata sayısını artırmayalım.
                print("-> ❌ BaseURL bulunamadı (Bu kanal için normal olabilir).")
                continue # Bu kanalı atla ve devam et
            
            baseurl = match.group(1)
            direct_url = f"{baseurl}{channel_id}.m3u8"
            
            m3u_content.append(f'#EXTINF:-1 tvg-name="{channel_name}" group-title="{category}",{channel_name}')
            m3u_content.append(direct_url)
            
            print("-> ✅ Link bulundu.")
            created += 1
            time.sleep(0.1)
            
        except requests.exceptions.RequestException:
            print("-> ❌ Ağ hatası.")
            failed += 1
        except Exception:
            print("-> ❌ Beklenmeyen hata.")
            failed += 1
    
    # Dosya yazma ve raporlama kısmı aynı...
    if created > 0:
        try:
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
        except Exception as e:
            print(f"\n❌ KRİTİK HATA: Dosya yazılamadı: {e}")
    else:
        print("\nℹ️  BaseURL içeren hiçbir kanal linki bulunamadığı için dosya oluşturulmadı.")

    print("\n" + "="*50)
    print("📊 İŞLEM SONUCLARI")
    print("="*50)
    print(f"✅ Başarıyla oluşturulan link: {created}")
    print(f"❌ Başarısız veya atlanan kanal: {len(channels) - created}")
    
    if created > 0:
        print("\n🎉 İşlem başarıyla tamamlandı!")
    else:
        print("\nℹ️  Hiç dosya oluşturulamadı.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ KRİTİK HATA: {e}")
        sys.exit(1)
