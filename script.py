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

# --- SISTEMA DO ACUMULADOR MENSAL ---
acumulador_mensal = {
    "abatedouro": 0.0,
    "sala": 0.0,
    "ultimo_mes_reset": 0
}

try:
    print("Sincronizando acumulador mensal com o Firebase...")
    res_ac = requests.get(f"{FIREBASE_URL}/acumulados_mes.json")
    if res_ac.status_code == 200 and res_ac.json():
        dados_nuvem = res_ac.json()
        acumulador_mensal["abatedouro"] = dados_nuvem.get("abatedouro", 0.0)
        acumulador_mensal["sala"] = dados_nuvem.get("sala", 0.0)
        acumulador_mensal["ultimo_mes_reset"] = dados_nuvem.get("ultimo_mes_reset", 0)
except Exception as e:
    print(f"Aviso: Iniciando acumulador do zero. Motivo: {e}")

def ler_dados_clp():
    dados_temp = plc.read_area(0x84, DB_TEMP, 0, 1048)
    dados_energia = plc.read_area(0x84, DB_ENERGIA, 0, 128)
    dados_agua = plc.read_area(0x84, DB_AGUA, 0, 750) 
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
        
        # --- ÁGUA ---
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
        "gatilho_2_horas":          get_bool(dados_gatilho, 0, 0)
    }

ultimo_salvamento_1min = 0
estado_anterior_gatilho = False

try:
    while True:
        agora = time.time()
        hoje = datetime.now()
        dados = ler_dados_clp()
        gatilho_atual = dados["gatilho_2_horas"]
        
        # 1. Atualiza Tempo Real (A cada 5 segundos)
        res_tr = requests.put(f"{FIREBASE_URL}/tempo_real.json", json=dados)
            
        data_atual = hoje.strftime("%Y-%m-%d")
        hora_atual = hoje.strftime("%H:%M")
        url_hist = f"{FIREBASE_URL}/historico/{data_atual}/{hora_atual}.json"

        # 2. Salva Histórico e Acumulador (A cada 60 segundos)
        if agora - ultimo_salvamento_1min >= 60:
            
            # 2.1 ATUALIZA O ACUMULADOR MENSAL
            # Se for dia 12 (ou maior) e ainda não tivermos zerado a conta neste mês
            if hoje.day >= 12 and acumulador_mensal.get("ultimo_mes_reset") != hoje.month:
                acumulador_mensal["abatedouro"] = 0.0
                acumulador_mensal["sala"] = 0.0
                acumulador_mensal["ultimo_mes_reset"] = hoje.month
                print(f"[{hora_atual}] Acumulador mensal zerado! Iniciando ciclo do dia 12.")

            # Converte a potência do momento (kW) para a energia gasta no minuto (kWh) dividindo por 60
            pot_abatedouro = dados["ccm1_potencia"] + dados["ccm2_potencia"]
            pot_sala = dados["qgbt1_potencia"] + dados["qgbt2_potencia"]
            
            acumulador_mensal["abatedouro"] += (pot_abatedouro / 60.0)
            acumulador_mensal["sala"] += (pot_sala / 60.0)

            # Salva o acumulador atualizado em um nó isolado na nuvem
            requests.put(f"{FIREBASE_URL}/acumulados_mes.json", json=acumulador_mensal)

            # 2.2 SALVA HISTÓRICO PADRÃO
            dados_temp_energia = {k: v for k, v in dados.items() if not k.startswith("agua_") and k != "gatilho_2_horas"}
            requests.patch(url_hist, json=dados_temp_energia)
                
            ultimo_salvamento_1min = agora

        # 3. Salva Histórico de Água (Acionado pelo CLP - Borda de Subida)
        if gatilho_atual and not estado_anterior_gatilho:
            dados_agua = {k: v for k, v in dados.items() if k.startswith("agua_")}
            requests.patch(url_hist, json=dados_agua)
            print(f"[{hora_atual}] Histórico de Água salvo via GATILHO.")
                
        estado_anterior_gatilho = gatilho_atual
        print(f"[{hoje.strftime('%H:%M:%S')}] Acumulado Mês: {(acumulador_mensal['abatedouro'] + acumulador_mensal['sala']):.1f} kWh")
        
        time.sleep(5)

except KeyboardInterrupt:
    print("\nDesconectando do CLP...")
    plc.disconnect()