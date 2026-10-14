import snap7
from snap7.util import get_real, get_bool
import requests
from datetime import datetime
import time

IP_CLP = '20.1.1.1'
RACK = 0
SLOT = 1

# --- DECLARAÇÃO DAS DBs ---
DB_TEMP = 7       # Temperaturas
DB_AGUA = 21      # Hidrômetros
DB_ENERGIA = 34   # PACs (Quadros)
DB_GATILHO = 23   # DB do Bit de Gatilho

FIREBASE_URL = 'https://planta-supervisorio-default-rtdb.firebaseio.com'

plc = snap7.client.Client()
plc.connect(IP_CLP, RACK, SLOT)

if plc.get_connected():
    print("Conectado ao S7-1200 - Lendo DBs 7, 21, 34 e 23...")
else:
    print("Falha na conexão com o CLP.")
    exit()

def ler_dados_clp():
    dados_temp = plc.read_area(0x84, DB_TEMP, 0, 1048)
    dados_energia = plc.read_area(0x84, DB_ENERGIA, 0, 128)
    dados_agua = plc.read_area(0x84, DB_AGUA, 0, 750) 
    
    # Lendo apenas o byte 340 da DB23 (onde está o gatilho)
    # read_area(área, DB, offset_inicial, quantidade_de_bytes)
    dados_gatilho = plc.read_area(0x84, DB_GATILHO, 340, 1) 
    
    return {
        # --- TEMPERATURAS ---
        "temp_cms":                  round(get_real(dados_temp, 604), 2),
        "temp_envaseCms":            round(get_real(dados_temp, 784), 2),
        "temp_salaCortes1":          round(get_real(dados_temp, 724), 2),
        "temp_salaCortes2":          round(get_real(dados_temp, 744), 2),
        "temp_abastiqf":             round(get_real(dados_temp, 644), 2),
        "temp_embprimariaiqf":       round(get_real(dados_temp, 624), 2),
        "temp_frangointeiro":        round(get_real(dados_temp, 704), 2),
        "temp_temperados":           round(get_real(dados_temp, 564), 2),
        "temp_chillers":             round(get_real(dados_temp, 764), 2),
        "temp_miudos":               round(get_real(dados_temp, 664), 2),
        "temp_padronizacao":         round(get_real(dados_temp, 804), 2),
        "temp_paletizacao":          round(get_real(dados_temp, 824), 2),
        "temp_chiller_condicionais": round(get_real(dados_temp, 544), 2),
        "temp_pre_chiller_entrada":  round(get_real(dados_temp, 284), 2),
        "temp_pre_chiller_saida":    round(get_real(dados_temp, 304), 2),
        "temp_chiller1_entrada":     round(get_real(dados_temp, 324), 2),
        "temp_chiller1_saida":       round(get_real(dados_temp, 344), 2),
        "temp_chiller2_entrada":     round(get_real(dados_temp, 364), 2),
        "temp_chiller2_saida":       round(get_real(dados_temp, 384), 2),
        "temp_chiller_coracao":      round(get_real(dados_temp, 184), 2),
        "temp_chiller_figado":       round(get_real(dados_temp, 164), 2),
        "temp_chiller_moela":        round(get_real(dados_temp, 264), 2),
        "temp_chiller_cabeca":       round(get_real(dados_temp, 204), 2),
        "temp_chiller_pe1":          round(get_real(dados_temp, 224), 2),
        "temp_chiller_pe2":          round(get_real(dados_temp, 244), 2),
        "temp_abast_pre_chiller":    round(get_real(dados_temp, 84), 2),
        "temp_retmac_pre_chiller":   round(get_real(dados_temp, 104), 2),
        "temp_abast_chiller2":       round(get_real(dados_temp, 484), 2),
        "temp_retmac_chiller2":      round(get_real(dados_temp, 504), 2),
        "temp_saida_placas":         round(get_real(dados_temp, 1044), 2),
        
        # --- ENERGIA ---
        "ccm1_tensao":         round(get_real(dados_energia, 28), 2),
        "ccm1_potencia":       round(get_real(dados_energia, 20), 2),
        "ccm2_tensao":         round(get_real(dados_energia, 60), 2),
        "ccm2_potencia":       round(get_real(dados_energia, 52), 2),
        "qgbt1_tensao":        round(get_real(dados_energia, 92), 2),
        "qgbt1_potencia":      round(get_real(dados_energia, 84), 2),
        "qgbt2_tensao":        round(get_real(dados_energia, 124), 2),
        "qgbt2_potencia":      round(get_real(dados_energia, 116), 2),
        
        # --- ÁGUA (TOTALIZADORES PARA TEMPO REAL) ---
        "agua_pre_chiller":       round(get_real(dados_agua, 638), 2),
        "agua_chiller1":          round(get_real(dados_agua, 642), 2),
        "agua_chiller2":          round(get_real(dados_agua, 646), 2),
        "agua_condicionais":      round(get_real(dados_agua, 650), 2),
        "agua_coracao":           round(get_real(dados_agua, 654), 2),
        "agua_figado":            round(get_real(dados_agua, 658), 2),
        "agua_moela":             round(get_real(dados_agua, 662), 2),
        "agua_cabeca":            round(get_real(dados_agua, 666), 2),
        "agua_pe1":               round(get_real(dados_agua, 670), 2),
        "agua_pe2":               round(get_real(dados_agua, 674), 2),
        "agua_chuveiro_final":    round(get_real(dados_agua, 678), 2),
        "agua_tanque_escalda":    round(get_real(dados_agua, 682), 2),

        # --- ÁGUA (PULSOS DE CONSUMO PARA TABELA/GRÁFICO) ---
        "agua_cons_pre_chiller":    round(get_real(dados_agua, 10), 2),
        "agua_cons_chiller1":       round(get_real(dados_agua, 48), 2),
        "agua_cons_chiller2":       round(get_real(dados_agua, 86), 2),
        "agua_cons_pe1":            round(get_real(dados_agua, 124), 2),
        "agua_cons_pe2":            round(get_real(dados_agua, 162), 2),
        "agua_cons_cabeca":         round(get_real(dados_agua, 200), 2),
        "agua_cons_moela":          round(get_real(dados_agua, 238), 2),
        "agua_cons_coracao":        round(get_real(dados_agua, 276), 2),
        "agua_cons_figado":         round(get_real(dados_agua, 314), 2),
        "agua_cons_condicionais":   round(get_real(dados_agua, 352), 2),
        "agua_cons_chuveiro_final": round(get_real(dados_agua, 708), 2),
        "agua_cons_tanque_escalda": round(get_real(dados_agua, 746), 2),
        
        # --- GATILHO ---
        # get_bool(bytearray, indice_do_byte_no_array, indice_do_bit)
        # Como lemos apenas 1 byte (o 340) a partir do offset 340, ele é o byte 0 do array "dados_gatilho"
        "gatilho_2_horas":          get_bool(dados_gatilho, 0, 0) # Lendo o bit .0 (DBX340.0)
    }

