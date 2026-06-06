from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def net_hesapla(dogru, yanlis):
    try:
        if not dogru: dogru = 0
        if not yanlis: yanlis = 0
        return float(dogru) - (float(yanlis) / 4)
    except ValueError:
        return 0.0

def veritabanindan_bolum_getir(puan_turu, kullanici_puani):
    try:
        conn = sqlite3.connect('uni.db') 
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM UNIT")
        tum_satirlar = cursor.fetchall()
        
        cursor.execute("PRAGMA table_info(UNIT);")
        sutun_bilgileri = cursor.fetchall()
        
        uni_idx, bolum_idx, tur_idx, puan_idx = 0, 1, 2, 3
        
        for idx, sutun in enumerate(sutun_bilgileri):
            sutun_adi = sutun[1].replace('\xa0', ' ').strip()
            if "Üniversite" in sutun_adi: uni_idx = idx
            elif "Bölüm" in sutun_adi: bolum_idx = idx
            elif "Puan Türü" in sutun_adi or "Tür" in sutun_adi: tur_idx = idx
            elif "Taban Puan" in sutun_adi or "Puan" in sutun_adi: puan_idx = idx

        sonuclar = []
        
        for satir in tum_satirlar:
            satir_puan_turu = str(satir[tur_idx]).replace('\xa0', ' ').strip().upper()
            satir_taban_puan_str = str(satir[puan_idx]).replace('\xa0', ' ').strip().replace(',', '.')
            
            if puan_turu.upper() in satir_puan_turu:
                try:
                    satir_taban_puan = float(satir_taban_puan_str)
                    if satir_taban_puan <= kullanici_puani:
                        sonuclar.append((satir[uni_idx], satir[bolum_idx], satir_taban_puan))
                except ValueError:
                    continue
        
        conn.close()
        sonuclar.sort(key=lambda x: x[2], reverse=True)
        return sonuclar

    except Exception as e:
        print(f"Sistemsel Hata: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        puan_turu = request.form.get('puan_turu')
        diploma = float(request.form.get('diploma') or 0)
        
        obp = (diploma * 5) * 0.12
        
        tyt_tur = net_hesapla(request.form.get('tyt_turkce_d'), request.form.get('tyt_turkce_y'))
        tyt_mat = net_hesapla(request.form.get('tyt_mat_d'), request.form.get('tyt_mat_y'))
        tyt_sos = net_hesapla(request.form.get('tyt_sos_d'), request.form.get('tyt_sos_y'))
        tyt_fen = net_hesapla(request.form.get('tyt_fen_d'), request.form.get('tyt_fen_y'))
        
        tyt_ham_katki = (tyt_tur * 3.33) + (tyt_mat * 3.33) + (tyt_sos * 3.34) + (tyt_fen * 3.34)
        
        hesaplanan_puan = 0
        
        if puan_turu == "TYT":
            hesaplanan_puan = 100 + tyt_ham_katki + obp
            
        elif puan_turu == "SAY":
            ayt_mat = net_hesapla(request.form.get('ayt_mat_d'), request.form.get('ayt_mat_y'))
            ayt_fiz = net_hesapla(request.form.get('ayt_fiz_d'), request.form.get('ayt_fiz_y'))
            ayt_kim = net_hesapla(request.form.get('ayt_kim_d'), request.form.get('ayt_kim_y'))
            ayt_biy = net_hesapla(request.form.get('ayt_biy_d'), request.form.get('ayt_biy_y'))
            
            ayt_say_katki = (ayt_mat + ayt_fiz + ayt_kim + ayt_biy) * 5.0
            hesaplanan_puan = 100 + (tyt_ham_katki * 0.4) + (ayt_say_katki * 0.6) + obp
            
        elif puan_turu == "EA":
            ayt_mat = net_hesapla(request.form.get('ayt_mat_d'), request.form.get('ayt_mat_y'))
            ayt_edb = net_hesapla(request.form.get('ayt_edb_d'), request.form.get('ayt_edb_y'))
            ayt_tar1 = net_hesapla(request.form.get('ayt_tar1_d'), request.form.get('ayt_tar1_y'))
            ayt_cog1 = net_hesapla(request.form.get('ayt_cog1_d'), request.form.get('ayt_cog1_y'))
            
            ayt_ea_katki = (ayt_mat + ayt_edb + ayt_tar1 + ayt_cog1) * 5.0
            hesaplanan_puan = 100 + (tyt_ham_katki * 0.4) + (ayt_ea_katki * 0.6) + obp

        elif puan_turu == "SÖZ":
            ayt_edb = net_hesapla(request.form.get('ayt_edb_d'), request.form.get('ayt_edb_y'))
            ayt_tar1 = net_hesapla(request.form.get('ayt_tar1_d'), request.form.get('ayt_tar1_y'))
            ayt_cog1 = net_hesapla(request.form.get('ayt_cog1_d'), request.form.get('ayt_cog1_y'))
            ayt_tar2 = net_hesapla(request.form.get('ayt_tar2_d'), request.form.get('ayt_tar2_y'))
            ayt_cog2 = net_hesapla(request.form.get('ayt_cog2_d'), request.form.get('ayt_cog2_y'))
            ayt_fel = net_hesapla(request.form.get('ayt_fel_d'), request.form.get('ayt_fel_y'))
            ayt_din = net_hesapla(request.form.get('ayt_din_d'), request.form.get('ayt_din_y'))
            
            ayt_soz_katki = (ayt_edb + ayt_tar1 + ayt_cog1 + ayt_tar2 + ayt_cog2 + ayt_fel + ayt_din) * 5.0
            hesaplanan_puan = 100 + (tyt_ham_katki * 0.4) + (ayt_soz_katki * 0.6) + obp

        elif puan_turu == "DİL":
            ydt_dil = net_hesapla(request.form.get('ydt_d'), request.form.get('ydt_y'))
            
            ydt_katki = ydt_dil * 5.0
            hesaplanan_puan = 100 + (tyt_ham_katki * 0.4) + (ydt_katki * 0.6) + obp

        sonuclar = veritabanindan_bolum_getir(puan_turu, hesaplanan_puan)

        return render_template('index.html', puan=round(hesaplanan_puan, 2), tur=puan_turu, sonuclar=sonuclar, form_data=dict(request.form))

    return render_template('index.html', puan=None, form_data={})

if __name__ == '__main__':
    app.run(debug=True)