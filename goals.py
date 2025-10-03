import requests
import re
import os
import sys
import time

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
        'Sec-Ch-Ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    }
    
    # DEĞİŞİKLİK: Sadece "trgoals" ve ardından sayı içeren domainleri kabul edecek bir kural (regex)
    domain_pattern = re.compile(r'https://trgoals[0-9]+\.xyz')

    print(f"\n🔍 Domain aranıyor: trgoals{start_range}.xyz → trgoals{end_range-1}.xyz")
    for i in range(start_range, end_range):
        test_domain = f"{base}{i}.xyz"
        try:
            response = requests.get(test_domain, timeout=10, allow_redirects=True, headers=headers)
            
            # Yönlendirme sonrası ulaşılan son URL'yi al ve temizle (sondaki / işaretini kaldır)
            final_url = response.url.rstrip('/')

            # KRİTİK DEĞİŞİKLİK:
            # Durum kodu 200 OLMALI VE bulunan URL'nin formatı bizim istediğimiz NUMARALI formata uymalı.
            if response.status_code == 200 and domain_pattern.match(final_url):
                domain = final_url
                print(f"✅ Geçerli ve numaralı domain bulundu: {domain}")
                break # Doğru formatı bulduğumuz için aramayı durdur.
            else:
                # Eğer format uymuyorsa (örn: trgoalsgiris.xyz), bunu bir yönlendirme olarak bildir ama devam et.
                print(f"⏳ Denenen domain: {test_domain} -> Yönlendi: {final_url} (Geçersiz format, devam ediliyor...)")

        except requests.exceptions.RequestException as e:
            print(f"⏳ Denenen domain: {test_domain} (Hata: {str(e)[:40]}...)")
            continue
    
    if not domain:
        print("❌ UYARI: Hiçbir geçerli domain bulunamadı - işlem sonlandırılacak.")
        sys.exit(1)
    
    # --- KODUN GERİ KALANI DEĞİŞMEDİ ---
    channels = {
        "yayinzirve": ("beIN Sports 1 ☪️", "BeinSports"),
        "yayininat": ("beIN Sports 1 ⭐", "BeinSports"),
        "yayin1": ("beIN Sports 1 ♾️", "BeinSports"),
        "yayinb2": ("beIN Sports 2", "BeinSports"),
        "yayinb3": ("beIN Sports 3", "BeinSports"),
        "yayinb4": ("beIN Sports 4", "BeinSports"),
        "yayinb5": ("beIN Sports 5", "BeinSports"),
        "yayinbm1": ("beIN Sports 1 Max", "BeinSports"),
        "yayinbm2": ("beIN Sports 2 Max", "BeinSports"),
        "yayinss": ("Saran Sports 1", "Spor"),
        "yayinss2": ("Saran Sports 2", "Spor"),
        "yayint1": ("Tivibu Sports 1", "Spor"),
        "yayint2": ("Tivibu Sports 2", "Spor"),
        "yayint3": ("Tivibu Sports 3", "Spor"),
        "yayint4": ("Tivibu Sports 4", "Spor"),
        "yayinsmarts": ("Smart Sports", "Spor"),
        "yayinsms2": ("Smart Sports 2", "Spor"),
        "yayintrtspor": ("TRT Spor", "Spor"),
        "yayintrtspor2": ("TRT Spor 2", "Spor"),
        "yayinas": ("A Spor", "Spor"),
        "yayinnbatv": ("NBA TV", "Spor"),
        "yayinatv": ("ATV", "Ulusal"),
        "yayintv_8": ("TV8", "Ulusal"),
        "yayintv_85": ("TV8.5", "Ulusal"),
        "yayinex1": ("Tâbii 1", "Tabii"),
        "yayinex2": ("Tâbii 2", "Tabii"),
        "yayinex3": ("Tâbii 3", "Tabii"),
        "yayinex4": ("Tâbii 4", "Tabii"),
        "yayinex5": ("Tâbii 5", "Tabii"),
        "yayinex6": ("Tâbii 6", "Tabii"),
        "yayinex7": ("Tâbii 7", "Tabii"),
        "yayinex8": ("Tâbii 8", "Tabii")
    }
    
    m3u_content = []
    output_filename = "kanallar.m3u8"

    print(f"\n📺 {len(channels)} kanal işleniyor...")
    created = 0
    failed = 0
    
    for i, (channel_id, (channel_name, category)) in enumerate(channels.items(), 1):
        try:
            print(f"\n[{i}/{len(channels)}] {channel_name} ({category}) işleniyor...")
            url = f"{domain}/channel.html?id={channel_id}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ HTTP Hatası: {response.status_code}")
                failed += 1
                continue
            
            match = re.search(r'const baseurl = "(.*?)"', response.text)
            if not match:
                print("❌ BaseURL bulunamadı")
                failed += 1
                continue
            
            baseurl = match.group(1)
            direct_url = f"{baseurl}{channel_id}.m3u8"
            
            m3u_content.append(f'#EXTINF:-1 tvg-name="{channel_name}" group-title="{category}",{channel_name}')
            m3u_content.append(direct_url)
            
            print(f"✅ {channel_name} → link bulundu.")
            created += 1
            
            time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ağ hatası: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            failed += 1
    
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
            print(f"\n📂 Tüm kanallar başarıyla '{output_filename}' dosyasına kaydedildi.")
        except Exception as e:
            print(f"\n❌ KRİTİK HATA: Dosya yazılamadı: {e}")
    else:
        print("\nℹ️  Hiçbir kanal linki bulunamadığı için dosya oluşturulmadı.")

    print("\n" + "="*50)
    print("📊 İŞLEM SONUCLARI")
    print("="*50)
    print(f"✅ Başarılı: {created}")
    print(f"❌ Başarısız: {failed}")
    
    if created > 0:
        print("\n🎉 İşlem başarıyla tamamlandı!")
    else:
        print("\nℹ️  Hiç dosya oluşturulamadı, lütfen internet bağlantınızı kontrol edin.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ KRİTİK HATA: {e}")
        sys.exit(1)
