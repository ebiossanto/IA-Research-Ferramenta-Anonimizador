import os  
import sys  
import json  
import hashlib  
from typing import Any, Dict, List, Tuple, Optional  
from dataclasses import dataclass, field

\# \=====================================================================  
\# 1\. MOTOR DE PERSISTÊNCIA SEGURO COM VALIDAÇÃO DE CHECKSUM  
\# \=====================================================================  
class VerifiedFilePatchStore:  
    """Gerencia a persistência em disco validando a integridade dos hashes em lote."""  
    def \_\_init\_\_(self, base\_dir: str \= "muta\_storage"):  
        self.base\_dir \= base\_dir  
        self.versions\_dir \= os.path.join(base\_dir, "versions")  
        os.makedirs(self.versions\_dir, exist\_ok=True)  
        self.history\_file \= os.path.join(base\_dir, "history.json")  
        if not os.path.exists(self.history\_file):  
            self.save\_history({"head": "", "count": 0})

    def load\_history(self) \-\> Dict\[str, Any\]:  
        with open(self.history\_file, "r") as f:  
            return json.load(f)

    def save\_history(self, data: Dict\[str, Any\]):  
        temp\_file \= self.history\_file \+ ".tmp"  
        with open(temp\_file, "w") as f:  
            json.dump(data, f, indent=2)  
        os.replace(temp\_file, self.history\_file)

    def save\_node(self, node\_hash: str, node\_data: Dict\[str, Any\]):  
        file\_path \= os.path.join(self.versions\_dir, f"{node\_hash}.json")  
        temp\_file \= file\_path \+ ".tmp"  
        with open(temp\_file, "w") as f:  
            json.dump(node\_data, f, indent=2)  
        os.replace(temp\_file, file\_path)

    def load\_node(self, node\_hash: str) \-\> Dict\[str, Any\]:  
        """Carrega o nó e valida o checksum criptográfico (Defesa Antiadulteração)."""  
        file\_path \= os.path.join(self.versions\_dir, f"{node\_hash}.json")  
        if not os.path.exists(file\_path):  
            raise FileNotFoundError(f"\[MUTA Crypto Error\] Checkpoint ausente: {node\_hash}")  
              
        with open(file\_path, "r") as f:  
            node\_data \= json.load(f)  
              
        \# Recalcula o hash com base nos dados lidos para checar integridade (Prioridade MUTA 4.4)  
        parent\_hash \= node\_data\["parent\_hash"\]  
        delta \= node\_data\["delta"\]  
        content \= f"{parent\_hash}:{json.dumps(delta, sort\_keys=True)}"  
        recalculated\_hash \= hashlib.sha256(content.encode()).hexdigest()  
          
        if recalculated\_hash \!= node\_hash:  
            raise SecurityError(  
                f"\\n\[ALERTA DE SEGURANÇA MUTA\] Quebra de integridade detectada\!\\n"  
                f"O arquivo '{node\_hash}.json' foi adulterado maliciosamente por um agente externo.\\n"  
                f"Hash esperado: {node\_hash}\\nHash calculado: {recalculated\_hash}"  
            )  
              
        return node\_data

    def audit\_entire\_chain(self) \-\> Tuple\[bool, str\]:  
        """Audita recursivamente toda a cadeia de blocos de estado a partir da HEAD."""  
        history \= self.load\_history()  
        cursor \= history\["head"\]  
        genesis\_root \= hashlib.sha256(b"MUTA\_GENESIS").hexdigest()  
          
        if not cursor:  
            return True, "Cadeia vazia (Gênese intocada)."  
              
        try:  
            while cursor \!= genesis\_root:  
                \# O próprio método load\_node disparará SecurityError caso ache inconsistência  
                node \= self.load\_node(cursor)  
                cursor \= node\["parent\_hash"\]  
            return True, "Toda a cadeia de persistência foi validada com sucesso. Integridade 100%."  
        except SecurityError as e:  
            return False, str(e)

\# \=====================================================================  
\# 2\. GERENCIADOR DE ESTADOS CONTEXTUAIS  
\# \=====================================================================  
class PersistentDeltaStateManager:  
    def \_\_init\_\_(self, store: VerifiedFilePatchStore, frequencia\_snapshot: int \= 3):  
        self.store \= store  
        self.frequencia\_snapshot \= frequencia\_snapshot  
        self.root\_hash \= hashlib.sha256(b"MUTA\_GENESIS").hexdigest()  
          
        history \= self.store.load\_history()  
        self.current\_head \= history\["head"\] if history\["head"\] else self.root\_hash  
        self.contador\_passos \= history\["count"\]

    def append\_mutation(self, delta: Dict\[str, Any\]) \-\> str:  
        if not delta:  
            return self.current\_head  
              
        self.contador\_passos \+= 1  
        snapshot\_a\_salvar \= None  
          
        if self.contador\_passos % self.frequencia\_snapshot \== 0:  
            snapshot\_a\_salvar \= self.reconstruct\_state\_at(self.current\_head)  
            snapshot\_a\_salvar.update(delta)  
              
        content \= f"{self.current\_head}:{json.dumps(delta, sort\_keys=True)}"  
        new\_hash \= hashlib.sha256(content.encode()).hexdigest()  
          
        node\_data \= {  
            "parent\_hash": self.current\_head,  
            "delta": delta,  
            "snapshot\_consolidado": snapshot\_a\_salvar  
        }  
          
        self.store.save\_node(new\_hash, node\_data)  
        self.current\_head \= new\_hash  
        self.store.save\_history({"head": self.current\_head, "count": self.contador\_passos})  
        return self.current\_head

    def reconstruct\_state\_at(self, target\_hash: str) \-\> Dict\[str, Any\]:  
        state: Dict\[str, Any\] \= {}  
        path\_de\_deltas \= \[\]  
        cursor \= target\_hash  
          
        while cursor \!= self.root\_hash:  
            node\_data \= self.store.load\_node(cursor)  
            if node\_data.get("snapshot\_consolidado") is not None:  
                state.update(node\_data\["snapshot\_consolidado"\])  
                break  
            path\_de\_deltas.append(node\_data\["delta"\])  
            cursor \= node\_data\["parent\_hash"\]  
              
        for delta in reversed(path\_de\_deltas):  
            state.update(delta)  
        return state

