import requests
import re
import os
import sys
import time

def main():
    print("🚀 PyGoals M3U8 Kanal İndirici Başlatılıyor...")
    print("⏰ Lütfen işlemin tamamlanmasını bekleyin...")
    
    # Trgoals domain kontrol
    base = "https://trgoals"
    domain = ""
    
    print("\n🔍 Domain aranıyor: trgoals1407.xyz → trgoals2100.xyz")
    for i in range(1407, 2101):
        test_domain = f"{base}{i}.xyz"
        try:
            response = requests.head(test_domain, timeout=3)
            if response.status_code == 200:
                domain = test_domain
                print(f"✅ Domain bulundu: {domain}")
                break
            else:
                print(f"⏳ Denenen domain: {test_domain} (Status: {response.status_code})")
        except Exception as e:
            print(f"⏳ Denenen domain: {test_domain} (Hata: {str(e)[:30]}...)")
            continue
    
    if not domain:
        print("❌ UYARI: Hiçbir domain çalışmıyor - işlem sonlandırılacak.")
        sys.exit(1)
    
    # DEĞİŞİKLİK 1: Kanal veri yapısı güncellendi.
    # Artık her kanal için bir tuple (demet) içinde (Kanal Adı, Kategori) bilgisi tutuluyor.
    channels = {
        # BeinSports Kategorisi
        "yayinzirve": ("beIN Sports 1 ☪️", "BeinSports"),
        "yayininat": ("beIN Sports 1 ⭐", "BeinSports"),
        "yayin1": ("beIN Sports 1 ♾️", "BeinSports"),
        "yayinb2": ("beIN Sports 2", "BeinSports"),
        "yayinb3": ("beIN Sports 3", "BeinSports"),
        "yayinb4": ("beIN Sports 4", "BeinSports"),
        "yayinb5": ("beIN Sports 5", "BeinSports"),
        "yayinbm1": ("beIN Sports 1 Max", "BeinSports"),
        "yayinbm2": ("beIN Sports 2 Max", "BeinSports"),
        # Spor Kategorisi
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
        # Ulusal Kategorisi
        "yayinatv": ("ATV", "Ulusal"),
        "yayintv8": ("TV8", "Ulusal"),
        "yayintv85": ("TV8.5", "Ulusal"),
        # Tabii Kategorisi
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
    
    # DEĞİŞİKLİK 2: Döngü, yeni veri yapısını okuyacak şekilde güncellendi.
    # (channel_name, category) tuple'ı ayrıştırılıyor.
    for i, (channel_id, (channel_name, category)) in enumerate(channels.items(), 1):
        try:
            print(f"\n[{i}/{len(channels)}] {channel_name} ({category}) işleniyor...")
            
            url = f"{domain}/channel.html?id={channel_id}"
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            
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
            
            # DEĞİŞİKLİK 3: M3U satırına 'group-title' (kategori) eklendi.
            m3u_content.append(f'#EXTINF:-1 tvg-name="{channel_name}" group-title="{category}",{channel_name}')
            m3u_content.append(direct_url)
            
            print(f"✅ {channel_name} → link bulundu.")
            created += 1
            
            time.sleep(0.1)
            
        except requests.exceptions.Timeout:
            print("❌ İstek zaman aşımına uğradı")
            failed += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ Ağ hatası: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            failed += 1
    
    if created > 0:
        try:
            header = f"""#EXTM3U
#EXT-X-USER-AGENT:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36
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
