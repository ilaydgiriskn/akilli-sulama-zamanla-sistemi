import sys
import os

# app dizinini modül arama yoluna ekle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.decision_engine import calculate_water_balance, decide_irrigation

def run_tests():
    print("--- Karar Motoru Testleri ---\n")
    
    # Senaryo 1: Yağış yok, sıcaklık normal, bütçe sınırda
    # Önceki bütçe: -10, Sebze tüketimi: 4.5
    # Yeni bütçe = -10 + 0 - 4.5 = -14.5 (Eşik -15.0) -> SULAMA GEREKMİYOR
    nb1 = calculate_water_balance(-10.0, 0.0, "sebze", 25.0)
    decision1 = decide_irrigation(nb1, 50, 0.0)
    print(f"Senaryo 1 | Yeni Bütçe: {nb1} | Karar: {decision1}")
    assert decision1 == "SULAMA GEREKMİYOR"
    
    # Senaryo 2: Yağış yok, sıcaklık yüksek, bütçe eşiği geçiyor
    # Önceki bütçe: -11, Sebze tüketimi: 4.5 * 1.15 = 5.175
    # Yeni bütçe = -11 + 0 - 5.175 = -16.175 (Eşik -15.0) -> SULAMA ÖNERİLİR
    nb2 = calculate_water_balance(-11.0, 0.0, "sebze", 32.0)
    decision2 = decide_irrigation(nb2, 50, 0.0)
    print(f"Senaryo 2 | Yeni Bütçe: {nb2} | Karar: {decision2}")
    assert decision2 == "SULAMA ÖNERİLİR"
    
    # Senaryo 3: Yağış bekleniyor ve nem yüksek
    # Önceki bütçe: -14, Yeni bütçe < -15 olsa bile
    nb3 = calculate_water_balance(-14.0, 10.0, "tahil", 20.0) # Tahıl = 3.5, -14 + 10 - 3.5 = -7.5
    decision3 = decide_irrigation(nb3, 80, 10.0)
    print(f"Senaryo 3 | Yeni Bütçe: {nb3} | Karar: {decision3}")
    assert "SULAMA GEREKMİYOR" in decision3

    print("\n[BAŞARILI] Tüm testler geçti!")

if __name__ == "__main__":
    run_tests()