class SecurityError(Exception):  
    """Exceção para violações de assinaturas digitais ou hashes."""  
    pass

\# \=====================================================================  
\# 3\. INTERFACE DE TERMINAL SYS.ARGV (MUTA-CLI NATIVA)  
\# \=====================================================================  
class MutaNativeCLI:  
    def \_\_init\_\_(self, store: VerifiedFilePatchStore, manager: PersistentDeltaStateManager):  
        self.store \= store  
        self.manager \= manager

    def execute\_from\_args(self, args: List\[str\]):  
        if len(args) \< 2:  
            self.print\_help()  
            return

        cmd \= args\[1\].lower()

        if cmd \== "status":  
            print(f"\[MUTA STATUS\]")  
            print(f"  HEAD atual em disco : {self.manager.current\_head}")  
            print(f"  Total de passos     : {self.manager.contador\_passos}")  
              
        elif cmd \== "mutate":  
            if len(args) \< 3:  
                print("\[Erro MUTA CLI\] Uso: python muta\_vm.py mutate '\<json\_delta\>'")  
                return  
            try:  
                delta\_payload \= json.loads(args\[2\])  
                new\_hash \= self.manager.append\_mutation(delta\_payload)  
                print(f"\[MUTA SUCCESS\] Mutação persistida. Nova HEAD: {new\_hash}")  
            except Exception as e:  
                print(f"\[MUTA CLI Error\] Falha ao processar mutação: {e}")

        elif cmd \== "rollback":  
            if len(args) \< 3:  
                print("\[Erro MUTA CLI\] Uso: python muta\_vm.py rollback \<hash\>")  
                return  
            target\_hash \= args\[2\]  
            try:  
                estado \= self.manager.reconstruct\_state\_at(target\_hash)  
                self.manager.current\_head \= target\_hash  
                self.store.save\_history({"head": target\_hash, "count": self.manager.contador\_passos})  
                print(f"\[MUTA SUCCESS\] Viagem no tempo realizada.")  
                print(f"Estado restaurado: {estado}")  
            except Exception as e:  
                print(f"\[MUTA CLI Error\] Abortado: {e}")

        elif cmd \== "verify":  
            print("\[MUTA AUDITORIA\] Iniciando verificação de integridade da árvore em lote...")  
            sucesso, msg \= self.store.audit\_entire\_chain()  
            if sucesso:  
                print(f"\[MUTA OK\] {msg}")  
            else:  
                print(f"\[MUTA CRITICAL\] REJEITADO.\\n{msg}")

        else:  
            self.print\_help()

    def print\_help(self):  
        print("MUTA Language CLI \- Engine Core 4.4")  
        print("Uso: python muta\_vm.py \<comando\> \[argumentos\]")  
        print("\\nComandos:")  
        print("  status            \- Exibe metadados da HEAD atual.")  
        print("  mutate '\<json\>'   \- Commita mutação atômica em disco.")  
        print("  rollback \<hash\>   \- Rebobina o estado físico para o hash alvo.")  
        print("  verify            \- Valida os checksums criptográficos contra adulterações.")

\# \=====================================================================  
\# 4\. AMBIENTE AUTOMATIZADO DE VALIDAÇÃO DO EXPERIMENTO  
\# \=====================================================================  
if \_\_name\_\_ \== "\_\_main\_\_":  
    \# Caso o script seja chamado via terminal real (ex: python muta\_vm.py status)  
    if len(sys.argv) \> 1:  
        storage \= VerifiedFilePatchStore("muta\_live\_storage")  
        state\_mgr \= PersistentDeltaStateManager(storage)  
        native\_cli \= MutaNativeCLI(storage, state\_mgr)  
        native\_cli.execute\_from\_args(sys.argv)  
        sys.exit(0)

    \# \--- SIMULAÇÃO CONTROLADA PARA EMULAR O COMPORTAMENTO DE TERMINAL \---  
    print("=================================================================")  
    print("🛡️ EXECUÇÃO MUTA CORE 4.4: VALIDANDO SYS.ARGV \+ AUDITORIA DE ANTIADULTERAÇÃO")  
    print("=================================================================")  
      
    storage\_test \= VerifiedFilePatchStore("muta\_sandbox\_storage")  
    mgr\_test \= PersistentDeltaStateManager(storage\_test)  
    cli\_test \= MutaNativeCLI(storage\_test, mgr\_test)  
      
    \# 1\. Simula entrada de argumentos via terminal: 'python muta\_vm.py mutate'  
    print("\\n\[Passo 1\] Emulando comando via terminal: mutate")  
    args\_simulados\_1 \= \["muta\_vm.py", "mutate", '{"dispositivo": "turbina\_01", "rpm": 3200}'\]  
    cli\_test.execute\_from\_args(args\_simulados\_1)

