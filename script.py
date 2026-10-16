import snap7
from snap7.util import get_real, get_bool
import requests
from datetime import datetime
import time

IP_CLP = '20.1.1.1'
RACK = 0
SLOT = 1

# --- DECLARAÇÃO DAS DBs ---
DB_TEMP = 7         # Temperaturas
DB_AGUA = 21        # Hidrômetros (Gráfico 1 min e Tabela Gatilho)
DB_UTILIDADES = 29  # Pressões (Utilidades)
DB_ENERGIA = 34     # PACs (Quadros)
DB_DB23 = 23        # DB 23 (Contém Água Hiperclorada no offset 336 e Bit de Gatilho no offset 340)

FIREBASE_URL = 'https://planta-supervisorio-default-rtdb.firebaseio.com'

plc = snap7.client.Client()

def conectar_clp():
    """Tenta conectar ou reconectar ao CLP com segurança."""
    try:
        if plc.get_connected():
            plc.disconnect()
        plc.connect(IP_CLP, RACK, SLOT)
        if plc.get_connected():
            print("Conectado ao S7-1200 com sucesso!")
            return True
    except Exception as e:
        print(f"Erro ao conectar no CLP: {e}")
    return False

# Conexão inicial
conectar_clp()

# --- SISTEMA DO ACUMULADOR MENSAL ---
acumulador_mensal = {
    "abatedouro": 0.0,
    "sala": 0.0,
    "ultimo_mes_reset": 0
}

def requisicao_firebase(metodo, url, dados=None):
    """Função auxiliar para tratar quedas de internet sem quebrar o script."""
    try:
        if metodo == "get":
            return requests.get(url, timeout=10)
        elif metodo == "put":
            return requests.put(url, json=dados, timeout=10)
        elif metodo == "patch":
            return requests.patch(url, json=dados, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"[Aviso de Rede] Falha na comunicação com o Firebase: {e}")
    return None

# Sincronização inicial com o Firebase
try:
    print("Sincronizando acumulador mensal com o Firebase...")
    res_ac = requisicao_firebase("get", f"{FIREBASE_URL}/acumulados_mes.json")
    if res_ac and res_ac.status_code == 200 and res_ac.json():
        dados_nuvem = res_ac.json()
        acumulador_mensal["abatedouro"] = dados_nuvem.get("abatedouro", 0.0)
        acumulador_mensal["sala"] = dados_nuvem.get("sala", 0.0)
        acumulador_mensal["ultimo_mes_reset"] = dados_nuvem.get("ultimo_mes_reset", 0)
except Exception as e:
    print(f"Aviso: Iniciando acumulador do zero. Motivo: {e}")

