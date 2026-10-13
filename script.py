import snap7
from snap7.util import get_real
import requests
from datetime import datetime
import time

IP_CLP = '20.1.3.1'
RACK = 0
SLOT = 1

# --- DECLARAÇÃO DAS DBs ---
DB_TEMP = 7       # Temperaturas
DB_AGUA = 21      # Hidrômetros
DB_ENERGIA = 34   # PACs (Quadros)

FIREBASE_URL = 'https://planta-supervisorio-default-rtdb.firebaseio.com/'

plc = snap7.client.Client()
plc.connect(IP_CLP, RACK, SLOT)

if plc.get_connected():
    print("Conectado ao S7-1200 - Lendo DBs 7, 21 e 34...")
else:
    exit()

def ler_dados_clp():
    dados_temp = plc.read_area(0x84, DB_TEMP, 0, 1048)
    dados_energia = plc.read_area(0x84, DB_ENERGIA, 0, 128)
    dados_agua = plc.read_area(0x84, DB_AGUA, 0, 678)
    
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
        "agua_pre_chiller":    round(get_real(dados_agua, 638), 2),
        "agua_chiller1":       round(get_real(dados_agua, 642), 2),
        "agua_chiller2":       round(get_real(dados_agua, 646), 2),
        "agua_condicionais":   round(get_real(dados_agua, 650), 2),
        "agua_coracao":        round(get_real(dados_agua, 654), 2),
        "agua_figado":         round(get_real(dados_agua, 658), 2),
        "agua_moela":          round(get_real(dados_agua, 662), 2),
        "agua_cabeca":         round(get_real(dados_agua, 666), 2),
        "agua_pe1":            round(get_real(dados_agua, 670), 2),
        "agua_pe2":            round(get_real(dados_agua, 674), 2)
    }

def enviar_firebase(dados_lidos, salvar_historico=False):
    hoje = datetime.now()
    requests.put(f"{FIREBASE_URL}/tempo_real.json", json=dados_lidos)
    
    if salvar_historico:
        data_atual = hoje.strftime("%Y-%m-%d")
        hora_atual = hoje.strftime("%H:%M")
        requests.put(f"{FIREBASE_URL}/historico/{data_atual}/{hora_atual}.json", json=dados_lidos)

contador_ciclos = 0

try:
    while True:
        dados = ler_dados_clp()
        salvar_hist = False
        
        if contador_ciclos >= 60: # Salva a cada 5 minutos
            salvar_hist = True
            contador_ciclos = 0
            
        enviar_firebase(dados, salvar_historico=salvar_hist)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Atualizado. Potência CCM1: {dados['ccm1_potencia']} kW | Água: {dados['agua_pre_chiller']} m³")
        
        contador_ciclos += 1
        time.sleep(5)

except KeyboardInterrupt:
    plc.disconnect()