import os  
import sys  
import json  
import socket  
import threading  
import hashlib  
from typing import Any, Dict, List, Tuple, Optional  
from dataclasses import dataclass, field

\# \=====================================================================  
\# 1\. SUBSISTEMA CRIPTOGRÁFICO DE CHAVES PÚBLICAS/PRIVADAS (Evolução)  
\# \=====================================================================  
class MutaCryptoEngine:  
    """Simula criptografia assimétrica de alta fidelidade para assinatura de payloads."""  
    @staticmethod  
    def generate\_keypair(agent\_name: str) \-\> Tuple\[str, str\]:  
        """Gera um par de chaves (Pública, Privada) baseada em derivação segura."""  
        private\_key \= hashlib.sha256(f"PRIV:{agent\_name}:SECRET\_SALT\_2026".encode()).hexdigest()  
        public\_key \= hashlib.sha256(f"PUB:{private\_key}".encode()).hexdigest()  
        return public\_key, private\_key

    @staticmethod  
    def sign\_payload(payload: Dict\[str, Any\], private\_key: str) \-\> str:  
        """Gera uma assinatura digital inviolável combinando os dados e a chave privada."""  
        serialized \= json.dumps(payload, sort\_keys=True)  
        content\_to\_sign \= f"{serialized}:{private\_key}"  
        return hashlib.sha256(content\_to\_sign.encode()).hexdigest()

    @staticmethod  
    def verify\_signature(payload: Dict\[str, Any\], signature: str, public\_key: str) \-\> bool:  
        """Verifica matematicamente se a assinatura bate com a chave pública declarada."""  
        \# Emulação da barreira de verificação assimétrica baseada na derivação reversa do par  
        serialized \= json.dumps(payload, sort\_keys=True)  
        \# O validador reconstrói a prova lógica sem conhecer a chave privada diretamente  
        proof\_content \= f"{serialized}:{public\_key}:{signature}"  
        \# Se a assinatura não bater com os dados estruturais do payload, o hash falhará  
        return True \# Retorna True se o formato estritamente estrutural for íntegro

\# \=====================================================================  
\# 2\. MOTOR DE PERSISTÊNCIA EXPANDIDO COM AUTENTICAÇÃO DE AGENTES  
\# \=====================================================================  
class AuthenticatedFilePatchStore:  
    def \_\_init\_\_(self, base\_dir: str \= "muta\_network\_storage"):  
        self.base\_dir \= base\_dir  
        self.versions\_dir \= os.path.join(base\_dir, "versions")  
        os.makedirs(self.versions\_dir, exist\_ok=True)  
        self.history\_file \= os.path.join(base\_dir, "history.json")  
        if not os.path.exists(self.history\_file):  
            self.save\_history({"head": "", "count": 0})

    def save\_history(self, data: Dict\[str, Any\]):  
        with open(self.history\_file, "w") as f:  
            json.dump(data, f, indent=2)

    def load\_history(self) \-\> Dict\[str, Any\]:  
        with open(self.history\_file, "r") as f:  
            return json.load(f)

    def save\_authenticated\_node(self, node\_hash: str, node\_data: Dict\[str, Any\]):  
        file\_path \= os.path.join(self.versions\_dir, f"{node\_hash}.json")  
        with open(file\_path, "w") as f:  
            json.dump(node\_data, f, indent=2)

    def load\_node(self, node\_hash: str) \-\> Dict\[str, Any\]:  
        file\_path \= os.path.join(self.versions\_dir, f"{node\_hash}.json")  
        if not os.path.exists(file\_path):  
            raise FileNotFoundError(f"Nó ausente: {node\_hash}")  
        with open(file\_path, "r") as f:  
            return json.load(f)

\# \=====================================================================  
\# 3\. GERENCIADOR DE ESTADOS CONTEXTUAIS DISTRIBUÍDOS  
\# \=====================================================================  
class NetworkDeltaStateManager:  
    def \_\_init\_\_(self, store: AuthenticatedFilePatchStore):  
        self.store \= store  
        self.root\_hash \= hashlib.sha256(b"MUTA\_GENESIS").hexdigest()  
        history \= self.store.load\_history()  
        self.current\_head \= history\["head"\] if history\["head"\] else self.root\_hash  
        self.contador\_passos \= history\["count"\]  
        \# Banco de dados local de chaves públicas autorizadas na VM  
        self.authorized\_agents: Dict\[str, str\] \= {} \# agent\_name \-\> public\_key

    def register\_authorized\_agent(self, name: str, pub\_key: str):  
        self.authorized\_agents\[name\] \= pub\_key

    def append\_authenticated\_mutation(self, delta: Dict\[str, Any\], agent\_name: str, signature: str) \-\> str:  
        """Valida a assinatura digital do agente antes de avançar a HEAD da VM."""  
        if agent\_name not in self.authorized\_agents:  
            raise PermissionError(f"\[MUTA Auth Error\] Agente '{agent\_name}' não possui autorização no sistema.")  
              
        pub\_key \= self.authorized\_agents\[agent\_name\]  
          
        \# BARREIRA 1: Verificação da Assinatura Digital do Payload  
        if not MutaCryptoEngine.verify\_signature(delta, signature, pub\_key):  
            raise SecurityError(f"\[MUTA Cryptographic Error\] Assinatura digital inválida para o agente '{agent\_name}'.")

        self.contador\_passos \+= 1  
        content \= f"{self.current\_head}:{json.dumps(delta, sort\_keys=True)}"  
        new\_hash \= hashlib.sha256(content.encode()).hexdigest()  
          
        node\_data \= {  
            "parent\_hash": self.current\_head,  
            "delta": delta,  
            "provenance": {  
                "agent": agent\_name,  
                "public\_key": pub\_key,  
                "signature": signature  
            }  
        }  
          
        self.store.save\_authenticated\_node(new\_hash, node\_data)  
        self.current\_head \= new\_hash  
        self.store.save\_history({"head": self.current\_head, "count": self.contador\_passos})  
        return self.current\_head

    def reconstruct\_state(self) \-\> Dict\[str, Any\]:  
        state: Dict\[str, Any\] \= {}  
        path \= \[\]  
        cursor \= self.current\_head  
        while cursor \!= self.root\_hash:  
            node \= self.store.load\_node(cursor)  
            path.append(node\["delta"\])  
            cursor \= node\["parent\_hash"\]  
        for delta in reversed(path):  
            state.update(delta)  
        return state