def ler_dados_clp():
    dados_temp = plc.read_area(0x84, DB_TEMP, 0, 1048)
    dados_energia = plc.read_area(0x84, DB_ENERGIA, 0, 128)
    dados_agua = plc.read_area(0x84, DB_AGUA, 0, 772) 
    dados_utilidades = plc.read_area(0x84, DB_UTILIDADES, 0, 438)
    dados_db23 = plc.read_area(0x84, DB_DB23, 0, 344)
    
    return {
        # --- TEMPERATURAS ---
        "temp_cms":                 round(get_real(dados_temp, 604), 2),
        "temp_envaseCms":           round(get_real(dados_temp, 784), 2),
        "temp_salaCortes1":         round(get_real(dados_temp, 724), 2),
        "temp_salaCortes2":         round(get_real(dados_temp, 744), 2),
        "temp_abastiqf":            round(get_real(dados_temp, 644), 2),
        "temp_embprimariaiqf":      round(get_real(dados_temp, 624), 2),
        "temp_frangointeiro":       round(get_real(dados_temp, 704), 2),
        "temp_temperados":          round(get_real(dados_temp, 564), 2),
        "temp_chillers":            round(get_real(dados_temp, 764), 2),
        "temp_miudos":              round(get_real(dados_temp, 664), 2),
        "temp_padronizacao":        round(get_real(dados_temp, 804), 2),
        "temp_paletizacao":         round(get_real(dados_temp, 824), 2),
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
        "temp_glicol":               round(get_real(dados_temp, 1044), 2),
        
        # --- ENERGIA ---
        "ccm1_tensao":        round(get_real(dados_energia, 28), 2),
        "ccm1_potencia":      round(get_real(dados_energia, 20), 2),
        "ccm2_tensao":        round(get_real(dados_energia, 60), 2),
        "ccm2_potencia":      round(get_real(dados_energia, 52), 2),
        "qgbt1_tensao":       round(get_real(dados_energia, 92), 2),
        "qgbt1_potencia":     round(get_real(dados_energia, 84), 2),
        "qgbt2_tensao":       round(get_real(dados_energia, 124), 2),
        "qgbt2_potencia":     round(get_real(dados_energia, 116), 2),
        
        # --- ÁGUA (GATILHO A CADA 2 HORAS) ---
        "agua_pre_chiller":       round(get_real(dados_agua, 10), 2),
        "agua_chiller1":          round(get_real(dados_agua, 48), 2),
        "agua_chiller2":          round(get_real(dados_agua, 86), 2),
        "agua_condicionais":      round(get_real(dados_agua, 352), 2),
        "agua_coracao":           round(get_real(dados_agua, 276), 2),
        "agua_figado":            round(get_real(dados_agua, 314), 2),
        "agua_moela":             round(get_real(dados_agua, 238), 2),
        "agua_cabeca":            round(get_real(dados_agua, 200), 2),
        "agua_pe1":               round(get_real(dados_agua, 124), 2),
        "agua_pe2":               round(get_real(dados_agua, 162), 2),
        "agua_chuveiro_final":    round(get_real(dados_agua, 708), 2),
        "agua_tanque_escalda":    round(get_real(dados_agua, 746), 2),

        # --- ÁGUA (CONSUMO / GRÁFICO DE MINUTO EM MINUTO) ---
        "agua_cons_pre_chiller":      round(get_real(dados_agua, 6), 2),
        "agua_cons_chiller1":         round(get_real(dados_agua, 44), 2),
        "agua_cons_chiller2":         round(get_real(dados_agua, 82), 2),
        "agua_cons_pe1":              round(get_real(dados_agua, 120), 2),
        "agua_cons_pe2":              round(get_real(dados_agua, 158), 2),
        "agua_cons_cabeca":           round(get_real(dados_agua, 196), 2),
        "agua_cons_moela":            round(get_real(dados_agua, 234), 2),
        "agua_cons_coracao":          round(get_real(dados_agua, 310), 2),
        "agua_cons_figado":           round(get_real(dados_agua, 314), 2),
        "agua_cons_condicionais":     round(get_real(dados_agua, 348), 2),
        "agua_cons_chuveiro_final":   round(get_real(dados_agua, 704), 2),
        "agua_cons_tanque_escalda":   round(get_real(dados_agua, 742), 2),

        # --- ÁGUA (VALOR DOS HIDRÔMETROS REAIS NAS DIVS/CARDS) ---
        "agua_total_pre_chiller":     round(get_real(dados_agua, 32), 2),
        "agua_total_chiller1":        round(get_real(dados_agua, 70), 2),
        "agua_total_chiller2":        round(get_real(dados_agua, 108), 2),
        "agua_total_pe1":             round(get_real(dados_agua, 146), 2),
        "agua_total_pe2":             round(get_real(dados_agua, 184), 2),
        "agua_total_cabeca":          round(get_real(dados_agua, 222), 2),
        "agua_total_moela":           round(get_real(dados_agua, 260), 2),
        "agua_total_coracao":         round(get_real(dados_agua, 298), 2),
        "agua_total_figado":          round(get_real(dados_agua, 336), 2),
        "agua_total_condicionais":    round(get_real(dados_agua, 374), 2),
        "agua_total_chuveiro_final":  round(get_real(dados_agua, 730), 2),
        "agua_total_tanque_escalda":  round(get_real(dados_agua, 768), 2),

        # --- UTILIDADES (DB 29) ---
        "pressao_ar":                 round(get_real(dados_utilidades, 2), 2),
        "pressao_agua_quente":        round(get_real(dados_utilidades, 422), 2),
        "pressao_agua_potavel":       round(get_real(dados_utilidades, 426), 2),
        "pressao_agua_higienizacao":  round(get_real(dados_utilidades, 430), 2),
        "pressao_agua_pressurizada":  round(get_real(dados_utilidades, 434), 2),

        # --- ÁGUA HIPERCLORADA (DB 23) ---
        "agua_hiperclorada":          round(get_real(dados_db23, 336), 2),
        
        # --- GATILHO (DB 23) ---
        "gatilho_2_horas":            get_bool(dados_db23, 340, 0)
    }

ultimo_salvamento_1min = 0
estado_anterior_gatilho = False

