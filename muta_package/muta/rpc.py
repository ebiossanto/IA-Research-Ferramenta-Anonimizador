#!/usr/bin/env python3
"""MUTA RPC - Remote Procedure Call for state orchestration.

Provides TCP socket-based remote orchestration of state transitions.
Enables distributed agents to perform authenticated mutations remotely.

Classes:
    MutaRPCServer: TCP server accepting remote mutation commands
    MutaRPCClient: Client for remote mutation operations
"""

import socket
import threading
import json
from typing import Any, Dict, Optional

from .crypto import MutaCryptoEngine
from .engine import PersistentDeltaStateManager, SecurityError, VerifiedFilePatchStore, append_authenticated_mutation


class MutaRPCServer:
    """Native TCP socket server for remote MUTA state orchestration.

    Accepts remote commands to mutate state, check status, etc.
    All mutations require digital signature verification before advancing HEAD.
    """

    def __init__(self, manager: NetworkDeltaStateManager, host: str = "127.0.0.1", port: int = 9999):
        self.manager = manager
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.is_running: bool = False

    def start(self) -> None:
        """Start the RPC server, listening on configured host:port.

        Launches the accept loop in a daemon thread so it doesn't block the terminal.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.is_running = True

        # Run the accept loop in a separate thread
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def _listen_loop(self) -> None:
        """Accept client connections and handle each in a new thread."""
        while self.is_running:
            try:
                conn, addr = self.server_socket.accept()
                threading.Thread(target=self._handle_client, args=(conn,), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, conn: socket.socket) -> None:
        """Handle a single client connection.

        Receives a JSON request, dispatches to the appropriate method,
        and sends back a JSON response.
        """
        try:
            raw_data = conn.recv(4096).decode('utf-8')
            if not raw_data:
                return

            request = json.loads(raw_data)
            method = request.get("method")
            params = request.get("params", {})

            response = {"status": "success", "result": ""}

            if method == "mutate":
                # Process remote authenticated mutation
                delta = params["delta"]
                agent = params["agent"]
                sig = params["signature"]
                new_hash = self.manager.append_authenticated_mutation(delta, agent, sig)
                response["result"] = {"new_hash": new_hash}
            elif method == "status":
                response["result"] = {
                    "head": self.manager.current_head,
                    "count": self.manager.contador_passos
                }
            else:
                response = {"status": "error", "message": f"Method '{method}' unknown."}

            conn.sendall(json.dumps(response).encode('utf-8'))
        except Exception as e:
            err_resp = {"status": "error", "message": str(e)}
            conn.sendall(json.dumps(err_resp).encode('utf-8'))
        finally:
            conn.close()

    def stop(self) -> None:
        """Stop the RPC server."""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()


class MutaRPCClient:
    """Client for remote MUTA operations via TCP socket.

    Connects to a MutaRPCServer and sends method calls with parameters.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 9999):
        self.host = host
        self.port = port

    def call(self, method: str, params: dict[str, Any] = {}) -> dict[str, Any]:
        """Send a remote method call and return the response.

        Args:
            method: The RPC method name (e.g., "mutate", "status").
            params: Parameters dict specific to the method.

        Returns:
            The parsed JSON response from the server.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            payload = {"method": method, "params": params}
            s.sendall(json.dumps(payload).encode('utf-8'))
            raw_resp = s.recv(4096).decode('utf-8')
            return json.loads(raw_resp)