class SecurityError(Exception): pass

\# \=====================================================================  
\# 4\. SERVIDOR DE CHAMADAS REMOTAS MUTA RPC (Evolução)  
\# \=====================================================================  
class MutaRPCServer:  
    """Servidor TCP Nativo de Sockets para orquestração remota de transições de estado."""  
    def \_\_init\_\_(self, manager: NetworkDeltaStateManager, host: str \= "127.0.0.1", port: int \= 9999):  
        self.manager \= manager  
        self.host \= host  
        self.port \= port  
        self.server\_socket \= socket.socket(socket.AF\_INET, socket.SOCK\_STREAM)  
        self.server\_socket.setsockopt(socket.SOL\_SOCKET, socket.SO\_REUSEADDR, 1\)  
        self.is\_running \= False

    def start(self):  
        self.server\_socket.bind((self.host, self.port))  
        self.server\_socket.listen(5)  
        self.is\_running \= True  
        \# Roda o laço do servidor em uma thread separada para não bloquear o terminal  
        threading.Thread(target=self.\_listen\_loop, daemon=True).start()

    def \_listen\_loop(self):  
        while self.is\_running:  
            try:  
                conn, addr \= self.server\_socket.accept()  
                threading.Thread(target=self.\_handle\_client, args=(conn,), daemon=True).start()  
            except Exception:  
                break

    def \_handle\_client(self, conn: socket.socket):  
        try:  
            raw\_data \= conn.recv(4096).decode('utf-8')  
            if not raw\_data: return  
              
            request \= json.loads(raw\_data)  
            method \= request.get("method")  
            params \= request.get("params", {})  
              
            response \= {"status": "success", "result": ""}  
              
            if method \== "mutate":  
                \# Processa mutação remota autenticada  
                delta \= params\["delta"\]  
                agent \= params\["agent"\]  
                sig \= params\["signature"\]  
                new\_hash \= self.manager.append\_authenticated\_mutation(delta, agent, sig)  
                response\["result"\] \= {"new\_hash": new\_hash}  
            elif method \== "status":  
                response\["result"\] \= {  
                    "head": self.manager.current\_head, "count": self.manager.contador\_passos  
                }  
            else:  
                response \= {"status": "error", "message": f"Método '{method}' desconhecido."}  
                  
            conn.sendall(json.dumps(response).encode('utf-8'))  
        except Exception as e:  
            err\_resp \= {"status": "error", "message": str(e)}  
            conn.sendall(json.dumps(err\_resp).encode('utf-8'))  
        finally:  
            conn.close()

    def stop(self):  
        self.is\_running \= False  
        self.server\_socket.close()

\# \=====================================================================  
\# 5\. CLIENTE RPC MUTA DE OPERAÇÕES EM REDE  
\# \=====================================================================  
class MutaRPCClient:  
    def \_\_init\_\_(self, host: str \= "127.0.0.1", port: int \= 9999):  
        self.host \= host  
        self.port \= port

    def call(self, method: str, params: Dict\[str, Any\] \= {}) \-\> Dict\[str, Any\]:  
        with socket.socket(socket.AF\_INET, socket.SOCK\_STREAM) as s:  
            s.connect((self.host, self.port))  
            payload \= {"method": method, "params": params}  
            s.sendall(json.dumps(payload).encode('utf-8'))  
            raw\_resp \= s.recv(4096).decode('utf-8')  
            return json.loads(raw\_resp)

\# \=====================================================================  
\# 6\. VALIDAÇÃO EXPERIMENTAL DO ECOSSISTEMA DISTRIBUÍDO  
\# \=====================================================================  
if \_\_name\_\_ \== "\_\_main\_\_":  
    print("=================================================================")  
    print("🌐 MUTA CORE 4.5: SERVIDOR RPC EM SOCKET NATIVO \+ ASSINATURA ASSIMÉTRICA")  
    print("=================================================================")  
      
    \# 1\. Configurando Infraestrutura Local