ultimo_salvamento_1min = 0
estado_anterior_gatilho = False # Para detectar a borda de subida

try:
    while True:
        agora = time.time()
        hoje = datetime.now()
        dados = ler_dados_clp()
        
        gatilho_atual = dados["gatilho_2_horas"]
        
        # 1. Atualiza Tempo Real a cada 5 segundos
        res_tr = requests.put(f"{FIREBASE_URL}/tempo_real.json", json=dados)
        if res_tr.status_code != 200:
            print(f"Erro Realtime Firebase: {res_tr.text}")
            
        data_atual = hoje.strftime("%Y-%m-%d")
        hora_atual = hoje.strftime("%H:%M")
        url_hist = f"{FIREBASE_URL}/historico/{data_atual}/{hora_atual}.json"

        # 2. Salva Histórico de Temperatura e Energia (A cada 60 segundos)
        if agora - ultimo_salvamento_1min >= 60:
            # Filtra removendo chaves de água e o próprio gatilho
            dados_temp_energia = {k: v for k, v in dados.items() if not k.startswith("agua_") and k != "gatilho_2_horas"}
            res_hist_1min = requests.patch(url_hist, json=dados_temp_energia)
            
            if res_hist_1min.status_code == 200:
                pass # Removi o print para não poluir muito, já que roda a cada minuto
            else:
                print(f"Erro ao salvar Temp/Energia: {res_hist_1min.text}")
                
            ultimo_salvamento_1min = agora

        # 3. Salva Histórico de Água (Acionado pelo CLP - Borda de Subida)
        # Verifica se o gatilho está True AGORA e estava False no loop anterior
        if gatilho_atual and not estado_anterior_gatilho:
            dados_agua = {k: v for k, v in dados.items() if k.startswith("agua_")}
            res_hist_2hrs = requests.patch(url_hist, json=dados_agua)
            
            if res_hist_2hrs.status_code == 200:
                print(f"[{hora_atual}] Histórico de Água salvo via GATILHO DO CLP.")
            else:
                print(f"Erro ao salvar Água: {res_hist_2hrs.text}")
                
        # Atualiza o estado para o próximo ciclo
        estado_anterior_gatilho = gatilho_atual

        print(f"[{hoje.strftime('%H:%M:%S')}] Lendo CLP. Potência: {dados['ccm1_potencia']} kW | Água Chiller: {dados['agua_pre_chiller']} m³ | Gatilho: {gatilho_atual}")
        
        time.sleep(5)

except KeyboardInterrupt:
    print("\nDesconectando do CLP...")
    plc.disconnect()