try:
    while True:
        agora = time.time()
        hoje = datetime.now()
        hora_atual = hoje.strftime("%H:%M")
        
        # 1. Verifica/Garante a conexão com o CLP antes de tentar ler
        if not plc.get_connected():
            print(f"[{hoje.strftime('%H:%M:%S')}] Conexão com o CLP perdida. Tentando reconectar...")
            if not conectar_clp():
                time.sleep(5)
                continue # Pula o ciclo atual e tenta novamente no próximo loop
        
        # Tenta ler os dados do CLP com segurança
        try:
            dados = ler_dados_clp()
        except Exception as e:
            print(f"[{hoje.strftime('%H:%M:%S')}] Erro ao ler dados do CLP: {e}")
            try:
                plc.disconnect()
            except:
                pass
            time.sleep(5)
            continue

        gatilho_atual = dados["gatilho_2_horas"]
        
        # 2. Atualiza Tempo Real (A cada 5 segundos)
        requisicao_firebase("put", f"{FIREBASE_URL}/tempo_real.json", dados)
            
        data_atual = hoje.strftime("%Y-%m-%d")
        url_hist = f"{FIREBASE_URL}/historico/{data_atual}/{hora_atual}.json"

        # 3. Salva Histórico de Minuto (A cada 60 segundos)
        if agora - ultimo_salvamento_1min >= 60:
            if hoje.day >= 12 and acumulador_mensal.get("ultimo_mes_reset") != hoje.month:
                acumulador_mensal["abatedouro"] = 0.0
                acumulador_mensal["sala"] = 0.0
                acumulador_mensal["ultimo_mes_reset"] = hoje.month
                print(f"[{hora_atual}] Acumulador mensal zerado! Iniciando ciclo do dia 12.")

            pot_abatedouro = dados["ccm1_potencia"] + dados["ccm2_potencia"]
            pot_sala = dados["qgbt1_potencia"] + dados["qgbt2_potencia"]
            
            acumulador_mensal["abatedouro"] += (pot_abatedouro / 60.0)
            acumulador_mensal["sala"] += (pot_sala / 60.0)

            requisicao_firebase("put", f"{FIREBASE_URL}/acumulados_mes.json", acumulador_mensal)

            # --- SALVA O HISTÓRICO DE MINUTO ---
            chaves_excluidas_minuto = [
                "gatilho_2_horas",
                "agua_pre_chiller", "agua_chiller1", "agua_chiller2", 
                "agua_condicionais", "agua_coracao", "agua_figado", 
                "agua_moela", "agua_cabeca", "agua_pe1", "agua_pe2", 
                "agua_chuveiro_final", "agua_tanque_escalda"
            ]
            
            dados_historico_minuto = {k: v for k, v in dados.items() if k not in chaves_excluidas_minuto}
            
            requisicao_firebase("patch", url_hist, dados_historico_minuto)
            print(f"[{hora_atual}] Histórico de 1 min salvo com sucesso.")
                
            ultimo_salvamento_1min = agora

        # 4. Salva Histórico da Tabela de Água (Acionado pelo CLP - Borda de Subida do Gatilho a cada 2h)
        if gatilho_atual and not estado_anterior_gatilho:
            dados_agua_tabela = {
                "agua_pre_chiller": dados["agua_pre_chiller"],
                "agua_chiller1": dados["agua_chiller1"],
                "agua_chiller2": dados["agua_chiller2"],
                "agua_condicionais": dados["agua_condicionais"],
                "agua_coracao": dados["agua_coracao"],
                "agua_figado": dados["agua_figado"],
                "agua_moela": dados["agua_moela"],
                "agua_cabeca": dados["agua_cabeca"],
                "agua_pe1": dados["agua_pe1"],
                "agua_pe2": dados["agua_pe2"],
                "agua_chuveiro_final": dados["agua_chuveiro_final"],
                "agua_tanque_escalda": dados["agua_tanque_escalda"]
            }
            requisicao_firebase("patch", url_hist, dados_agua_tabela)
            print(f"[{hora_atual}] Histórico de Tabela de Água (Gatilho 2h) salvo com sucesso.")
                
        estado_anterior_gatilho = gatilho_atual
        print(f"[{hoje.strftime('%H:%M:%S')}] Acumulado Mês: {(acumulador_mensal['abatedouro'] + acumulador_mensal['sala']):.1f} kWh")
        
        time.sleep(5)

except KeyboardInterrupt:
    print("\nEncerrando script manualmente...")
    try:
        plc.disconnect()
    except:
        pass